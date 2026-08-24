"""Model comparison page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.app_utils import (
    format_feature_name,
    format_number,
    load_model_comparison,
    readable_parameters,
    render_metric_grid,
)
from app.chart_utils import (
    error_metrics_chart,
    fit_quality_dumbbell_chart,
    ocr_chart,
    rmse_ranking_chart,
    weak_spot_heatmap,
)


st.title("Model comparison")
st.caption("Compare the four required regression models using the saved project evaluation results.")

comparison = load_model_comparison()
best_model = comparison.iloc[0]
second_model = comparison.iloc[1] if len(comparison) > 1 else comparison.iloc[0]
fastest_model = comparison.sort_values("fit_time_seconds").iloc[0]
rmse_gain = float(second_model["test_rmse"] - best_model["test_rmse"])
rmse_gain_pct = rmse_gain / float(second_model["test_rmse"]) * 100

render_metric_grid(
    [
        {
            "label": "Best model",
            "value": "RF model",
            "help": f"Full model name: {best_model['model']}.",
        },
        {
            "label": "Lowest RMSE",
            "value": format_number(float(best_model["test_rmse"]), 1),
            "delta": f"{rmse_gain_pct:.1f}% lower than second",
        },
        {"label": "Best R2", "value": f"{float(best_model['test_r2']):.3f}"},
        {
            "label": "Fastest fit",
            "value": "Linear",
            "delta": f"{float(fastest_model['fit_time_seconds']):.2f}s",
            "help": f"Full model name: {fastest_model['model']}.",
        },
    ]
)

st.subheader("Ranking table")
ranking_columns = [
    "rank_by_rmse",
    "model",
    "model_family",
    "test_mae",
    "test_rmse",
    "training_r2",
    "testing_r2",
    "train_test_r2_gap",
    "cross_validation_rmse",
    "fit_time_seconds",
]
ranking = comparison[ranking_columns].rename(
    columns={
        "rank_by_rmse": "Rank",
        "model": "Model",
        "model_family": "Model family",
        "test_mae": "MAE",
        "test_rmse": "RMSE",
        "training_r2": "Training R2",
        "testing_r2": "Testing R2",
        "train_test_r2_gap": "Train-test R2 gap",
        "cross_validation_rmse": "Cross-validation RMSE",
        "fit_time_seconds": "Fit time (s)",
    }
)

st.dataframe(
    ranking,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn(format="%d"),
        "MAE": st.column_config.NumberColumn(format="%.1f"),
        "RMSE": st.column_config.NumberColumn(format="%.1f"),
        "Training R2": st.column_config.NumberColumn(format="%.3f"),
        "Testing R2": st.column_config.NumberColumn(format="%.3f"),
        "Train-test R2 gap": st.column_config.NumberColumn(format="%.3f"),
        "Cross-validation RMSE": st.column_config.NumberColumn(format="%.1f"),
        "Fit time (s)": st.column_config.NumberColumn(format="%.2f"),
    },
)

st.subheader("Visual comparison")
ranking_col, errors_col = st.columns(2, gap="medium")
with ranking_col:
    with st.container(border=True, height="stretch"):
        st.subheader("RMSE ranking")
        st.caption("Lower is better. The orange point marks the selected model.")
        st.altair_chart(ocr_chart(rmse_ranking_chart(comparison)), width="stretch")

with errors_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Error metrics by model")
        st.caption("Compare average, large-error, and cross-validation error.")
        st.altair_chart(ocr_chart(error_metrics_chart(comparison)), width="stretch")

fit_col, weak_spot_col = st.columns(2, gap="medium")
with fit_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Fit and overfitting")
        st.caption("Longer testing-to-training connectors indicate a larger generalisation gap.")
        st.altair_chart(ocr_chart(fit_quality_dumbbell_chart(comparison)), width="stretch")

with weak_spot_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Operational weak spots")
        st.caption("Darker cells indicate larger worst-segment mean absolute error.")
        st.altair_chart(ocr_chart(weak_spot_heatmap(comparison)), width="stretch")

st.subheader("How the measures should be read")
measure_col, interpretation_col = st.columns(2, gap="large")

with measure_col:
    with st.container(border=True, height="stretch"):
        st.markdown(
            """
            **RMSE** gives larger penalties to big mistakes, so it is useful for avoiding supply shocks.

            **MAE** shows the average size of a prediction error in rented bikes.

            **R2** explains how much demand variation the model captures.
            """
        )

with interpretation_col:
    with st.container(border=True, height="stretch"):
        st.markdown(
            """
            **Fit time** matters because the prototype should be practical to retrain and deploy.

            **Train-test gap** flags overfitting when training performance is much stronger than testing performance.

            **Cross-validation RMSE** checks whether performance is stable beyond one split.
            """
        )

st.subheader("Model-level summaries")
model_rows = list(comparison.iterrows())
for row_start in range(0, len(model_rows), 2):
    cards = st.columns(2, gap="large")
    for column_index, (_, row) in enumerate(model_rows[row_start : row_start + 2]):
        with cards[column_index]:
            with st.container(border=True, height="stretch"):
                st.markdown(f"**{int(row['rank_by_rmse'])}. {row['model']}**")
                st.caption(str(row["model_family"]))
                metric_left, metric_right = st.columns(2)
                metric_left.metric("RMSE", format_number(float(row["test_rmse"]), 1))
                metric_right.metric("R2", f"{float(row['test_r2']):.3f}")
                st.markdown(f"Top feature: **{format_feature_name(str(row['top_feature']))}**")
                st.markdown(f"Interpretability: {row['interpretability']}")
                st.markdown(f"Streamlit suitability: {row['streamlit_deployment_suitability']}")
                with st.expander("Tuning and weak spots", icon=":material/tune:"):
                    st.write(f"Tuning complexity: {row['training_tuning_complexity']}")
                    st.write(f"Worst hour: {int(row['worst_hour'])} with MAE {float(row['worst_hour_mae']):,.1f}")
                    st.write(f"Worst season: {row['worst_season']} with MAE {float(row['worst_season_mae']):,.1f}")
                    st.write(f"Best parameters: {readable_parameters(row['best_parameters'])}")

st.success(
    f"{best_model['model']} ranks first because it has the lowest test RMSE while keeping strong test R2 performance.",
    icon=":material/check_circle:",
)
