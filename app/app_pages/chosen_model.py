"""Selected-model explanation page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app_utils import (
    figure_path,
    format_number,
    load_feature_importance,
    load_metadata,
    load_model_comparison,
    selected_model_row,
)


st.title("Why this model was chosen")
st.caption("Evidence for the model used by the prediction page.")

metadata = load_metadata()
comparison = load_model_comparison()
importance = load_feature_importance()
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
    st.subheader("Actual vs predicted")
    st.image(figure_path("09_actual_vs_predicted.png"), caption="How closely predictions follow actual rented-bike counts")

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Residual distribution")
        st.image(figure_path("10_residual_distribution.png"), caption="Prediction errors centered around the actual values")

with right:
    with st.container(border=True):
        st.subheader("Error by hour")
        st.image(figure_path("11_error_by_hour.png"), caption="Hourly error pattern for operational planning")

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Error by season")
        st.image(figure_path("12_error_by_season.png"), caption="Seasonal error pattern")

with right:
    with st.container(border=True):
        st.subheader("Feature importance")
        st.image(figure_path("13_feature_importance.png"), caption="Most influential inputs in the selected model")

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
