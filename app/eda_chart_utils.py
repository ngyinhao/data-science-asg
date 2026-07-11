"""Interactive exploratory charts for historical Seoul bike demand."""

from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd

from app_utils import (
    CONTINUOUS_INSIGHT_VARIABLES,
    RAINFALL_BAND_ORDER,
    SEASON_ORDER,
    SNOWFALL_BAND_ORDER,
)
from chart_utils import BLUE, LIGHT_BLUE, NEUTRAL, ORANGE


TARGET_COLUMN = "rented_bike_count"
MEASURE_ORDER = ["Mean", "Median"]
MEASURE_COLORS = [BLUE, ORANGE]
MEASURE_SHAPES = ["circle", "diamond"]
MEASURE_DASHES = [[1, 0], [7, 4]]
SPARSE_BAND_THRESHOLD = 30

VARIABLE_SPECS: dict[str, dict[str, Any]] = {
    "Hour": {
        "kind": "hour",
        "column": "hour",
        "unit": "hour of day",
        "question": "When is hourly demand usually highest or lowest?",
    },
    "Temperature": {
        "kind": "continuous",
        "column": "temperature_c",
        "unit": "°C",
        "question": "How does demand vary across historical temperature ranges?",
    },
    "Humidity": {
        "kind": "continuous",
        "column": "humidity_pct",
        "unit": "%",
        "question": "How does demand vary across historical humidity ranges?",
    },
    "Wind speed": {
        "kind": "continuous",
        "column": "wind_speed_m_per_s",
        "unit": "m/s",
        "question": "How does demand vary across historical wind-speed ranges?",
    },
    "Visibility": {
        "kind": "continuous",
        "column": "visibility_10m",
        "unit": "10 m units",
        "question": "How does demand vary across historical visibility ranges?",
    },
    "Dew-point temperature": {
        "kind": "continuous",
        "column": "dew_point_temperature_c",
        "unit": "°C",
        "question": "How does demand vary across historical dew-point ranges?",
    },
    "Solar radiation": {
        "kind": "continuous",
        "column": "solar_radiation_mj_per_m2",
        "unit": "MJ/m²",
        "question": "How does demand vary across historical solar-radiation ranges?",
    },
    "Rainfall": {
        "kind": "exposure",
        "column": "rainfall_band",
        "unit": "mm",
        "order": RAINFALL_BAND_ORDER,
        "question": "How does demand differ across meaningful rainfall bands?",
    },
    "Snowfall": {
        "kind": "exposure",
        "column": "snowfall_band",
        "unit": "cm",
        "order": SNOWFALL_BAND_ORDER,
        "question": "How does demand differ across meaningful snowfall bands?",
    },
    "Season": {
        "kind": "season",
        "column": "seasons",
        "unit": "season category",
        "order": SEASON_ORDER,
        "question": "How do typical demand and its spread differ by season?",
    },
    "Holiday status": {
        "kind": "paired",
        "column": "holiday_label",
        "unit": "holiday category",
        "order": ["No holiday", "Holiday"],
        "question": "How does demand differ between holiday and non-holiday hours?",
    },
    "Functioning-day status": {
        "kind": "paired",
        "column": "functioning_day_label",
        "unit": "operating category",
        "order": ["Functioning", "Not functioning"],
        "question": "How does operating status change the observed demand population?",
    },
}

VARIABLE_OPTIONS = list(VARIABLE_SPECS)
WEATHER_VARIABLES = {
    "Temperature",
    "Humidity",
    "Wind speed",
    "Visibility",
    "Dew-point temperature",
    "Solar radiation",
    "Rainfall",
    "Snowfall",
}

CORRELATION_COLUMNS = [
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
]
CORRELATION_LABELS = {
    "rented_bike_count": "Rented bikes",
    "hour": "Hour",
    "temperature_c": "Temperature",
    "humidity_pct": "Humidity",
    "wind_speed_m_per_s": "Wind speed",
    "visibility_10m": "Visibility",
    "dew_point_temperature_c": "Dew point",
    "solar_radiation_mj_per_m2": "Solar radiation",
    "rainfall_mm": "Rainfall",
    "snowfall_cm": "Snowfall",
}


