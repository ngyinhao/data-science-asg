"""Create charts, notebooks, and report material for the Seoul Bike project."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / "tmp" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np
import pandas as pd
import joblib

from data_preprocessing import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    PROJECT_ROOT,
    TARGET_COLUMN,
    load_raw_data,
    prepare_dataset,
    save_prepared_dataset,
)


FIGURES_DIR = PROJECT_ROOT / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REPORT_DIR = PROJECT_ROOT / "report"
TABLES_DIR = REPORT_DIR / "tables"
MODELS_DIR = PROJECT_ROOT / "models"


def ensure_dirs() -> None:
    for path in [FIGURES_DIR, NOTEBOOKS_DIR, REPORT_DIR, TABLES_DIR, MODELS_DIR, PROJECT_ROOT / "tmp" / "matplotlib"]:
        path.mkdir(parents=True, exist_ok=True)


def save_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def order_existing(values: list[str], preferred_order: list[str]) -> list[str]:
    ordered = [value for value in preferred_order if value in values]
    ordered.extend([value for value in values if value not in ordered])
    return ordered


def create_eda_tables(prepared: pd.DataFrame) -> dict[str, object]:
    missing = prepared.isna().sum().reset_index()
    missing.columns = ["column", "missing_count"]
    dtypes = prepared.dtypes.astype(str).reset_index()
    dtypes.columns = ["column", "data_type"]
    numeric_summary = prepared[NUMERIC_FEATURES + [TARGET_COLUMN]].describe().T.reset_index()
    categorical_rows = []
    for column in CATEGORICAL_FEATURES:
        counts = prepared[column].value_counts().reset_index()
        counts.columns = ["category", "count"]
        counts.insert(0, "column", column)
        categorical_rows.append(counts)
    categorical_counts = pd.concat(categorical_rows, ignore_index=True)

    missing.to_csv(TABLES_DIR / "missing_values.csv", index=False)
    dtypes.to_csv(TABLES_DIR / "data_types.csv", index=False)
    numeric_summary.to_csv(TABLES_DIR / "numeric_summary.csv", index=False)
    categorical_counts.to_csv(TABLES_DIR / "categorical_counts.csv", index=False)

    return {
        "shape": prepared.shape,
        "missing_total": int(prepared.isna().sum().sum()),
        "duplicates": int(prepared.duplicated().sum()),
        "missing": missing,
        "dtypes": dtypes,
        "numeric_summary": numeric_summary,
        "categorical_counts": categorical_counts,
    }


def create_eda_figures(prepared: pd.DataFrame) -> dict[str, str]:
    figure_notes: dict[str, str] = {}

    by_hour = prepared.groupby("hour")[TARGET_COLUMN].mean()
    plt.figure(figsize=(9, 5))
    plt.plot(by_hour.index, by_hour.values, marker="o", color="#526d82")
    plt.title("Average Rented Bike Count by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average rented bike count")
    plt.xticks(range(0, 24, 2))
    save_plot(FIGURES_DIR / "01_demand_by_hour.png")
    figure_notes["01_demand_by_hour.png"] = (
        f"Demand is highest around {int(by_hour.idxmax())}:00 and lowest around {int(by_hour.idxmin())}:00."
    )

    season_order = order_existing(list(prepared["seasons"].unique()), ["Spring", "Summer", "Autumn", "Winter"])
    by_season = prepared.groupby("seasons")[TARGET_COLUMN].mean().reindex(season_order)
    plt.figure(figsize=(7, 5))
    plt.bar(by_season.index, by_season.values, color="#7a9d54")
    plt.title("Average Rented Bike Count by Season")
    plt.xlabel("Season")
    plt.ylabel("Average rented bike count")
    save_plot(FIGURES_DIR / "02_demand_by_season.png")
    figure_notes["02_demand_by_season.png"] = (
        f"{by_season.idxmax()} has the highest average demand, while {by_season.idxmin()} has the lowest."
    )

    by_holiday = prepared.groupby("holiday")[TARGET_COLUMN].mean().sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    plt.bar(by_holiday.index, by_holiday.values, color="#d08c60")
    plt.title("Average Rented Bike Count by Holiday Status")
    plt.xlabel("Holiday status")
    plt.ylabel("Average rented bike count")
    save_plot(FIGURES_DIR / "03_demand_by_holiday.png")
    figure_notes["03_demand_by_holiday.png"] = (
        f"The higher-demand holiday group is {by_holiday.index[0]}."
    )

    by_functioning = prepared.groupby("functioning_day")[TARGET_COLUMN].mean().sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    plt.bar(by_functioning.index, by_functioning.values, color="#5865a8")
    plt.title("Average Rented Bike Count by Functioning Day")
    plt.xlabel("Functioning day")
    plt.ylabel("Average rented bike count")
    save_plot(FIGURES_DIR / "04_demand_by_functioning_day.png")
    figure_notes["04_demand_by_functioning_day.png"] = (
        "Non-functioning rows show near-zero demand, so this field is important for operational interpretation."
    )

    sample = prepared.sample(min(len(prepared), 3000), random_state=42)
    plt.figure(figsize=(8, 5))
    plt.scatter(sample["temperature_c"], sample[TARGET_COLUMN], s=12, alpha=0.35, color="#4a6fa5")
    temp_fit = np.polyfit(prepared["temperature_c"], prepared[TARGET_COLUMN], deg=1)
    xs = np.linspace(prepared["temperature_c"].min(), prepared["temperature_c"].max(), 100)
    plt.plot(xs, temp_fit[0] * xs + temp_fit[1], color="#222222", linewidth=1)
    plt.title("Temperature vs Rented Bike Count")
    plt.xlabel("Temperature (C)")
    plt.ylabel("Rented bike count")
    save_plot(FIGURES_DIR / "05_temperature_vs_rented_bike_count.png")
    temp_corr = prepared["temperature_c"].corr(prepared[TARGET_COLUMN])
    figure_notes["05_temperature_vs_rented_bike_count.png"] = (
        f"Temperature has a correlation of {temp_corr:.2f} with rented bike count."
    )

    plt.figure(figsize=(8, 5))
    plt.scatter(sample["rainfall_mm"], sample[TARGET_COLUMN], s=12, alpha=0.35, color="#526d82")
    plt.title("Rainfall vs Rented Bike Count")
    plt.xlabel("Rainfall (mm)")
    plt.ylabel("Rented bike count")
    save_plot(FIGURES_DIR / "06_rainfall_vs_rented_bike_count.png")
    dry_mean = prepared.loc[prepared["rainfall_mm"] == 0, TARGET_COLUMN].mean()
    rainy_mean = prepared.loc[prepared["rainfall_mm"] > 0, TARGET_COLUMN].mean()
    figure_notes["06_rainfall_vs_rented_bike_count.png"] = (
        f"Average demand is {dry_mean:.0f} in dry hours and {rainy_mean:.0f} in rainy hours."
    )

    numeric_corr = prepared[NUMERIC_FEATURES + [TARGET_COLUMN]].corr()
    plt.figure(figsize=(10, 8))
    image = plt.imshow(numeric_corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(image, fraction=0.046, pad=0.04)
    labels = numeric_corr.columns
    plt.xticks(range(len(labels)), labels, rotation=75, ha="right", fontsize=8)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.title("Correlation Heatmap")
    save_plot(FIGURES_DIR / "07_correlation_heatmap.png")
    top_corr = (
        numeric_corr[TARGET_COLUMN]
        .drop(TARGET_COLUMN)
        .abs()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )
    figure_notes["07_correlation_heatmap.png"] = (
        "The strongest numeric relationships with demand are " + ", ".join(top_corr) + "."
    )

    snowfall_mean = prepared.loc[prepared["snowfall_cm"] > 0, TARGET_COLUMN].mean()
    no_snow_mean = prepared.loc[prepared["snowfall_cm"] == 0, TARGET_COLUMN].mean()
    figure_notes["snowfall_observation"] = (
        f"Average demand is {no_snow_mean:.0f} without snowfall and {snowfall_mean:.0f} when snowfall is recorded."
    )

    return figure_notes


def create_eda_observations(prepared: pd.DataFrame, figure_notes: dict[str, str]) -> dict[str, str]:
    by_hour = prepared.groupby("hour")[TARGET_COLUMN].mean()
    by_season = prepared.groupby("seasons")[TARGET_COLUMN].mean()
    holiday_mean = prepared.groupby("holiday")[TARGET_COLUMN].mean().sort_values(ascending=False)
    functioning_mean = prepared.groupby("functioning_day")[TARGET_COLUMN].mean().sort_values(ascending=False)
    correlations = prepared[NUMERIC_FEATURES + [TARGET_COLUMN]].corr()[TARGET_COLUMN].drop(TARGET_COLUMN)

    heavy_rain = prepared.loc[prepared["rainfall_mm"] >= 5, TARGET_COLUMN].mean()
    dry = prepared.loc[prepared["rainfall_mm"] == 0, TARGET_COLUMN].mean()
    snow = prepared.loc[prepared["snowfall_cm"] > 0, TARGET_COLUMN].mean()
    no_snow = prepared.loc[prepared["snowfall_cm"] == 0, TARGET_COLUMN].mean()

    observations = {
        "highest_hour": f"{int(by_hour.idxmax())}:00 has the highest average rented-bike demand.",
        "lowest_hour": f"{int(by_hour.idxmin())}:00 has the lowest average rented-bike demand.",
        "highest_season": f"{by_season.idxmax()} has the highest average demand.",
        "lowest_season": f"{by_season.idxmin()} has the lowest average demand.",
        "temperature": f"Demand generally increases with temperature; the correlation is {correlations['temperature_c']:.2f}.",
        "rainfall": f"Rainfall reduces demand: dry-hour average is {dry:.0f}, while hours with at least 5 mm rain average {heavy_rain:.0f}.",
        "snowfall": f"Snowfall reduces demand: no-snow average is {no_snow:.0f}, while snow hours average {snow:.0f}.",
        "holiday": f"{holiday_mean.index[0]} has higher average demand than {holiday_mean.index[-1]}.",
        "functioning_day": f"When Functioning Day is {functioning_mean.index[-1]}, demand drops heavily and is usually near zero.",
        "strongest_features": "The strongest numeric relationships are "
        + ", ".join(correlations.abs().sort_values(ascending=False).head(5).index.tolist())
        + ".",
    }

    lines = [
        "# EDA Observations",
        "",
        "These notes answer the project EDA questions for bike supply planning.",
        "",
    ]
    for title, text in observations.items():
        lines.append(f"- **{title.replace('_', ' ').title()}**: {text}")
    lines.append("")
    lines.append("## Chart Notes")
    lines.append("")
    for figure, note in figure_notes.items():
        lines.append(f"- `{figure}`: {note}")

    (REPORT_DIR / "eda_observations.md").write_text("\n".join(lines), encoding="utf-8")
    (REPORT_DIR / "eda_observations.json").write_text(json.dumps(observations, indent=2), encoding="utf-8")
    return observations


def md_image(filename: str, caption: str) -> str:
    return f"![{caption}](../figures/{filename})"


def code_cell(source: str):
    return nbf.v4.new_code_cell(source)


def markdown_cell(source: str):
    return nbf.v4.new_markdown_cell(source)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Create a compact markdown table without optional dependencies."""

    display_df = df.copy()
    for column in display_df.select_dtypes(include=["float"]).columns:
        display_df[column] = display_df[column].map(lambda value: f"{value:.3f}")
    headers = [str(column) for column in display_df.columns]
    rows = [[str(value) for value in row] for row in display_df.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_notebook(path: Path, cells: list[object]) -> None:
    notebook = nbf.v4.new_notebook()
    notebook["cells"] = cells
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nbf.write(notebook, path)


def create_notebooks(tables: dict[str, object], observations: dict[str, str]) -> None:
    shape = tables["shape"]
    missing_total = tables["missing_total"]
    duplicates = tables["duplicates"]

    eda_cells = [
        markdown_cell("# Seoul Bike Sharing Demand - 01 Data Understanding\n\nProject frame: Bike Supply Planning."),
        markdown_cell(
            f"The dataset contains {shape[0]:,} hourly records and {shape[1]} prepared columns. "
            f"The formal checks found {missing_total} missing values and {duplicates} duplicate rows."
        ),
        code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "import sys\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "sys.path.insert(0, str(PROJECT_ROOT / 'src'))\n"
            "from data_preprocessing import load_raw_data, prepare_dataset\n\n"
            "raw = load_raw_data(PROJECT_ROOT / 'data' / 'raw' / 'SeoulBikeData.csv', encoding='cp949')\n"
            "df = prepare_dataset(raw)\n"
            "df.shape"
        ),
        code_cell("df.head()"),
        code_cell("pd.DataFrame({'column': df.columns, 'dtype': df.dtypes.astype(str).values})"),
        code_cell("df.isna().sum().to_frame('missing_count')"),
        code_cell("df.duplicated().sum()"),
        code_cell("df.describe().T"),
        code_cell("for column in ['seasons', 'holiday', 'functioning_day']:\n    display(df[column].value_counts())"),
        markdown_cell("## Demand by Hour\n\n" + md_image("01_demand_by_hour.png", "Average demand by hour") + "\n\n" + observations["highest_hour"] + " " + observations["lowest_hour"]),
        markdown_cell("## Demand by Season\n\n" + md_image("02_demand_by_season.png", "Average demand by season") + "\n\n" + observations["highest_season"] + " " + observations["lowest_season"]),
        markdown_cell("## Demand by Holiday\n\n" + md_image("03_demand_by_holiday.png", "Average demand by holiday") + "\n\n" + observations["holiday"]),
        markdown_cell("## Demand by Functioning Day\n\n" + md_image("04_demand_by_functioning_day.png", "Average demand by functioning day") + "\n\n" + observations["functioning_day"]),
        markdown_cell("## Temperature and Rainfall\n\n" + md_image("05_temperature_vs_rented_bike_count.png", "Temperature vs rented bike count") + "\n\n" + observations["temperature"] + "\n\n" + md_image("06_rainfall_vs_rented_bike_count.png", "Rainfall vs rented bike count") + "\n\n" + observations["rainfall"]),
        markdown_cell("## Correlation Heatmap\n\n" + md_image("07_correlation_heatmap.png", "Correlation heatmap") + "\n\n" + observations["strongest_features"]),
    ]
    write_notebook(NOTEBOOKS_DIR / "01_data_understanding.ipynb", eda_cells)

    prep_cells = [
        markdown_cell("# Seoul Bike Sharing Demand - 02 Data Preparation"),
        markdown_cell(
            "This notebook documents the preprocessing decisions used before modelling: Date conversion, calendar feature extraction, categorical encoding, keeping non-functioning-day records, keeping peak-demand outliers, scaling numeric variables, and train-test splitting."
        ),
        code_cell(
            "from pathlib import Path\n"
            "import sys\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "sys.path.insert(0, str(PROJECT_ROOT / 'src'))\n"
            "from data_preprocessing import save_prepared_dataset, FEATURE_COLUMNS, NUMERIC_FEATURES, CATEGORICAL_FEATURES\n\n"
            "prepared = save_prepared_dataset(PROJECT_ROOT / 'data' / 'processed' / 'seoul_bike_prepared.csv')\n"
            "prepared.head()"
        ),
        code_cell("prepared[['date', 'month', 'day', 'weekday', 'is_weekend']].head()"),
        code_cell("NUMERIC_FEATURES"),
        code_cell("CATEGORICAL_FEATURES"),
        code_cell("FEATURE_COLUMNS"),
        markdown_cell(
            "## Decisions\n\n"
            "- Date was converted into a true date type and expanded into month, day, weekday, and weekend fields.\n"
            "- Seasons, Holiday, and Functioning Day are encoded through the modelling pipeline with one-hot encoding.\n"
            "- Non-functioning-day records are kept because a closure or inactive system state is important for bike supply planning.\n"
            "- Outliers are kept because peak demand is exactly what the supply planning frame needs to understand.\n"
            "- Numeric features are scaled so Multiple Linear Regression has a fair baseline setup.\n"
            "- The project uses a 70/30 train-test split with a fixed random seed for reproducibility."
        ),
    ]
    write_notebook(NOTEBOOKS_DIR / "02_data_preparation.ipynb", prep_cells)

    comparison_path = MODELS_DIR / "model_comparison.csv"
    if comparison_path.exists():
        comparison = pd.read_csv(comparison_path)
        best = comparison.sort_values("test_rmse").iloc[0]
        best_text = (
            f"The selected model is {best['model']} because it produced the lowest test RMSE "
            f"({best['test_rmse']:.2f}) with test R2 of {best['test_r2']:.3f}."
        )
    else:
        best_text = "Run src/train_models.py to populate the model comparison outputs."

    model_cells = [
        markdown_cell("# Seoul Bike Sharing Demand - 03 Modelling and Evaluation"),
        markdown_cell(
            "Four required models are compared: Multiple Linear Regression, Decision Tree Regressor, Random Forest Regressor, and Gradient Boosting Regressor."
        ),
        code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "comparison = pd.read_csv(PROJECT_ROOT / 'models' / 'model_comparison.csv')\n"
            "comparison"
        ),
        markdown_cell(
            "## Minimum 15 Comparison Points\n\n"
            "The comparison table includes MAE, RMSE, R2, adjusted R2, training score, testing score, train-test gap, cross-validation RMSE, residual mean, residual standard deviation, maximum absolute error, worst hour error, worst season error, worst holiday/functioning-day error, feature importance, interpretability, tuning complexity, deployment suitability, fit time, tuned parameters, and final rank."
        ),
        markdown_cell("## Model Ranking\n\n" + md_image("08_model_rmse_comparison.png", "Model RMSE comparison")),
        markdown_cell("## Actual vs Predicted\n\n" + md_image("09_actual_vs_predicted.png", "Actual vs predicted")),
        markdown_cell("## Residual Distribution\n\n" + md_image("10_residual_distribution.png", "Residual distribution")),
        markdown_cell("## Error by Hour and Season\n\n" + md_image("11_error_by_hour.png", "Error by hour") + "\n\n" + md_image("12_error_by_season.png", "Error by season")),
        markdown_cell("## Feature Importance\n\n" + md_image("13_feature_importance.png", "Feature importance")),
        markdown_cell("## Final Model Choice\n\n" + best_text),
    ]
    write_notebook(NOTEBOOKS_DIR / "03_modelling_evaluation.ipynb", model_cells)


