"""Shared loaders and formatting helpers for the Streamlit pages."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import joblib
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_preprocessing import FEATURE_COLUMNS


MODEL_PATH = MODELS_DIR / "best_model.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
COMPARISON_PATH = MODELS_DIR / "model_comparison.csv"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance_best_model.csv"


@st.cache_resource
def load_model() -> Any:
    """Load the selected prediction model once per Streamlit process."""

    return joblib.load(MODEL_PATH)


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