def default_functioning_scope(variable: str) -> str:
    """Return the population default appropriate for the selected explorer view."""

    return "Functioning days" if variable in WEATHER_VARIABLES else "All days"


def variable_question(variable: str) -> str:
    """Return the analytical question attached to one explorer option."""

    return str(VARIABLE_SPECS[variable]["question"])


def variable_unit(variable: str) -> str:
    """Return the unit or category context for one explorer option."""

    return str(VARIABLE_SPECS[variable]["unit"])


def _profile_summary(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Aggregate mean, median, and sample size for stable numeric bins."""

    group_columns = [
        f"{column}_bin_index",
        f"{column}_bin_label",
        f"{column}_bin_lower",
        f"{column}_bin_upper",
        f"{column}_bin_midpoint",
    ]
    summary = (
        data.groupby(group_columns, observed=True)[TARGET_COLUMN]
        .agg(mean_demand="mean", median_demand="median", observations="size")
        .reset_index()
        .sort_values(f"{column}_bin_index")
    )
    summary[f"{column}_bin_label"] = summary[f"{column}_bin_label"].astype(str)
    return summary


def numeric_profile_chart(data: pd.DataFrame, column: str) -> alt.LayerChart:
    """Binned mean-and-median demand profile for a continuous variable."""

    specification = CONTINUOUS_INSIGHT_VARIABLES[column]
    summary = _profile_summary(data, column)
    label_column = f"{column}_bin_label"
    midpoint_column = f"{column}_bin_midpoint"
    long = summary.melt(
        id_vars=[label_column, midpoint_column, "observations"],
        value_vars=["mean_demand", "median_demand"],
        var_name="measure",
        value_name="demand",
    )
    long["measure"] = long["measure"].map(
        {"mean_demand": "Mean", "median_demand": "Median"}
    )
    tooltip = [
        alt.Tooltip(f"{label_column}:N", title="Exact bin range"),
        alt.Tooltip("measure:N", title="Measure"),
        alt.Tooltip("demand:Q", title="Rented bikes", format=",.1f"),
        alt.Tooltip("observations:Q", title="Hourly observations", format=","),
    ]
    base = alt.Chart(long).encode(
        x=alt.X(
            f"{midpoint_column}:Q",
            title=f"{specification['label']} ({specification['unit']})",
            scale=alt.Scale(zero=False),
        ),
        y=alt.Y("demand:Q", title="Rented bikes per hour", scale=alt.Scale(zero=True)),
        color=alt.Color(
            "measure:N",
            title="Demand measure",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_COLORS),
        ),
        tooltip=tooltip,
    )
    lines = base.mark_line(strokeWidth=3).encode(
        strokeDash=alt.StrokeDash(
            "measure:N",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_DASHES),
            legend=None,
        )
    )
    points = base.mark_point(filled=True, size=95, strokeWidth=1.2).encode(
        shape=alt.Shape(
            "measure:N",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_SHAPES),
            legend=None,
        )
    )
    return (lines + points).properties(height=380).interactive(bind_y=False)


def hourly_profile_chart(data: pd.DataFrame) -> alt.LayerChart:
    """Mean-and-median demand across the ordered 24-hour cycle."""

    summary = (
        data.groupby(["hour", "hour_label"], observed=True)[TARGET_COLUMN]
        .agg(mean_demand="mean", median_demand="median", observations="size")
        .reset_index()
        .sort_values("hour")
    )
    long = summary.melt(
        id_vars=["hour", "hour_label", "observations"],
        value_vars=["mean_demand", "median_demand"],
        var_name="measure",
        value_name="demand",
    )
    long["measure"] = long["measure"].map(
        {"mean_demand": "Mean", "median_demand": "Median"}
    )
    base = alt.Chart(long).encode(
        x=alt.X(
            "hour:O",
            title="Hour of day",
            sort=list(range(24)),
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("demand:Q", title="Rented bikes per hour", scale=alt.Scale(zero=True)),
        color=alt.Color(
            "measure:N",
            title="Demand measure",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_COLORS),
        ),
        tooltip=[
            alt.Tooltip("hour_label:N", title="Hour"),
            alt.Tooltip("measure:N", title="Measure"),
            alt.Tooltip("demand:Q", title="Rented bikes", format=",.1f"),
            alt.Tooltip("observations:Q", title="Hourly observations", format=","),
        ],
    )
    lines = base.mark_line(strokeWidth=3).encode(
        strokeDash=alt.StrokeDash(
            "measure:N",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_DASHES),
            legend=None,
        )
    )
    points = base.mark_point(filled=True, size=85).encode(
        shape=alt.Shape(
            "measure:N",
            scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_SHAPES),
            legend=None,
        )
    )

    peak_hour = int(summary.loc[summary["mean_demand"].idxmax(), "hour"])
    lowest_hour = int(summary.loc[summary["mean_demand"].idxmin(), "hour"])
    if peak_hour == lowest_hour:
        annotations = summary.loc[summary["hour"] == peak_hour, ["hour", "mean_demand"]].copy()
        annotations["annotation"] = "All shown hours tie"
    else:
        annotations = summary.loc[
            summary["hour"].isin([peak_hour, lowest_hour]), ["hour", "mean_demand"]
        ].copy()
        annotations["annotation"] = annotations["hour"].map(
            {peak_hour: f"Highest: {peak_hour:02d}:00", lowest_hour: f"Lowest: {lowest_hour:02d}:00"}
        )
    labels = (
        alt.Chart(annotations)
        .mark_text(dy=-14, fontWeight="bold", color=NEUTRAL)
        .encode(x=alt.X("hour:O", sort=list(range(24))), y="mean_demand:Q", text="annotation:N")
    )
    return (lines + points + labels).properties(height=380)


def _distribution_summary(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Pre-aggregate distribution statistics for accessible interval charts."""

    def lower_whisker(values: pd.Series) -> float:
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        lower_fence = q1 - 1.5 * (q3 - q1)
        return float(values.loc[values >= lower_fence].min())

    def upper_whisker(values: pd.Series) -> float:
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        upper_fence = q3 + 1.5 * (q3 - q1)
        return float(values.loc[values <= upper_fence].max())

    summary = (
        data.groupby(group_column, observed=True)[TARGET_COLUMN]
        .agg(
            min_demand="min",
            lower_whisker=lower_whisker,
            q1_demand=lambda values: values.quantile(0.25),
            median_demand="median",
            q3_demand=lambda values: values.quantile(0.75),
            upper_whisker=upper_whisker,
            max_demand="max",
            mean_demand="mean",
            observations="size",
        )
        .reset_index()
        .rename(columns={group_column: "category"})
    )
    summary["category"] = summary["category"].astype(str)
    summary["sample_label"] = summary["observations"].map(lambda value: f"n={int(value):,}")
    summary["sample_quality"] = summary["observations"].map(
        lambda value: "Sparse" if value < SPARSE_BAND_THRESHOLD else "Sufficient"
    )
    return summary


def distribution_interval_chart(
    data: pd.DataFrame,
    group_column: str,
    order: list[str],
) -> alt.LayerChart:
    """Min/max whisker, IQR, mean, and median comparison by category."""

    summary = _distribution_summary(data, group_column)
    tooltip = [
        alt.Tooltip("category:N", title="Group"),
        alt.Tooltip("mean_demand:Q", title="Mean", format=",.1f"),
        alt.Tooltip("median_demand:Q", title="Median", format=",.1f"),
        alt.Tooltip("q1_demand:Q", title="25th percentile", format=",.1f"),
        alt.Tooltip("q3_demand:Q", title="75th percentile", format=",.1f"),
        alt.Tooltip("lower_whisker:Q", title="Lower Tukey whisker", format=",.1f"),
        alt.Tooltip("upper_whisker:Q", title="Upper Tukey whisker", format=",.1f"),
        alt.Tooltip("min_demand:Q", title="Minimum", format=",.0f"),
        alt.Tooltip("max_demand:Q", title="Maximum", format=",.0f"),
        alt.Tooltip("observations:Q", title="Hourly observations", format=","),
        alt.Tooltip("sample_quality:N", title="Sample flag"),
    ]
    x_encoding = alt.X("category:N", title=None, sort=order, axis=alt.Axis(labelAngle=0))
    base = alt.Chart(summary).encode(x=x_encoding, tooltip=tooltip)
    whisker = base.mark_rule(color=NEUTRAL, strokeWidth=2).encode(
        y=alt.Y("lower_whisker:Q", title="Rented bikes per hour", scale=alt.Scale(zero=True)),
        y2="upper_whisker:Q",
    )
    interquartile_range = base.mark_rule(color=LIGHT_BLUE, strokeWidth=14).encode(
        y="q1_demand:Q",
        y2="q3_demand:Q",
    )
    points_source = summary.assign(
        mean_tooltip=summary["mean_demand"],
        median_tooltip=summary["median_demand"],
    )
    points_data = points_source.melt(
        id_vars=[
            "category",
            "min_demand",
            "lower_whisker",
            "q1_demand",
            "q3_demand",
            "upper_whisker",
            "max_demand",
            "mean_tooltip",
            "median_tooltip",
            "observations",
            "sample_quality",
        ],
        value_vars=["mean_demand", "median_demand"],
        var_name="measure",
        value_name="demand",
    )
    points_data["measure"] = points_data["measure"].map(
        {"mean_demand": "Mean", "median_demand": "Median"}
    )
    point_tooltip = [
        alt.Tooltip("category:N", title="Group"),
        alt.Tooltip("measure:N", title="Marked measure"),
        alt.Tooltip("demand:Q", title="Marked value", format=",.1f"),
        alt.Tooltip("mean_tooltip:Q", title="Mean", format=",.1f"),
        alt.Tooltip("median_tooltip:Q", title="Median", format=",.1f"),
        alt.Tooltip("q1_demand:Q", title="25th percentile", format=",.1f"),
        alt.Tooltip("q3_demand:Q", title="75th percentile", format=",.1f"),
        alt.Tooltip("lower_whisker:Q", title="Lower Tukey whisker", format=",.1f"),
        alt.Tooltip("upper_whisker:Q", title="Upper Tukey whisker", format=",.1f"),
        alt.Tooltip("min_demand:Q", title="Minimum", format=",.0f"),
        alt.Tooltip("max_demand:Q", title="Maximum", format=",.0f"),
        alt.Tooltip("observations:Q", title="Hourly observations", format=","),
        alt.Tooltip("sample_quality:N", title="Sample flag"),
    ]
    points = (
        alt.Chart(points_data)
        .mark_point(filled=True, size=145, strokeWidth=1.2)
        .encode(
            x=x_encoding,
            y=alt.Y("demand:Q", title="Rented bikes per hour"),
            color=alt.Color(
                "measure:N",
                title="Demand measure",
                scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_COLORS),
            ),
            shape=alt.Shape(
                "measure:N",
                scale=alt.Scale(domain=MEASURE_ORDER, range=MEASURE_SHAPES),
                legend=None,
            ),
            tooltip=point_tooltip,
        )
    )
    sample_labels = base.mark_text(dy=-10, fontWeight="bold", color=NEUTRAL).encode(
        y="upper_whisker:Q",
        text="sample_label:N",
    )
    return (whisker + interquartile_range + points + sample_labels).properties(height=390)