def create_report(observations: dict[str, str]) -> None:
    comparison_path = MODELS_DIR / "model_comparison.csv"
    metadata_path = MODELS_DIR / "model_metadata.json"
    if comparison_path.exists():
        comparison = pd.read_csv(comparison_path).sort_values("test_rmse")
        best = comparison.iloc[0]
        model_summary = (
            f"The best model is **{best['model']}** with test RMSE **{best['test_rmse']:.2f}**, "
            f"MAE **{best['test_mae']:.2f}**, and R2 **{best['test_r2']:.3f}**."
        )
        comparison_markdown = dataframe_to_markdown(
            comparison[
            [
                "model",
                "test_mae",
                "test_rmse",
                "test_r2",
                "adjusted_r2",
                "training_r2",
                "train_test_r2_gap",
                "cross_validation_rmse",
                "top_feature",
                "rank_by_rmse",
            ]
            ]
        )
    else:
        model_summary = "Model outputs have not been generated yet."
        comparison_markdown = "Run `src/train_models.py` to generate the model comparison table."

    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        preprocessing_decisions = "\n".join(f"- {item}" for item in metadata["preprocessing_decisions"])
        selected_reason = metadata["selected_model_reason"]
    else:
        preprocessing_decisions = "- Preprocessing decisions will be filled after model training."
        selected_reason = "Selection reason will be filled after model training."

    report = f"""# Seoul Bike Sharing Demand

## Cover Page

**Project title:** Seoul Bike Sharing Demand  
**Project frame:** Bike Supply Planning  
**Problem type:** Regression  
**Target variable:** Rented Bike Count  
**Group size:** Four members  
**Required models:** Four machine learning models  

## Executive Summary

This project predicts hourly bike rental demand in Seoul so a bike-sharing operator can prepare enough bicycles during high-demand periods and avoid unnecessary oversupply during low-demand periods. The dataset contains hourly rental demand, weather, holiday, season, and system-functioning information.

{model_summary}

## 1. Business Understanding

The business problem is bike supply planning. The operational user is a bike-sharing operator, city mobility planner, or operations manager who needs a demand estimate before deciding how many bicycles should be available. The key decision is not simply which algorithm is most accurate, but which model provides trustworthy demand estimates for planning supply.

## 2. Data Understanding

The raw dataset has 8,760 hourly records and 14 original columns. It contains no missing values and no duplicate rows after formal checking. The target is hourly rented-bike count.

Main EDA findings:

- {observations['highest_hour']}
- {observations['lowest_hour']}
- {observations['highest_season']}
- {observations['lowest_season']}
- {observations['temperature']}
- {observations['rainfall']}
- {observations['snowfall']}
- {observations['holiday']}
- {observations['functioning_day']}
- {observations['strongest_features']}

Report-ready charts are saved in the `figures/` folder:

- `01_demand_by_hour.png`
- `02_demand_by_season.png`
- `03_demand_by_holiday.png`
- `04_demand_by_functioning_day.png`
- `05_temperature_vs_rented_bike_count.png`
- `06_rainfall_vs_rented_bike_count.png`
- `07_correlation_heatmap.png`

## 3. Data Preparation

{preprocessing_decisions}

The prepared modelling dataset is saved as `data/processed/seoul_bike_prepared.csv`.

## 4. Modelling

The four required models are:

1. Multiple Linear Regression as a baseline.
2. Decision Tree Regressor.
3. Random Forest Regressor.
4. Gradient Boosting Regressor.

Tree and boosting models were tuned with cross-validation. The linear model was kept as a transparent baseline.

## 5. Evaluation

The project uses more than 15 comparison points: MAE, RMSE, R2, adjusted R2, training score, testing score, train-test gap, cross-validation RMSE, residual mean, residual standard deviation, maximum absolute error, error by hour, error by season, error by holiday, error by functioning day, feature importance or coefficient strength, interpretability, training and tuning complexity, Streamlit suitability, fit time, tuned parameters, and ranking.

{comparison_markdown}

Final selection reason: {selected_reason}

## 6. Deployment

The prototype is a Streamlit app located at `app/streamlit_app.py`. Users can enter hour, season, temperature, humidity, rainfall, snowfall, holiday status, and functioning-day status. The app loads `models/best_model.pkl` and displays the predicted rented-bike count with a simple supply buffer chart.

Prototype preview image: `report/prototype_screenshot.png`.

## 7. Conclusion

The bike supply planning frame makes the project practical: the model is judged by how well it supports an operations decision, not only by raw accuracy. The selected model should be used as a decision-support tool together with current station inventory, local events, and staff judgement.

## References

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5-32. https://doi.org/10.1023/A:1010933404324

Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189-1232. https://doi.org/10.1214/aos/1013203451

Joe Beach Capital. (n.d.). *Seoul Bike Share Demand | Data Import*. Kaggle. https://www.kaggle.com/code/joebeachcapital/seoul-bike-share-demand-data-import

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825-2830. https://jmlr.org/papers/v12/pedregosa11a.html

Sathishkumar, V. E., Park, J., & Cho, Y. (2020). Using data mining techniques for bike sharing demand prediction in metropolitan city. *Computer Communications, 153*, 353-366. https://doi.org/10.1016/j.comcom.2020.02.007

Seoul Bike Sharing Demand [Dataset]. (2020). *UCI Machine Learning Repository*. https://doi.org/10.24432/C5F62R
"""

    (REPORT_DIR / "project_report_draft.md").write_text(report, encoding="utf-8")


