"""Model comparison page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app_utils import figure_path, format_feature_name, format_number, load_model_comparison, readable_parameters


st.title("Model comparison")
st.caption("Compare the four required regression models using the saved project evaluation results.")

comparison = load_model_comparison()
best_model = comparison.iloc[0]
second_model = comparison.iloc[1] if len(comparison) > 1 else comparison.iloc[0]
fastest_model = comparison.sort_values("fit_time_seconds").iloc[0]
rmse_gain = float(second_model["test_rmse"] - best_model["test_rmse"])
rmse_gain_pct = rmse_gain / float(second_model["test_rmse"]) * 100

with st.container(horizontal=True):
    st.metric("Best model", str(best_model["model"]), border=True)
    st.metric(
        "Lowest RMSE",
        format_number(float(best_model["test_rmse"]), 1),
        f"{rmse_gain_pct:.1f}% lower than second",
        border=True,
    )
    st.metric("Best R2", f"{float(best_model['test_r2']):.3f}", border=True)
    st.metric("Fastest fit", str(fastest_model["model"]), f"{float(fastest_model['fit_time_seconds']):.2f}s", border=True)

st.subheader("Ranking table")
ranking_columns = [
    "rank_by_rmse",
    "model",
    "model_family",
    "test_mae",
    "test_rmse",
    "test_r2",
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
        "test_r2": "Test R2",
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
        "Test R2": st.column_config.NumberColumn(format="%.3f"),
        "Training R2": st.column_config.NumberColumn(format="%.3f"),
        "Testing R2": st.column_config.NumberColumn(format="%.3f"),
        "Train-test R2 gap": st.column_config.NumberColumn(format="%.3f"),
        "Cross-validation RMSE": st.column_config.NumberColumn(format="%.1f"),
        "Fit time (s)": st.column_config.NumberColumn(format="%.2f"),
    },
)

st.subheader("Visual comparison")
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Saved RMSE chart")
        st.image(figure_path("08_model_rmse_comparison.png"), caption="Generated model RMSE comparison")

with right:
    with st.container(border=True):
        st.subheader("Error metrics by model")
        error_chart = comparison[["model", "test_mae", "test_rmse", "cross_validation_rmse"]].rename(
            columns={
                "model": "Model",
                "test_mae": "MAE",
                "test_rmse": "RMSE",
                "cross_validation_rmse": "Cross-validation RMSE",
            }
        )
        error_long = error_chart.melt("Model", var_name="Metric", value_name="Bike count error")
        st.bar_chart(
            error_long,
            x="Model",
            y="Bike count error",
            color="Metric",
            y_label="Bike count error",
            stack=False,
        )

with st.container(border=True):
    st.subheader("Fit quality and overfitting")
    fit_chart = comparison[["model", "training_r2", "testing_r2", "train_test_r2_gap"]].rename(
        columns={
            "model": "Model",
            "training_r2": "Training R2",
            "testing_r2": "Testing R2",
            "train_test_r2_gap": "Train-test R2 gap",
        }
    )
    fit_long = fit_chart.melt("Model", var_name="Measure", value_name="Score")
    st.bar_chart(fit_long, x="Model", y="Score", color="Measure", y_label="Score", stack=False)

st.subheader("How the measures should be read")
measure_col, interpretation_col = st.columns(2, gap="large")

with measure_col:
    with st.container(border=True):
        st.markdown(
            """
            **RMSE** gives larger penalties to big mistakes, so it is useful for avoiding supply shocks.

            **MAE** shows the average size of a prediction error in rented bikes.

            **R2** explains how much demand variation the model captures.
            """
        )

with interpretation_col:
    with st.container(border=True):
        st.markdown(
            """
            **Fit time** matters because the prototype should be practical to retrain and deploy.

            **Train-test gap** flags overfitting when training performance is much stronger than testing performance.

            **Cross-validation RMSE** checks whether performance is stable beyond one split.
            """
        )

st.subheader("Model-level summaries")
cards = st.columns(2, gap="large")
for index, (_, row) in enumerate(comparison.iterrows()):
    with cards[index % 2]:
        with st.container(border=True):
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