def build_variable_chart(data: pd.DataFrame, variable: str) -> alt.LayerChart:
    """Dispatch one of the twelve explorer selections to its chart form."""

    specification = VARIABLE_SPECS[variable]
    kind = specification["kind"]
    column = str(specification["column"])
    if kind == "hour":
        return hourly_profile_chart(data)
    if kind == "continuous":
        return numeric_profile_chart(data, column)
    return distribution_interval_chart(data, column, list(specification["order"]))


def sparse_exposure_bands(data: pd.DataFrame, variable: str) -> list[str]:
    """Return post-filter rain or snow bands below the stated sample threshold."""

    specification = VARIABLE_SPECS[variable]
    if specification["kind"] != "exposure":
        return []
    counts = (
        data.groupby(str(specification["column"]), observed=True)
        .size()
        .reindex(list(specification["order"]), fill_value=0)
    )
    return [str(label) for label, count in counts.items() if count < SPARSE_BAND_THRESHOLD]


def _comparison_sentence(summary: pd.Series, reference: pd.Series) -> str:
    """Describe an absolute and percentage mean difference without causal wording."""

    difference = float(summary["mean_demand"] - reference["mean_demand"])
    reference_mean = float(reference["mean_demand"])
    percentage = abs(difference / reference_mean * 100) if reference_mean else float("nan")
    direction = "higher" if difference >= 0 else "lower"
    percentage_text = f"{percentage:.1f}% {direction}" if pd.notna(percentage) else "not percentage-comparable"
    return (
        f"{summary['category']} averages {abs(difference):,.1f} bikes {direction} than "
        f"{reference['category']} ({percentage_text}); their medians are "
        f"{float(summary['median_demand']):,.1f} and {float(reference['median_demand']):,.1f}."
    )


