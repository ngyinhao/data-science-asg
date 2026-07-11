"""Validate that the Seoul Bike project checklist artifacts exist."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
import sys

import joblib
import pandas as pd

from data_preprocessing import FEATURE_COLUMNS, PROJECT_ROOT


if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.app_utils import (
    PREPARED_DATA_COLUMNS,
    filter_insights_data,
    filtered_data_csv,
    prepare_insights_data,
)
from app.eda_chart_utils import (
    VARIABLE_OPTIONS,
    build_variable_chart,
    correlation_heatmap,
    default_functioning_scope,
    hour_season_heatmap,
    hour_season_scale_max,
)


REQUIRED_PATHS = [
    "data/raw/SeoulBikeData.csv",
    "data/processed/seoul_bike_prepared.csv",
    "notebooks/01_data_understanding.ipynb",
    "notebooks/02_data_preparation.ipynb",
    "notebooks/03_modelling_evaluation.ipynb",
    "src/data_preprocessing.py",
    "src/train_models.py",
    "src/create_project_artifacts.py",
    "app/streamlit_app.py",
    "app/app_pages/project_insights.py",
    "app/eda_chart_utils.py",
    "models/multiple_linear_regression.pkl",
    "models/decision_tree_regressor.pkl",
    "models/random_forest_regressor.pkl",
    "models/gradient_boosting_regressor.pkl",
    "models/best_model.pkl",
    "models/model_comparison.csv",
    "models/model_metadata.json",
    "models/test_predictions_best_model.csv",
    "models/feature_importance_best_model.csv",
    "figures/01_demand_by_hour.png",
    "figures/02_demand_by_season.png",
    "figures/03_demand_by_holiday.png",
    "figures/04_demand_by_functioning_day.png",
    "figures/05_temperature_vs_rented_bike_count.png",
    "figures/06_rainfall_vs_rented_bike_count.png",
    "figures/07_correlation_heatmap.png",
    "figures/08_model_rmse_comparison.png",
    "figures/09_actual_vs_predicted.png",
    "figures/10_residual_distribution.png",
    "figures/11_error_by_hour.png",
    "figures/12_error_by_season.png",
    "figures/13_feature_importance.png",
    "figures/14_prototype_preview.png",
    "report/project_report_draft.md",
    "report/eda_observations.md",
    "report/prototype_screenshot.png",
    "planning/interactive-chart-map.md",
    "scripts/run_streamlit.ps1",
]

REQUIRED_INSIGHT_COLUMNS = [
    "date",
    "rented_bike_count",
    "hour",
    "temperature_c",
    "humidity_pct",
    "wind_speed_m_per_s",
    "visibility_10m",
    "dew_point_temperature_c",
    "solar_radiation_mj_per_m2",
    "rainfall_mm",
    "snowfall_cm",
    "seasons",
    "holiday",
    "functioning_day",
]

CONTINUOUS_INSIGHT_COLUMNS = [
    "temperature_c",
    "humidity_pct",
    "wind_speed_m_per_s",
    "visibility_10m",
    "dew_point_temperature_c",
    "solar_radiation_mj_per_m2",
]

REQUIRED_COMPARISON_COLUMNS = [
    "test_mae",
    "test_rmse",
    "test_r2",
    "adjusted_r2",
    "training_r2",
    "testing_r2",
    "train_test_r2_gap",
    "cross_validation_rmse",
    "residual_mean",
    "residual_std",
    "worst_hour_mae",
    "worst_season_mae",
    "worst_holiday_group_mae",
    "worst_functioning_day_group_mae",
    "top_feature",
    "interpretability",
    "training_tuning_complexity",
    "streamlit_deployment_suitability",
]


def validate() -> dict[str, object]:
    missing_paths = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]
    if missing_paths:
        raise AssertionError(f"Missing required paths: {missing_paths}")

    prepared = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "seoul_bike_prepared.csv")
    comparison = pd.read_csv(PROJECT_ROOT / "models" / "model_comparison.csv")
    metadata = json.loads((PROJECT_ROOT / "models" / "model_metadata.json").read_text(encoding="utf-8"))
    report = (PROJECT_ROOT / "report" / "project_report_draft.md").read_text(encoding="utf-8")

    missing_columns = [column for column in REQUIRED_COMPARISON_COLUMNS if column not in comparison.columns]
    if missing_columns:
        raise AssertionError(f"Missing comparison columns: {missing_columns}")

    if prepared.shape[0] != 8760:
        raise AssertionError(f"Prepared row count should be 8760, found {prepared.shape[0]}")
    missing_insight_columns = [
        column for column in REQUIRED_INSIGHT_COLUMNS if column not in prepared.columns
    ]
    if missing_insight_columns:
        raise AssertionError(f"Prepared data is missing insight columns: {missing_insight_columns}")
    if set(prepared["seasons"].unique()) != {"Spring", "Summer", "Autumn", "Winter"}:
        raise AssertionError("Prepared seasons must contain the four expected categories.")
    if set(prepared["holiday"].unique()) != {"No Holiday", "Holiday"}:
        raise AssertionError("Prepared holiday values are not the two expected categories.")
    if set(prepared["functioning_day"].unique()) != {"Yes", "No"}:
        raise AssertionError("Prepared functioning-day values are not the two expected categories.")

    rainfall_band_counts = [
        int((prepared["rainfall_mm"] == 0).sum()),
        int(((prepared["rainfall_mm"] > 0) & (prepared["rainfall_mm"] <= 1)).sum()),
        int(((prepared["rainfall_mm"] > 1) & (prepared["rainfall_mm"] <= 5)).sum()),
        int((prepared["rainfall_mm"] > 5).sum()),
    ]
    if rainfall_band_counts != [8232, 280, 182, 66]:
        raise AssertionError(f"Unexpected rainfall-band counts: {rainfall_band_counts}")

    snowfall_band_counts = [
        int((prepared["snowfall_cm"] == 0).sum()),
        int(((prepared["snowfall_cm"] > 0) & (prepared["snowfall_cm"] <= 1)).sum()),
        int((prepared["snowfall_cm"] > 1).sum()),
    ]
    if snowfall_band_counts != [8317, 255, 188]:
        raise AssertionError(f"Unexpected snowfall-band counts: {snowfall_band_counts}")

    non_functioning = prepared.loc[prepared["functioning_day"] == "No", "rented_bike_count"]
    if len(non_functioning) != 295 or not non_functioning.eq(0).all():
        raise AssertionError("All 295 non-functioning records must retain zero observed demand.")

    minimum_continuous_bin_counts = {}
    for column in CONTINUOUS_INSIGHT_COLUMNS:
        _, edges = pd.qcut(prepared[column], q=10, retbins=True, duplicates="drop")
        counts = pd.cut(prepared[column], bins=edges, include_lowest=True).value_counts()
        minimum_continuous_bin_counts[column] = int(counts.min())
    if min(minimum_continuous_bin_counts.values()) < 30:
        raise AssertionError(
            f"A full-data continuous insight bin is too sparse: {minimum_continuous_bin_counts}"
        )

    insights_data = prepare_insights_data(prepared)
    insight_chart_dataset_counts = {}
    for variable in VARIABLE_OPTIONS:
        filtered = filter_insights_data(
            insights_data,
            ["Spring", "Summer", "Autumn", "Winter"],
            default_functioning_scope(variable),
        )
        chart_spec = build_variable_chart(filtered, variable).to_dict()
        dataset_counts = [len(rows) for rows in chart_spec.get("datasets", {}).values()]
        if not dataset_counts or any(count == 0 for count in dataset_counts):
            raise AssertionError(
                f"Insight chart {variable!r} has an empty rendered layer: {dataset_counts}"
            )
        insight_chart_dataset_counts[variable] = dataset_counts

    all_days = filter_insights_data(
        insights_data,
        ["Spring", "Summer", "Autumn", "Winter"],
        "All days",
    )
    functioning_days = filter_insights_data(
        insights_data,
        ["Spring", "Summer", "Autumn", "Winter"],
        "Functioning days",
    )
    not_functioning = filter_insights_data(
        insights_data,
        ["Spring", "Summer", "Autumn", "Winter"],
        "Not functioning",
    )
    if [len(all_days), len(functioning_days), len(not_functioning)] != [8760, 8465, 295]:
        raise AssertionError("The insights functioning-day filters returned unexpected row counts.")

    export = pd.read_csv(BytesIO(filtered_data_csv(functioning_days)))
    if list(export.columns) != PREPARED_DATA_COLUMNS or len(export) != len(functioning_days):
        raise AssertionError("Filtered CSV must contain only source columns and active rows.")

    hour_season_heatmap(all_days, hour_season_scale_max(insights_data)).to_dict()
    correlation_heatmap(all_days).to_dict()
    if comparison["model"].nunique() != 4:
        raise AssertionError("The comparison table must contain four distinct models.")
    if comparison.shape[1] < 15:
        raise AssertionError("The comparison table must contain at least 15 comparison points.")
    if len(metadata.get("models_trained", [])) != 4:
        raise AssertionError("Metadata must list four trained models.")
    if report.count("https://") < 5:
        raise AssertionError("Report draft must include at least five reference links.")

    model = joblib.load(PROJECT_ROOT / "models" / "best_model.pkl")
    sample = {
        "hour": 18,
        "temperature_c": 24.0,
        "humidity_pct": 55,
        "wind_speed_m_per_s": 1.5,
        "visibility_10m": 1500,
        "dew_point_temperature_c": 14.0,
        "solar_radiation_mj_per_m2": 0.6,
        "rainfall_mm": 0.0,
        "snowfall_cm": 0.0,
        "month": 7,
        "day": 15,
        "weekday": 4,
        "is_weekend": 0,
        "seasons": "Summer",
        "holiday": "No Holiday",
        "functioning_day": "Yes",
    }
    prediction = float(model.predict(pd.DataFrame([sample], columns=FEATURE_COLUMNS))[0])
    if prediction < 0:
        raise AssertionError("Prototype sample prediction should not be negative.")

    return {
        "status": "passed",
        "prepared_shape": list(prepared.shape),
        "models_compared": comparison["model"].tolist(),
        "comparison_point_count": int(comparison.shape[1]),
        "selected_model": metadata["selected_model"],
        "sample_prediction": round(prediction, 2),
        "rainfall_band_counts": rainfall_band_counts,
        "snowfall_band_counts": snowfall_band_counts,
        "minimum_continuous_bin_counts": minimum_continuous_bin_counts,
        "insight_chart_dataset_counts": insight_chart_dataset_counts,
        "insight_filter_row_counts": {
            "all_days": len(all_days),
            "functioning_days": len(functioning_days),
            "not_functioning": len(not_functioning),
        },
        "required_paths_checked": len(REQUIRED_PATHS),
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
