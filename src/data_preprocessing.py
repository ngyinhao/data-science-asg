"""Shared data loading and preprocessing helpers for the Seoul Bike project."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "SeoulBikeData.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "seoul_bike_prepared.csv"

TARGET_COLUMN = "rented_bike_count"
DATE_COLUMN = "date"

CATEGORICAL_FEATURES = ["seasons", "holiday", "functioning_day"]
NUMERIC_FEATURES = [
    "hour",
    "temperature_c",
    "humidity_pct",
    "wind_speed_m_per_s",
    "visibility_10m",
    "dew_point_temperature_c",
    "solar_radiation_mj_per_m2",
    "rainfall_mm",
    "snowfall_cm",
    "month",
    "day",
    "weekday",
    "is_weekend",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def clean_column_name(column_name: str) -> str:
    """Convert the raw dataset's mixed labels into stable ASCII snake_case."""

    name = column_name.strip().lower()
    name = name.replace("\N{DEGREE SIGN}", "")
    name = name.replace("%", "pct")
    name = name.replace("/", "_per_")
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def load_raw_data(path: Path | str = RAW_DATA_PATH, encoding: str = "cp949") -> pd.DataFrame:
    """Load the raw CSV with explicit encoding and normalized column names."""

    raw = pd.read_csv(path, encoding=encoding)
    df = raw.rename(columns={column: clean_column_name(column) for column in raw.columns})
    return df.rename(
        columns={
            "temperature": "temperature_c",
            "dew_point_temperature": "dew_point_temperature_c",
        }
    )


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Date and derive calendar fields used by the models."""

    prepared = df.copy()
    prepared[DATE_COLUMN] = pd.to_datetime(prepared[DATE_COLUMN], dayfirst=True, errors="coerce")
    prepared["month"] = prepared[DATE_COLUMN].dt.month
    prepared["day"] = prepared[DATE_COLUMN].dt.day
    prepared["weekday"] = prepared[DATE_COLUMN].dt.weekday
    prepared["is_weekend"] = prepared["weekday"].isin([5, 6]).astype(int)
    return prepared


def prepare_dataset(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return the modelling-ready dataset while keeping all operational rows."""

    if df is None:
        df = load_raw_data()

    prepared = add_date_features(df)
    missing_features = [column for column in FEATURE_COLUMNS + [TARGET_COLUMN] if column not in prepared.columns]
    if missing_features:
        raise ValueError(f"Missing required columns after preprocessing: {missing_features}")

    return prepared


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split the prepared dataset into feature matrix and target vector."""

    return df[FEATURE_COLUMNS].copy(), df[TARGET_COLUMN].copy()


def make_preprocessor() -> ColumnTransformer:
    """Create the shared preprocessing transformer for all four models."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def save_prepared_dataset(path: Path | str = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Prepare and save the modelling dataset."""

    prepared = prepare_dataset()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(output_path, index=False)
    return prepared