def variable_takeaway(data: pd.DataFrame, variable: str) -> str:
    """Calculate a concise, filter-aware interpretation for the selected chart."""

    specification = VARIABLE_SPECS[variable]
    kind = specification["kind"]
    column = str(specification["column"])
    if kind == "hour":
        summary = (
            data.groupby("hour", observed=True)[TARGET_COLUMN]
            .agg(mean_demand="mean", median_demand="median")
            .reset_index()
        )
        peak = summary.loc[summary["mean_demand"].idxmax()]
        low = summary.loc[summary["mean_demand"].idxmin()]
        if int(peak["hour"]) == int(low["hour"]):
            return f"All shown hours have the same mean demand of {float(peak['mean_demand']):,.1f} bikes."
        return (
            f"Mean demand is highest at {int(peak['hour']):02d}:00 "
            f"({float(peak['mean_demand']):,.1f}) and lowest at {int(low['hour']):02d}:00 "
            f"({float(low['mean_demand']):,.1f}) in the active population."
        )
    if kind == "continuous":
        summary = _profile_summary(data, column)
        highest = summary.loc[summary["mean_demand"].idxmax()]
        return (
            f"The highest binned mean is {float(highest['mean_demand']):,.1f} bikes in the "
            f"{highest[f'{column}_bin_label']} range; the median is "
            f"{float(highest['median_demand']):,.1f} across {int(highest['observations']):,} hours."
        )

    summary = _distribution_summary(data, column)
    order = list(specification["order"])
    summary["sort_order"] = summary["category"].map(
        {category: index for index, category in enumerate(order)}
    )
    summary = summary.sort_values("sort_order")
    if kind == "season":
        highest = summary.loc[summary["mean_demand"].idxmax()]
        lowest = summary.loc[summary["mean_demand"].idxmin()]
        return (
            f"{highest['category']} has the highest mean demand ({float(highest['mean_demand']):,.1f}), "
            f"while {lowest['category']} has the lowest ({float(lowest['mean_demand']):,.1f}); "
            "the interval shows how widely individual hours vary."
        )
    if len(summary) < 2:
        only = summary.iloc[0]
        return (
            f"Only {only['category']} is represented after filtering, with mean demand "
            f"{float(only['mean_demand']):,.1f} and median {float(only['median_demand']):,.1f}."
        )
    return _comparison_sentence(summary.iloc[-1], summary.iloc[0])


