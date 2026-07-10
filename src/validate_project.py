"""Validate that the Seoul Bike project checklist artifacts exist."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from data_preprocessing import FEATURE_COLUMNS, PROJECT_ROOT


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
    "scripts/run_streamlit.ps1",
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
        "required_paths_checked": len(REQUIRED_PATHS),
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
