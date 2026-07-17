"""Selected-model explanation page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.app_utils import (
    format_number,
    load_feature_importance,
    load_metadata,
    load_model_comparison,
    load_test_predictions,
    render_metric_grid,
    selected_model_row,
)
from app.chart_utils import (
    actual_vs_predicted_chart,
    feature_importance_chart,
    hourly_error_chart,
    ocr_chart,
    residual_histogram,
    seasonal_error_box_chart,
)


st.title("Why this model was chosen")
st.caption("Evidence for the model used by the prediction page.")

metadata = load_metadata()
comparison = load_model_comparison()
importance = load_feature_importance()
predictions = load_test_predictions()
selected_name = str(metadata["selected_model"])
selected = selected_model_row(comparison, selected_name)
runner_up = comparison.loc[comparison["model"] != selected_name].iloc[0]
rmse_gap = float(runner_up["test_rmse"] - selected["test_rmse"])

st.badge(selected_name, icon=":material/verified:", color="green")
st.markdown(f"**Selection reason:** {metadata['selected_model_reason']}")

render_metric_grid(
    [
        {"label": "Test RMSE", "value": format_number(float(selected["test_rmse"]), 1)},
        {"label": "Test MAE", "value": format_number(float(selected["test_mae"]), 1)},
        {"label": "Test R2", "value": f"{float(selected['test_r2']):.3f}"},
        {
            "label": "RMSE advantage",
            "value": format_number(rmse_gap, 1),
            "delta": "vs next-best model",
        },
    ]
)

st.subheader("Why it is suitable")
reason_col, evidence_col = st.columns(2, gap="medium")

with reason_col:
    with st.container(border=True, height="stretch"):
        st.markdown(
            f"""
            Random Forest is used for prediction because it gives the strongest error performance among the required models.
            It captures non-linear demand patterns across weather, calendar, and operating-status inputs better than the linear baseline.

            Its test R2 of **{float(selected['test_r2']):.3f}** shows that it explains most of the demand variation in the held-out test data.
            """
        )

with evidence_col:
    with st.container(border=True, height="stretch"):
        st.markdown(
            f"""
            The model is also practical for the website. The saved comparison marks its Streamlit deployment suitability as:

            **{selected['streamlit_deployment_suitability']}**

            The main caution is a train-test R2 gap of **{float(selected['train_test_r2_gap']):.3f}**, so evaluation charts should be reviewed alongside the score.
            """
        )

st.subheader("Visual evidence")

agreement_col, residual_col = st.columns(2, gap="medium")
with agreement_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Prediction agreement")
        st.caption("Held-out observations; the dashed line is perfect agreement.")
        st.altair_chart(ocr_chart(actual_vs_predicted_chart(predictions)), width="stretch")

with residual_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Residual distribution")
        st.caption("Check whether errors centre near zero and whether tails are heavy.")
        st.altair_chart(ocr_chart(residual_histogram(predictions)), width="stretch")

hourly_col, seasonal_col = st.columns(2, gap="medium")
with hourly_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Hourly error profile")
        st.caption("Mean absolute error across the 24-hour operating cycle.")
        st.altair_chart(ocr_chart(hourly_error_chart(predictions)), width="stretch")

with seasonal_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Seasonal error spread")
        st.caption("Boxes show the middle 50%; whiskers use the 1.5×IQR rule.")
        st.altair_chart(ocr_chart(seasonal_error_box_chart(predictions)), width="stretch")

with st.container(border=True):
    st.subheader("Feature importance")
    feature_count = st.slider("Features to display", 5, min(20, len(importance)), 12)
    st.caption("Lollipop ranking of the model's strongest global feature drivers; hover for exact importance.")
    st.altair_chart(
        ocr_chart(feature_importance_chart(importance, feature_count)),
        width="stretch",
    )
    with st.expander("How to read feature importance", icon=":material/info:"):
        st.markdown(
            """
            - The values show each feature's share of the Random Forest's total reduction in prediction error across its tree splits. Together, they sum to 1.
            - A larger value means the model relied more heavily on that feature across the fitted trees. It does not show whether the feature raises or lowers demand.
            - Importance is not a causal effect. Correlated inputs, such as temperature and dew point, can divide or inflate one another's importance.
            - Category levels are one-hot encoded, so entries such as **functioning day: yes** and **season: autumn** appear as separate drivers.
            """
        )

st.info(
    "The prediction page therefore uses Random Forest Regressor because it gives the best test error result while remaining practical for an interactive Streamlit prototype.",
    icon=":material/info:",
)
