"""Train and evaluate the four required Seoul Bike demand models."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / "tmp" / "matplotlib"))

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from data_preprocessing import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    PROJECT_ROOT,
    TARGET_COLUMN,
    make_preprocessor,
    prepare_dataset,
    save_prepared_dataset,
    split_features_target,
)


RANDOM_STATE = 42
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "report" / "tables"


@dataclass(frozen=True)
class ModelSpec:
    name: str
    filename: str
    estimator: object
    param_grid: dict[str, list[object]] | None
    family: str
    interpretability: str
    tuning_complexity: str
    streamlit_suitability: str


MODEL_SPECS = [
    ModelSpec(
        name="Multiple Linear Regression",
        filename="multiple_linear_regression.pkl",
        estimator=LinearRegression(),
        param_grid=None,
        family="Linear baseline",
        interpretability="High: coefficients show direction and relative strength after preprocessing.",
        tuning_complexity="Low: no major hyperparameters were tuned.",
        streamlit_suitability="High: fast prediction and easy explanation.",
    ),
    ModelSpec(
        name="Decision Tree Regressor",
        filename="decision_tree_regressor.pkl",
        estimator=DecisionTreeRegressor(random_state=RANDOM_STATE),
        param_grid={
            "model__max_depth": [5, 8, 12, None],
            "model__min_samples_leaf": [5, 20, 50],
        },
        family="Single tree",
        interpretability="Medium-high: tree rules and feature importance are explainable.",
        tuning_complexity="Medium: depth and leaf-size choices strongly affect overfitting.",
        streamlit_suitability="High: fast prediction, but can be less stable than ensemble models.",
    ),
    ModelSpec(
        name="Random Forest Regressor",
        filename="random_forest_regressor.pkl",
        estimator=RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
        param_grid={
            "model__n_estimators": [120],
            "model__max_depth": [12, None],
            "model__min_samples_leaf": [2, 5],
        },
        family="Bagging ensemble",
        interpretability="Medium: feature importance helps, but individual predictions are less transparent.",
        tuning_complexity="Medium-high: several parameters affect speed and generalisation.",
        streamlit_suitability="High: reliable and still quick enough for single-user prototype prediction.",
    ),
    ModelSpec(
        name="Gradient Boosting Regressor",
        filename="gradient_boosting_regressor.pkl",
        estimator=GradientBoostingRegressor(random_state=RANDOM_STATE),
        param_grid={
            "model__n_estimators": [150, 250],
            "model__learning_rate": [0.05, 0.1],
            "model__max_depth": [2, 3],
        },
        family="Boosting ensemble",
        interpretability="Medium: feature importance helps, but boosted interactions are harder to explain.",
        tuning_complexity="High: learning rate, depth, and number of trees must be balanced.",
        streamlit_suitability="High: compact model with strong tabular prediction performance.",
    ),
]


def adjusted_r2(r2: float, n_rows: int, n_features: int) -> float:
    if n_rows <= n_features + 1:
        return float("nan")
    return 1 - (1 - r2) * (n_rows - 1) / (n_rows - n_features - 1)


def rmse(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def make_model_pipeline(estimator: object) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor()),
            ("model", estimator),
        ]
    )


def tune_or_fit_model(spec: ModelSpec, X_train: pd.DataFrame, y_train: pd.Series) -> tuple[Pipeline, dict[str, object], float]:
    pipeline = make_model_pipeline(spec.estimator)
    started = time.perf_counter()

    if spec.param_grid:
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=spec.param_grid,
            scoring="neg_root_mean_squared_error",
            cv=KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        fit_time = time.perf_counter() - started
        return search.best_estimator_, search.best_params_, fit_time

    pipeline.fit(X_train, y_train)
    fit_time = time.perf_counter() - started
    return pipeline, {}, fit_time


def cross_val_rmse(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> float:
    scores = cross_val_score(
        model,
        X,
        y,
        scoring="neg_root_mean_squared_error",
        cv=KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        n_jobs=-1,
    )
    return float(-scores.mean())


def feature_summary(model: Pipeline) -> tuple[str, pd.DataFrame]:
    preprocess = model.named_steps["preprocess"]
    fitted_model = model.named_steps["model"]
    feature_names = preprocess.get_feature_names_out()

    if hasattr(fitted_model, "feature_importances_"):
        values = fitted_model.feature_importances_
        value_name = "importance"
    elif hasattr(fitted_model, "coef_"):
        values = np.abs(np.ravel(fitted_model.coef_))
        value_name = "absolute_coefficient"
    else:
        values = np.zeros(len(feature_names))
        value_name = "value"

    table = pd.DataFrame({"feature": feature_names, value_name: values})
    table = table.sort_values(value_name, ascending=False).reset_index(drop=True)
    top_feature = str(table.iloc[0]["feature"]) if len(table) else "Not available"
    return top_feature, table


def grouped_error_notes(prediction_frame: pd.DataFrame) -> dict[str, object]:
    by_hour = prediction_frame.groupby("hour")["absolute_error"].mean().sort_values(ascending=False)
    by_season = prediction_frame.groupby("seasons")["absolute_error"].mean().sort_values(ascending=False)
    by_holiday = prediction_frame.groupby("holiday")["absolute_error"].mean().sort_values(ascending=False)
    by_functioning = prediction_frame.groupby("functioning_day")["absolute_error"].mean().sort_values(ascending=False)

    return {
        "worst_hour": int(by_hour.index[0]),
        "worst_hour_mae": float(by_hour.iloc[0]),
        "worst_season": str(by_season.index[0]),
        "worst_season_mae": float(by_season.iloc[0]),
        "worst_holiday_group": str(by_holiday.index[0]),
        "worst_holiday_group_mae": float(by_holiday.iloc[0]),
        "worst_functioning_day_group": str(by_functioning.index[0]),
        "worst_functioning_day_group_mae": float(by_functioning.iloc[0]),
    }


def plot_metric_comparison(comparison: pd.DataFrame) -> None:
    figure_path = FIGURES_DIR / "08_model_rmse_comparison.png"
    plt.figure(figsize=(9, 5))
    bars = plt.bar(comparison["model"], comparison["test_rmse"], color=["#526d82", "#7a9d54", "#d08c60", "#5865a8"])
    plt.title("Model Comparison by Test RMSE")
    plt.ylabel("RMSE")
    plt.xticks(rotation=18, ha="right")
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=180)
    plt.close()


def plot_predictions(best_predictions: pd.DataFrame) -> None:
    plt.figure(figsize=(6, 6))
    plt.scatter(best_predictions["actual"], best_predictions["predicted"], s=14, alpha=0.45, color="#4a6fa5")
    limit = max(best_predictions["actual"].max(), best_predictions["predicted"].max())
    plt.plot([0, limit], [0, limit], color="#222222", linewidth=1)
    plt.title("Actual vs Predicted Demand")
    plt.xlabel("Actual rented bike count")
    plt.ylabel("Predicted rented bike count")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "09_actual_vs_predicted.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(best_predictions["residual"], bins=40, color="#7a9d54", edgecolor="white")
    plt.title("Residual Distribution for Selected Model")
    plt.xlabel("Actual - predicted")
    plt.ylabel("Number of test rows")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "10_residual_distribution.png", dpi=180)
    plt.close()

    hour_error = best_predictions.groupby("hour")["absolute_error"].mean()
    plt.figure(figsize=(9, 5))
    plt.plot(hour_error.index, hour_error.values, marker="o", color="#d08c60")
    plt.title("Selected Model Error by Hour")
    plt.xlabel("Hour")
    plt.ylabel("MAE")
    plt.xticks(range(0, 24, 2))
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "11_error_by_hour.png", dpi=180)
    plt.close()

    season_error = best_predictions.groupby("seasons")["absolute_error"].mean().sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    plt.bar(season_error.index, season_error.values, color="#5865a8")
    plt.title("Selected Model Error by Season")
    plt.xlabel("Season")
    plt.ylabel("MAE")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "12_error_by_season.png", dpi=180)
    plt.close()


def plot_feature_importance(feature_table: pd.DataFrame) -> None:
    value_column = [column for column in feature_table.columns if column != "feature"][0]
    top = feature_table.head(12).iloc[::-1]
    labels = top["feature"].str.replace("num__", "", regex=False).str.replace("cat__", "", regex=False)
    plt.figure(figsize=(9, 6))
    plt.barh(labels, top[value_column], color="#526d82")
    plt.title("Top Features for Selected Model")
    plt.xlabel(value_column.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "13_feature_importance.png", dpi=180)
    plt.close()


def train_and_evaluate() -> dict[str, object]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "tmp" / "matplotlib").mkdir(parents=True, exist_ok=True)

    prepared = save_prepared_dataset()
    X, y = split_features_target(prepared)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=RANDOM_STATE,
        shuffle=True,
    )

    rows: list[dict[str, object]] = []
    prediction_frames: dict[str, pd.DataFrame] = {}
    feature_tables: dict[str, pd.DataFrame] = {}
    fitted_models: dict[str, Pipeline] = {}

    for spec in MODEL_SPECS:
        model, best_params, fit_time = tune_or_fit_model(spec, X_train, y_train)
        train_pred = model.predict(X_train)
        test_pred = np.maximum(model.predict(X_test), 0)

        train_r2 = float(r2_score(y_train, train_pred))
        test_r2 = float(r2_score(y_test, test_pred))
        test_mae = float(mean_absolute_error(y_test, test_pred))
        test_rmse = rmse(y_test, test_pred)
        train_rmse = rmse(y_train, train_pred)
        cv_rmse = cross_val_rmse(model, X_train, y_train)

        predictions = X_test.copy()
        predictions["actual"] = y_test.values
        predictions["predicted"] = test_pred
        predictions["residual"] = predictions["actual"] - predictions["predicted"]
        predictions["absolute_error"] = predictions["residual"].abs()

        top_feature, feature_table = feature_summary(model)
        grouped_notes = grouped_error_notes(predictions)

        rows.append(
            {
                "model": spec.name,
                "model_family": spec.family,
                "test_mae": test_mae,
                "test_rmse": test_rmse,
                "test_r2": test_r2,
                "adjusted_r2": adjusted_r2(test_r2, len(y_test), len(FEATURE_COLUMNS)),
                "training_r2": train_r2,
                "testing_r2": test_r2,
                "train_test_r2_gap": train_r2 - test_r2,
                "train_rmse": train_rmse,
                "cross_validation_rmse": cv_rmse,
                "residual_mean": float(predictions["residual"].mean()),
                "residual_std": float(predictions["residual"].std()),
                "max_absolute_error": float(predictions["absolute_error"].max()),
                "worst_hour": grouped_notes["worst_hour"],
                "worst_hour_mae": grouped_notes["worst_hour_mae"],
                "worst_season": grouped_notes["worst_season"],
                "worst_season_mae": grouped_notes["worst_season_mae"],
                "worst_holiday_group": grouped_notes["worst_holiday_group"],
                "worst_holiday_group_mae": grouped_notes["worst_holiday_group_mae"],
                "worst_functioning_day_group": grouped_notes["worst_functioning_day_group"],
                "worst_functioning_day_group_mae": grouped_notes["worst_functioning_day_group_mae"],
                "top_feature": top_feature,
                "interpretability": spec.interpretability,
                "training_tuning_complexity": spec.tuning_complexity,
                "streamlit_deployment_suitability": spec.streamlit_suitability,
                "fit_time_seconds": fit_time,
                "best_parameters": json.dumps(best_params),
            }
        )

        joblib.dump(model, MODELS_DIR / spec.filename)
        prediction_frames[spec.name] = predictions
        feature_tables[spec.name] = feature_table
        fitted_models[spec.name] = model

    comparison = pd.DataFrame(rows).sort_values("test_rmse").reset_index(drop=True)
    comparison["rank_by_rmse"] = np.arange(1, len(comparison) + 1)
    best_model_name = str(comparison.iloc[0]["model"])
    best_predictions = prediction_frames[best_model_name]
    best_feature_table = feature_tables[best_model_name]

    comparison.to_csv(MODELS_DIR / "model_comparison.csv", index=False)
    comparison.to_csv(TABLES_DIR / "model_comparison.csv", index=False)
    best_predictions.to_csv(MODELS_DIR / "test_predictions_best_model.csv", index=False)
    best_predictions.to_csv(TABLES_DIR / "test_predictions_best_model.csv", index=False)
    best_feature_table.to_csv(MODELS_DIR / "feature_importance_best_model.csv", index=False)
    best_feature_table.to_csv(TABLES_DIR / "feature_importance_best_model.csv", index=False)
    joblib.dump(fitted_models[best_model_name], MODELS_DIR / "best_model.pkl")

    metadata = {
        "project_title": "Seoul Bike Sharing Demand",
        "project_frame": "Bike Supply Planning",
        "target": TARGET_COLUMN,
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "split_strategy": "Random 70/30 train-test split with random_state=42.",
        "preprocessing_decisions": [
            "Date was converted to a date type and expanded into month, day, weekday, and weekend fields.",
            "Categorical variables were one-hot encoded: seasons, holiday, and functioning_day.",
            "Non-functioning-day records were kept because a zero-demand closure state is operationally meaningful.",
            "Demand outliers were kept because supply planning must understand peak demand rather than hide it.",
            "Numeric features were scaled so Multiple Linear Regression can be compared fairly with the tree models.",
        ],
        "models_trained": [spec.name for spec in MODEL_SPECS],
        "selected_model": best_model_name,
        "selected_model_reason": (
            f"{best_model_name} achieved the lowest test RMSE among the four required models "
            "while remaining suitable for a Streamlit prototype."
        ),
        "comparison_points_count": int(len(comparison.columns)),
    }
    (MODELS_DIR / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    plot_metric_comparison(comparison)
    plot_predictions(best_predictions)
    plot_feature_importance(best_feature_table)

    return {
        "comparison": comparison,
        "metadata": metadata,
        "best_predictions": best_predictions,
    }


if __name__ == "__main__":
    result = train_and_evaluate()
    print(json.dumps(result["metadata"], indent=2))