def create_prototype_preview() -> None:
    """Create a report-ready preview image of the Streamlit prototype."""

    model_path = MODELS_DIR / "best_model.pkl"
    if not model_path.exists():
        prediction = 0.0
        selected_model = "Model not trained yet"
    else:
        model = joblib.load(model_path)
        scenario = {
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
        prediction = max(float(model.predict(pd.DataFrame([scenario], columns=FEATURE_COLUMNS))[0]), 0)
        metadata_path = MODELS_DIR / "model_metadata.json"
        if metadata_path.exists():
            selected_model = json.loads(metadata_path.read_text(encoding="utf-8"))["selected_model"]
        else:
            selected_model = "Selected model"

    fig = plt.figure(figsize=(13, 8), facecolor="#f5f7f9")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.06, 0.92, "Seoul Bike Supply Planner", fontsize=28, weight="bold", color="#1f2933")
    ax.text(0.06, 0.875, "Hourly demand estimate for bike supply planning", fontsize=13, color="#52616b")
    ax.text(0.06, 0.835, f"Model: {selected_model}", fontsize=11, color="#52616b")

    ax.add_patch(plt.Rectangle((0.06, 0.55), 0.38, 0.24, facecolor="#ffffff", edgecolor="#d9e2ec", linewidth=1))
    ax.text(0.08, 0.745, "Planning Inputs", fontsize=15, weight="bold", color="#1f2933")
    left_inputs = [
        "Hour: 18",
        "Season: Summer",
        "Holiday: No Holiday",
        "Functioning Day: Yes",
        "Weekday: Friday",
    ]
    for index, text in enumerate(left_inputs):
        ax.text(0.08, 0.71 - index * 0.032, text, fontsize=11, color="#334e68")

    ax.add_patch(plt.Rectangle((0.49, 0.55), 0.45, 0.24, facecolor="#ffffff", edgecolor="#d9e2ec", linewidth=1))
    ax.text(0.51, 0.745, "Weather Inputs", fontsize=15, weight="bold", color="#1f2933")
    weather_inputs = [
        "Temperature: 24.0 C",
        "Humidity: 55%",
        "Wind speed: 1.5 m/s",
        "Visibility: 1500 (10m)",
        "Rainfall: 0.0 mm",
        "Snowfall: 0.0 cm",
    ]
    for index, text in enumerate(weather_inputs):
        ax.text(0.51, 0.71 - index * 0.027, text, fontsize=11, color="#334e68")

    ax.add_patch(plt.Rectangle((0.06, 0.23), 0.38, 0.22, facecolor="#ffffff", edgecolor="#d9e2ec", linewidth=1))
    ax.text(0.08, 0.425, "Predicted rented bikes", fontsize=14, color="#52616b")
    ax.text(0.08, 0.355, f"{prediction:,.0f}", fontsize=40, weight="bold", color="#1f2933")
    ax.text(0.08, 0.305, "Prepare extra supply around busy stations.", fontsize=11, color="#3f7d20")

    ax.add_patch(plt.Rectangle((0.49, 0.23), 0.45, 0.22, facecolor="#ffffff", edgecolor="#d9e2ec", linewidth=1))
    ax.text(0.51, 0.425, "Supply Buffer View", fontsize=14, weight="bold", color="#1f2933")
    bars = [prediction, prediction * 1.1, prediction * 1.2]
    labels = ["Estimate", "10% buffer", "20% buffer"]
    max_bar = max(bars) if max(bars) else 1
    colors = ["#526d82", "#7a9d54", "#d08c60"]
    for index, (label, value) in enumerate(zip(labels, bars)):
        x = 0.52
        y = 0.38 - index * 0.055
        width = 0.32 * value / max_bar
        ax.add_patch(plt.Rectangle((x, y), width, 0.03, facecolor=colors[index], edgecolor="none"))
        ax.text(x + 0.335, y + 0.004, f"{label}: {value:,.0f}", fontsize=10, color="#334e68")

    ax.text(0.06, 0.16, "Prototype file: app/streamlit_app.py", fontsize=11, color="#52616b")
    ax.text(0.06, 0.13, "This preview reflects the default Streamlit scenario and saved model prediction.", fontsize=10, color="#52616b")

    fig.savefig(REPORT_DIR / "prototype_screenshot.png", dpi=180)
    fig.savefig(FIGURES_DIR / "14_prototype_preview.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    prepared = save_prepared_dataset()
    tables = create_eda_tables(prepared)
    figure_notes = create_eda_figures(prepared)
    observations = create_eda_observations(prepared, figure_notes)
    create_notebooks(tables, observations)
    create_report(observations)
    create_prototype_preview()
    print("Project artifacts created.")


if __name__ == "__main__":
    main()