def hour_season_scale_max(data: pd.DataFrame) -> float:
    """Return the full-population scale ceiling for comparable heatmap filtering."""

    return float(
        data.groupby(["hour", "seasons"], observed=True)[TARGET_COLUMN].mean().max()
    )


def hour_season_heatmap(data: pd.DataFrame, scale_max: float) -> alt.Chart:
    """Average demand by hour and season with post-filter sample context."""

    summary = (
        data.groupby(["hour", "hour_label", "seasons"], observed=True)[TARGET_COLUMN]
        .agg(mean_demand="mean", observations="size")
        .reset_index()
    )
    return (
        alt.Chart(summary)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X(
                "hour:O",
                title="Hour of day",
                sort=list(range(24)),
                axis=alt.Axis(labelAngle=0, labelExpr="toNumber(datum.label) % 2 === 0 ? datum.label : ''"),
            ),
            y=alt.Y("seasons:N", title=None, sort=SEASON_ORDER),
            color=alt.Color(
                "mean_demand:Q",
                title="Mean rented bikes",
                scale=alt.Scale(domain=[0, scale_max], scheme="blues"),
            ),
            tooltip=[
                alt.Tooltip("hour_label:N", title="Hour"),
                alt.Tooltip("seasons:N", title="Season"),
                alt.Tooltip("mean_demand:Q", title="Mean rented bikes", format=",.1f"),
                alt.Tooltip("observations:Q", title="Hourly observations", format=","),
            ],
        )
        .properties(height=250)
    )


