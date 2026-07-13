"""Shared loaders and formatting helpers for the Streamlit pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"
PREPARED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "seoul_bike_prepared.csv"

from src.data_preprocessing import FEATURE_COLUMNS


MODEL_PATH = MODELS_DIR / "best_model.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
COMPARISON_PATH = MODELS_DIR / "model_comparison.csv"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance_best_model.csv"
TEST_PREDICTIONS_PATH = MODELS_DIR / "test_predictions_best_model.csv"

SEASON_ORDER = ["Spring", "Summer", "Autumn", "Winter"]
RAINFALL_BAND_ORDER = ["No rain", "Light rain", "Moderate rain", "Heavy rain"]
SNOWFALL_BAND_ORDER = ["No snow", "Light snow", "Heavier snow"]
PREPARED_DATA_COLUMNS = [
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
    "month",
    "day",
    "weekday",
    "is_weekend",
]
CONTINUOUS_INSIGHT_VARIABLES = {
    "temperature_c": {"label": "Temperature", "unit": "°C", "decimals": 1},
    "humidity_pct": {"label": "Humidity", "unit": "%", "decimals": 0},
    "wind_speed_m_per_s": {"label": "Wind speed", "unit": "m/s", "decimals": 1},
    "visibility_10m": {"label": "Visibility", "unit": "10 m", "decimals": 0},
    "dew_point_temperature_c": {
        "label": "Dew-point temperature",
        "unit": "°C",
        "decimals": 1,
    },
    "solar_radiation_mj_per_m2": {
        "label": "Solar radiation",
        "unit": "MJ/m²",
        "decimals": 2,
    },
}


@st.cache_resource
def load_model() -> Any:
    """Load the selected prediction model with deployment-safe parallelism."""

    model = joblib.load(MODEL_PATH)
    estimator = getattr(model, "named_steps", {}).get("model")
    if estimator is not None and hasattr(estimator, "n_jobs"):
        estimator.n_jobs = 1
    return model


@st.cache_data
def load_metadata() -> dict[str, Any]:
    """Load model metadata used by the report pages."""

    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


@st.cache_data
def load_model_comparison() -> pd.DataFrame:
    """Load the four-model comparison table sorted by RMSE rank."""

    comparison = pd.read_csv(COMPARISON_PATH)
    if "rank_by_rmse" in comparison.columns:
        comparison = comparison.sort_values("rank_by_rmse")
    return comparison.reset_index(drop=True)


@st.cache_data
def load_feature_importance() -> pd.DataFrame:
    """Load best-model feature importance values with readable labels."""

    importance = pd.read_csv(FEATURE_IMPORTANCE_PATH)
    importance["feature_label"] = importance["feature"].map(format_feature_name)
    return importance


@st.cache_data
def load_test_predictions() -> pd.DataFrame:
    """Load held-out predictions used by the interactive evaluation charts."""

    return pd.read_csv(TEST_PREDICTIONS_PATH)


def _format_bin_edge(value: float, decimals: int) -> str:
    """Format one bin boundary without exposing floating-point noise."""

    return f"{value:,.{decimals}f}"


def prepare_insights_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Create reusable readable fields and stable bins for the insights page."""

    missing_columns = [column for column in PREPARED_DATA_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Prepared bike data is missing required columns: {missing_columns}")

    prepared = frame.copy()
    prepared["date"] = pd.to_datetime(prepared["date"], errors="raise")
    prepared["hour_label"] = prepared["hour"].map(lambda hour: f"{int(hour):02d}:00")
    prepared["holiday_label"] = prepared["holiday"].map(
        {"No Holiday": "No holiday", "Holiday": "Holiday"}
    )
    prepared["functioning_day_label"] = prepared["functioning_day"].map(
        {"Yes": "Functioning", "No": "Not functioning"}
    )
    prepared["rainfall_band"] = pd.cut(
        prepared["rainfall_mm"],
        bins=[-np.inf, 0, 1, 5, np.inf],
        labels=RAINFALL_BAND_ORDER,
        ordered=True,
    )
    prepared["snowfall_band"] = pd.cut(
        prepared["snowfall_cm"],
        bins=[-np.inf, 0, 1, np.inf],
        labels=SNOWFALL_BAND_ORDER,
        ordered=True,
    )

    for column, specification in CONTINUOUS_INSIGHT_VARIABLES.items():
        _, edges = pd.qcut(prepared[column], q=10, retbins=True, duplicates="drop")
        bin_index = pd.cut(
            prepared[column],
            bins=edges,
            labels=False,
            include_lowest=True,
        )
        if bin_index.isna().any():
            raise ValueError(f"Unable to assign every {column} value to a fixed analysis bin.")

        decimals = int(specification["decimals"])
        unit = str(specification["unit"])
        labels = [
            (
                f"{_format_bin_edge(float(edges[index]), decimals)} to "
                f"{_format_bin_edge(float(edges[index + 1]), decimals)} {unit}"
            )
            for index in range(len(edges) - 1)
        ]
        index_values = bin_index.astype("int64")
        prepared[f"{column}_bin_index"] = index_values
        prepared[f"{column}_bin_lower"] = index_values.map(
            {index: float(edges[index]) for index in range(len(edges) - 1)}
        )
        prepared[f"{column}_bin_upper"] = index_values.map(
            {index: float(edges[index + 1]) for index in range(len(edges) - 1)}
        )
        prepared[f"{column}_bin_midpoint"] = (
            prepared[f"{column}_bin_lower"] + prepared[f"{column}_bin_upper"]
        ) / 2
        prepared[f"{column}_bin_label"] = pd.Categorical(
            index_values.map(dict(enumerate(labels))),
            categories=labels,
            ordered=True,
        )

    return prepared


@st.cache_data(max_entries=1)
def load_prepared_bike_data() -> pd.DataFrame:
    """Load and enrich the complete prepared historical dataset once."""

    prepared = pd.read_csv(PREPARED_DATA_PATH)
    if len(prepared) != 8_760:
        raise ValueError(f"Prepared bike data should contain 8,760 rows, found {len(prepared):,}.")
    return prepare_insights_data(prepared)


def filter_insights_data(
    data: pd.DataFrame,
    seasons: list[str],
    functioning_scope: str,
) -> pd.DataFrame:
    """Apply inexpensive page filters after the cached full-data load."""

    filtered = data.loc[data["seasons"].isin(seasons)]
    functioning_values = {
        "Functioning days": "Yes",
        "Not functioning": "No",
    }
    if functioning_scope in functioning_values:
        filtered = filtered.loc[
            filtered["functioning_day"] == functioning_values[functioning_scope]
        ]
    elif functioning_scope != "All days":
        raise ValueError(f"Unknown functioning-day scope: {functioning_scope}")
    return filtered.copy()


def summarise_demand_insights(data: pd.DataFrame) -> dict[str, object]:
    """Recalculate the headline EDA findings from the prepared dataset."""

    target = "rented_bike_count"
    hourly_mean = data.groupby("hour", observed=True)[target].mean()
    seasonal_mean = data.groupby("seasons", observed=True)[target].mean()
    non_functioning = data.loc[data["functioning_day"] == "No", target]
    peak_hour = int(hourly_mean.idxmax())
    lowest_hour = int(hourly_mean.idxmin())
    highest_season = str(seasonal_mean.idxmax())
    lowest_season = str(seasonal_mean.idxmin())
    return {
        "peak_hour": peak_hour,
        "peak_hour_mean": float(hourly_mean.loc[peak_hour]),
        "lowest_hour": lowest_hour,
        "lowest_hour_mean": float(hourly_mean.loc[lowest_hour]),
        "highest_season": highest_season,
        "highest_season_mean": float(seasonal_mean.loc[highest_season]),
        "lowest_season": lowest_season,
        "lowest_season_mean": float(seasonal_mean.loc[lowest_season]),
        "temperature_correlation": float(data["temperature_c"].corr(data[target])),
        "dry_hour_mean": float(data.loc[data["rainfall_mm"] == 0, target].mean()),
        "heavy_rain_mean": float(data.loc[data["rainfall_mm"] >= 5, target].mean()),
        "no_snow_mean": float(data.loc[data["snowfall_cm"] == 0, target].mean()),
        "snow_mean": float(data.loc[data["snowfall_cm"] > 0, target].mean()),
        "non_functioning_mean": float(non_functioning.mean()),
        "non_functioning_rows": int(len(non_functioning)),
    }


def filtered_data_csv(data: pd.DataFrame) -> bytes:
    """Serialize only original historical columns from the active population."""

    export = data.loc[:, PREPARED_DATA_COLUMNS].copy()
    export["date"] = pd.to_datetime(export["date"]).dt.strftime("%Y-%m-%d")
    return export.to_csv(index=False).encode("utf-8")


def build_input_frame(values: dict[str, object]) -> pd.DataFrame:
    """Build a one-row feature frame in the order expected by the model."""

    row = {feature: values[feature] for feature in FEATURE_COLUMNS}
    return pd.DataFrame([row])


def figure_path(filename: str) -> Path:
    """Return the full path to a generated project figure."""

    return FIGURES_DIR / filename


def format_feature_name(feature_name: str) -> str:
    """Convert pipeline feature names into labels that read well in the UI."""

    cleaned = feature_name.replace("num__", "").replace("cat__", "")
    label_map = {
        "hour": "hour",
        "temperature_c": "temperature",
        "humidity_pct": "humidity",
        "wind_speed_m_per_s": "wind speed",
        "visibility_10m": "visibility",
        "dew_point_temperature_c": "dew point temperature",
        "solar_radiation_mj_per_m2": "solar radiation",
        "rainfall_mm": "rainfall",
        "snowfall_cm": "snowfall",
        "month": "month",
        "day": "day",
        "weekday": "weekday",
        "is_weekend": "weekend flag",
        "functioning_day_Yes": "functioning day: yes",
        "functioning_day_No": "functioning day: no",
        "holiday_No Holiday": "holiday: no holiday",
        "holiday_Holiday": "holiday: holiday",
        "seasons_Spring": "season: spring",
        "seasons_Summer": "season: summer",
        "seasons_Autumn": "season: autumn",
        "seasons_Winter": "season: winter",
    }
    return label_map.get(cleaned, cleaned.replace("_", " "))


def format_number(value: float, decimals: int = 0) -> str:
    """Format numeric metric values consistently."""

    return f"{value:,.{decimals}f}"


def selected_model_row(comparison: pd.DataFrame, selected_model: str) -> pd.Series:
    """Return the row for the selected model, falling back to the top rank."""

    matches = comparison.loc[comparison["model"] == selected_model]
    if not matches.empty:
        return matches.iloc[0]
    return comparison.iloc[0]


def readable_parameters(value: object) -> str:
    """Render tuned parameters without exposing CSV quoting details."""

    if pd.isna(value) or value in ("{}", ""):
        return "No tuned parameters"
    return str(value).replace('""', '"')
