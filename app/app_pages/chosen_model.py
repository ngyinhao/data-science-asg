"""Selected-model explanation page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app_utils import (
    format_number,
    load_feature_importance,
    load_metadata,
    load_model_comparison,
    load_test_predictions,
    selected_model_row,
)
from chart_utils import (
    actual_vs_predicted_chart,
    feature_importance_chart,
    hourly_error_chart,
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

with st.container(horizontal=True):
    st.metric("Test RMSE", format_number(float(selected["test_rmse"]), 1), border=True)
    st.metric("Test MAE", format_number(float(selected["test_mae"]), 1), border=True)
    st.metric("Test R2", f"{float(selected['test_r2']):.3f}", border=True)
    st.metric("RMSE advantage", format_number(rmse_gap, 1), "vs next-best model", border=True)

st.subheader("Why it is suitable")
reason_col, evidence_col = st.columns(2, gap="large")

with reason_col:
    with st.container(border=True):
        st.markdown(
            f"""
            Random Forest is used for prediction because it gives the strongest error performance among the required models.
            It captures non-linear demand patterns across weather, calendar, and operating-status inputs better than the linear baseline.

            Its test R2 of **{float(selected['test_r2']):.3f}** shows that it explains most of the demand variation in the held-out test data.
            """
        )

with evidence_col:
    with st.container(border=True):
        st.markdown(
            f"""
            The model is also practical for the website. The saved comparison marks its Streamlit deployment suitability as:

            **{selected['streamlit_deployment_suitability']}**

            The main caution is a train-test R2 gap of **{float(selected['train_test_r2_gap']):.3f}**, so evaluation charts should be reviewed alongside the score.
            """
        )

st.subheader("Visual evidence")

with st.container(border=True):
    st.subheader("Actual vs predicted demand")
    st.caption("Each point is a held-out test observation. Drag to brush a region, scroll to zoom, and hover for scenario details; the dashed line is perfect agreement.")
    st.altair_chart(actual_vs_predicted_chart(predictions), width="stretch")

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Residual distribution")
        st.caption("The histogram shows whether prediction errors are centered near zero and how heavy the tails are.")
        st.altair_chart(residual_histogram(predictions), width="stretch")

with right:
    with st.container(border=True):
        st.subheader("Hourly error profile")
        st.caption("Mean absolute error across the 24-hour operating cycle; hover over points for exact values.")
        st.altair_chart(hourly_error_chart(predictions), width="stretch")

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Seasonal error spread")
        st.caption("Box-and-whisker ranges compare typical and extreme absolute errors. The white point marks the mean.")
        st.altair_chart(seasonal_error_box_chart(predictions), width="stretch")

with right:
    with st.container(border=True):
        st.subheader("Feature importance")
        feature_count = st.slider("Features to display", 5, min(20, len(importance)), 12)
        st.caption("Lollipop ranking of the model's strongest global feature drivers; hover for exact importance.")
        st.altair_chart(feature_importance_chart(importance, feature_count), width="stretch")

st.subheader("Top feature drivers")
top_features = importance.head(10).rename(columns={"feature_label": "Feature", "importance": "Importance"})
st.dataframe(
    top_features[["Feature", "Importance"]],
    hide_index=True,
    column_config={"Importance": st.column_config.NumberColumn(format="%.3f")},
)

st.info(
    "The prediction page therefore uses Random Forest Regressor because it gives the best test error result while remaining practical for an interactive Streamlit prototype.",
    icon=":material/info:",
)