def hour_season_takeaway(data: pd.DataFrame) -> str:
    """Identify the highest-demand hour-season combination after filtering."""

    summary = (
        data.groupby(["hour", "seasons"], observed=True)[TARGET_COLUMN]
        .agg(mean_demand="mean", observations="size")
        .reset_index()
    )
    highest = summary.loc[summary["mean_demand"].idxmax()]
    if float(highest["mean_demand"]) == 0:
        return "Every shown hour-season cell has zero average demand in this population."
    return (
        f"The highest shown combination is {highest['seasons']} at {int(highest['hour']):02d}:00, "
        f"averaging {float(highest['mean_demand']):,.1f} rented bikes across "
        f"{int(highest['observations']):,} hourly observations."
    )


def correlation_heatmap(data: pd.DataFrame) -> alt.LayerChart:
    """Demand-correlation heatmap for the nine numeric explorer variables."""

    predictor_columns = [column for column in CORRELATION_COLUMNS if column != TARGET_COLUMN]
    correlations = data[CORRELATION_COLUMNS].corr()[TARGET_COLUMN].loc[predictor_columns]
    label_order = [CORRELATION_LABELS[column] for column in predictor_columns]
    summary = correlations.rename("correlation").rename_axis("variable").reset_index()
    summary["variable"] = summary["variable"].map(CORRELATION_LABELS)
    summary["relationship"] = "Correlation with rented-bike demand"
    summary["is_defined"] = summary["correlation"].notna()
    summary["correlation_label"] = summary["correlation"].map(
        lambda value: f"{value:.2f}" if pd.notna(value) else "N/A"
    )
    cells = (
        alt.Chart(summary)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X(
                "relationship:N",
                title=None,
                axis=alt.Axis(labels=False, ticks=False),
            ),
            y=alt.Y("variable:N", title=None, sort=label_order),
            color=alt.condition(
                "datum.is_defined",
                alt.Color(
                    "correlation:Q",
                    title="Correlation",
                    scale=alt.Scale(domain=[-1, 1], domainMid=0, scheme="redblue"),
                ),
                alt.value(NEUTRAL),
            ),
            tooltip=[
                alt.Tooltip("variable:N", title="Numeric variable"),
                alt.Tooltip("correlation_label:N", title="Correlation"),
            ],
        )
    )
    labels = (
        alt.Chart(summary)
        .mark_text(fontSize=12, fontWeight="bold")
        .encode(
            x=alt.X("relationship:N"),
            y=alt.Y("variable:N", sort=label_order),
            text="correlation_label:N",
            color=alt.condition(
                "datum.is_defined && abs(datum.correlation) >= 0.55",
                alt.value("#FFFFFF"),
                alt.value("#263238"),
            ),
        )
    )
    return (cells + labels).properties(height=360)
