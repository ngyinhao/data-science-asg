"""Interactive Altair charts shared by the Streamlit report pages."""

from __future__ import annotations

import math

import altair as alt
import pandas as pd


BLUE = "#4C78A8"
LIGHT_BLUE = "#72B7B2"
ORANGE = "#F58518"
GOLD = "#E5C453"
PINK = "#E45756"
OLIVE = "#8A9A5B"
PURPLE = "#B279A2"
NEUTRAL = "#9AA5B1"

MODEL_COLORS = [BLUE, ORANGE, PINK, OLIVE]
MODEL_SHORT_LABELS = {
    "Random Forest Regressor": "Random forest",
    "Gradient Boosting Regressor": "Gradient boost",
    "Decision Tree Regressor": "Decision tree",
    "Multiple Linear Regression": "Linear",
}
MODEL_COMPACT_LABELS = {
    "Random Forest Regressor": "RF",
    "Gradient Boosting Regressor": "Gradient",
    "Decision Tree Regressor": "Tree",
    "Multiple Linear Regression": "Linear",
}
SEASON_DOMAIN = ["Spring", "Summer", "Autumn", "Winter"]
SEASON_COLORS = [PINK, GOLD, ORANGE, BLUE]


def ocr_chart(chart):
    """Apply consistent, high-legibility typography to an Altair chart."""

    return (
        chart.configure_axis(
            labelFontSize=14,
            labelFontWeight=500,
            labelLimit=180,
            labelPadding=8,
            titleFontSize=16,
            titleFontWeight=600,
            titleLimit=240,
            titlePadding=12,
            gridOpacity=0.28,
        )
        .configure_legend(
            labelFontSize=14,
            labelFontWeight=500,
            labelLimit=220,
            titleFontSize=15,
            titleFontWeight=600,
            titleLimit=220,
        )
        .configure_header(
            labelFontSize=14,
            labelFontWeight=600,
            titleFontSize=15,
            titleFontWeight=600,
        )
        .configure_view(strokeWidth=0)
    )


def actual_vs_predicted_chart(predictions: pd.DataFrame) -> alt.LayerChart:
    """Scatter plot with tooltips, brushing, and a perfect-prediction reference."""

    lower = float(min(predictions["actual"].min(), predictions["predicted"].min()))
    upper = float(max(predictions["actual"].max(), predictions["predicted"].max()))
    reference = pd.DataFrame({"actual": [lower, upper], "predicted": [lower, upper]})
    brush = alt.selection_interval(name="demand_zoom", encodings=["x", "y"])

    points = (
        alt.Chart(predictions)
        .mark_circle(size=52, strokeWidth=0.4)
        .encode(
            x=alt.X("actual:Q", title="Actual rented bikes"),
            y=alt.Y("predicted:Q", title="Predicted rented bikes"),
            color=alt.Color(
                "seasons:N",
                title="Season",
                scale=alt.Scale(domain=SEASON_DOMAIN, range=SEASON_COLORS),
            ),
            opacity=alt.condition(brush, alt.value(0.75), alt.value(0.16)),
            tooltip=[
                alt.Tooltip("actual:Q", title="Actual", format=",.0f"),
                alt.Tooltip("predicted:Q", title="Predicted", format=",.0f"),
                alt.Tooltip("absolute_error:Q", title="Absolute error", format=",.1f"),
                alt.Tooltip("hour:Q", title="Hour"),
                alt.Tooltip("seasons:N", title="Season"),
                alt.Tooltip("temperature_c:Q", title="Temperature (C)", format=".1f"),
            ],
        )
        .add_params(brush)
    )
    ideal = (
        alt.Chart(reference)
        .mark_line(color=NEUTRAL, strokeDash=[7, 5], strokeWidth=2)
        .encode(x="actual:Q", y="predicted:Q")
    )
    return (ideal + points).properties(height=300).interactive()


def residual_histogram(predictions: pd.DataFrame) -> alt.LayerChart:
    """Interactive residual distribution with a zero-error reference."""

    residual_limit = max(
        100,
        math.ceil(float(predictions["residual"].abs().max()) / 100) * 100,
    )
    residual_domain = [-residual_limit, residual_limit]
    residual_ticks = [
        -residual_limit,
        -residual_limit / 2,
        0,
        residual_limit / 2,
        residual_limit,
    ]

    bars = (
        alt.Chart(predictions)
        .mark_bar(color=ORANGE, opacity=0.82, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "residual:Q",
                bin=alt.Bin(maxbins=36),
                title="Residual (actual - predicted)",
                scale=alt.Scale(domain=residual_domain, nice=False),
                axis=alt.Axis(values=residual_ticks, format=",.0f", labelAngle=-30),
            ),
            y=alt.Y("count():Q", title="Test observations"),
            tooltip=[
                alt.Tooltip("residual:Q", bin=alt.Bin(maxbins=36), title="Residual range"),
                alt.Tooltip("count():Q", title="Observations"),
            ],
        )
    )
    zero = (
        alt.Chart(pd.DataFrame({"x": [0]}))
        .mark_rule(color=NEUTRAL, strokeDash=[5, 4])
        .encode(x=alt.X("x:Q", scale=alt.Scale(domain=residual_domain, nice=False)))
    )
    return (bars + zero).properties(height=300).interactive(bind_y=False)


def hourly_error_chart(predictions: pd.DataFrame) -> alt.LayerChart:
    """Mean absolute error across the ordered 24-hour cycle."""

    hourly = predictions.groupby("hour", as_index=False).agg(
        mean_absolute_error=("absolute_error", "mean"),
        observations=("absolute_error", "size"),
    )
    base = alt.Chart(hourly).encode(
        x=alt.X(
            "hour:O",
            title="Hour of day",
            axis=alt.Axis(labelAngle=0, values=list(range(0, 24, 3))),
        ),
        y=alt.Y("mean_absolute_error:Q", title="Mean absolute error (bikes)", scale=alt.Scale(zero=True)),
        tooltip=[
            alt.Tooltip("hour:O", title="Hour"),
            alt.Tooltip("mean_absolute_error:Q", title="Mean absolute error", format=",.1f"),
            alt.Tooltip("observations:Q", title="Observations"),
        ],
    )
    line = base.mark_line(color=BLUE, strokeWidth=3)
    points = base.mark_circle(color=GOLD, size=90, stroke=BLUE, strokeWidth=1.5)
    return (line + points).properties(height=300).interactive(bind_y=False)


def seasonal_error_box_chart(predictions: pd.DataFrame) -> alt.LayerChart:
    """Seasonal box plot with Tukey whiskers and outlier context."""

    stats_rows = []
    for season, errors in predictions.groupby("seasons")["absolute_error"]:
        q1 = float(errors.quantile(0.25))
        q3 = float(errors.quantile(0.75))
        iqr = q3 - q1
        lower_fence = max(0.0, q1 - 1.5 * iqr)
        upper_fence = q3 + 1.5 * iqr
        inliers = errors.loc[errors.between(lower_fence, upper_fence)]
        stats_rows.append(
            {
                "seasons": season,
                "lower_whisker": float(inliers.min()),
                "q1": q1,
                "median": float(errors.median()),
                "q3": q3,
                "upper_whisker": float(inliers.max()),
                "mean": float(errors.mean()),
                "outlier_count": int((~errors.between(lower_fence, upper_fence)).sum()),
                "observations": int(len(errors)),
            }
        )
    stats = pd.DataFrame(stats_rows)
    color = alt.Color("seasons:N", title="Season", scale=alt.Scale(domain=SEASON_DOMAIN, range=SEASON_COLORS), legend=None)
    tooltip = [
        alt.Tooltip("seasons:N", title="Season"),
        alt.Tooltip("lower_whisker:Q", title="Lower whisker", format=",.1f"),
        alt.Tooltip("q1:Q", title="25th percentile", format=",.1f"),
        alt.Tooltip("median:Q", title="Median", format=",.1f"),
        alt.Tooltip("q3:Q", title="75th percentile", format=",.1f"),
        alt.Tooltip("upper_whisker:Q", title="Upper whisker", format=",.1f"),
        alt.Tooltip("mean:Q", title="Mean", format=",.1f"),
        alt.Tooltip("outlier_count:Q", title="Outliers beyond whiskers", format=",d"),
        alt.Tooltip("observations:Q", title="Observations", format=",d"),
    ]
    base = alt.Chart(stats).encode(
        x=alt.X(
            "seasons:N",
            title="Season",
            sort=SEASON_DOMAIN,
            axis=alt.Axis(labelAngle=0),
        ),
        color=color,
        tooltip=tooltip,
    )
    whisker = base.mark_rule(strokeWidth=2).encode(
        y=alt.Y("lower_whisker:Q", title="Absolute error (bikes)"),
        y2="upper_whisker:Q",
    )
    box = base.mark_bar(size=48, opacity=0.85).encode(y="q1:Q", y2="q3:Q")
    median = base.mark_tick(color="#263238", thickness=3, size=48).encode(y="median:Q")
    mean = base.mark_point(filled=True, color="#FFFFFF", stroke="#263238", size=75).encode(y="mean:Q")
    return (whisker + box + median + mean).properties(height=300)


def feature_importance_chart(importance: pd.DataFrame, top_n: int = 12) -> alt.LayerChart:
    """Horizontal lollipop ranking for the strongest feature drivers."""

    data = importance.head(top_n).copy()
    data["zero"] = 0.0
    order = list(data["feature_label"])
    base = alt.Chart(data).encode(
        y=alt.Y("feature_label:N", title=None, sort=order),
        tooltip=[
            alt.Tooltip("feature_label:N", title="Feature"),
            alt.Tooltip("importance:Q", title="Importance", format=".3f"),
        ],
    )
    stems = base.mark_rule(color=LIGHT_BLUE, strokeWidth=3).encode(x=alt.X("zero:Q", title="Feature importance"), x2="importance:Q")
    dots = base.mark_circle(size=125, color=BLUE, stroke="#FFFFFF", strokeWidth=1).encode(x="importance:Q")
    return (stems + dots).properties(height=max(300, top_n * 28)).interactive(bind_y=False)


def rmse_ranking_chart(comparison: pd.DataFrame) -> alt.LayerChart:
    """Ranked lollipop chart that highlights the selected model."""

    data = comparison.sort_values("test_rmse").copy()
    data["zero"] = 0.0
    data["model_label"] = data["model"].map(MODEL_SHORT_LABELS)
    best = str(data.iloc[0]["model"])
    order = list(data["model_label"])
    base = alt.Chart(data).encode(
        y=alt.Y("model_label:N", title=None, sort=order),
        tooltip=[
            alt.Tooltip("model:N", title="Model"),
            alt.Tooltip("test_rmse:Q", title="Test RMSE", format=",.1f"),
            alt.Tooltip("test_mae:Q", title="Test MAE", format=",.1f"),
            alt.Tooltip("test_r2:Q", title="Test R2", format=".3f"),
        ],
    )
    stems = base.mark_rule(color=NEUTRAL, strokeWidth=3).encode(
        x=alt.X(
            "zero:Q",
            title="Test RMSE",
            scale=alt.Scale(domain=[0, 480], nice=False),
        ),
        x2="test_rmse:Q",
    )
    dots = base.mark_circle(size=170, stroke="#FFFFFF", strokeWidth=1.2).encode(
        x=alt.X("test_rmse:Q", scale=alt.Scale(domain=[0, 480], nice=False)),
        color=alt.condition(alt.datum.model == best, alt.value(ORANGE), alt.value(BLUE)),
    )
    return (stems + dots).properties(height=300)


def error_metrics_chart(comparison: pd.DataFrame) -> alt.Chart:
    """Grouped error bars for MAE, test RMSE, and cross-validation RMSE."""

    data = comparison[["model", "test_mae", "test_rmse", "cross_validation_rmse"]].melt(
        "model", var_name="metric", value_name="bike_count_error"
    )
    labels = {"test_mae": "MAE", "test_rmse": "Test RMSE", "cross_validation_rmse": "CV RMSE"}
    data["metric"] = data["metric"].map(labels)
    data["model_label"] = data["model"].map(MODEL_COMPACT_LABELS)
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                "model_label:N",
                title=None,
                sort=list(MODEL_COMPACT_LABELS.values()),
                axis=alt.Axis(labelAngle=0, labelLimit=90, labelOverlap=False),
            ),
            xOffset="metric:N",
            y=alt.Y("bike_count_error:Q", title="Bike count error", scale=alt.Scale(zero=True)),
            color=alt.Color(
                "metric:N",
                title=None,
                scale=alt.Scale(
                    domain=["MAE", "Test RMSE", "CV RMSE"],
                    range=[GOLD, BLUE, PINK],
                ),
                legend=alt.Legend(orient="bottom", direction="horizontal", columns=3),
            ),
            tooltip=[
                alt.Tooltip("model:N", title="Model"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("bike_count_error:Q", title="Error", format=",.1f"),
            ],
        )
        .properties(height=300)
    )


def fit_quality_dumbbell_chart(comparison: pd.DataFrame) -> alt.LayerChart:
    """Training-versus-testing R2 dumbbells that expose overfitting gaps."""

    data = comparison[["model", "training_r2", "testing_r2", "train_test_r2_gap"]].copy()
    data["model_label"] = data["model"].map(MODEL_SHORT_LABELS)
    order = list(data.sort_values("testing_r2", ascending=False)["model_label"])
    base = alt.Chart(data).encode(
        y=alt.Y("model_label:N", title=None, sort=order),
        tooltip=[
            alt.Tooltip("model:N", title="Model"),
            alt.Tooltip("training_r2:Q", title="Training R2", format=".3f"),
            alt.Tooltip("testing_r2:Q", title="Testing R2", format=".3f"),
            alt.Tooltip("train_test_r2_gap:Q", title="Gap", format=".3f"),
        ],
    )
    connector = base.mark_rule(color=NEUTRAL, strokeWidth=4).encode(x=alt.X("testing_r2:Q", title="R2 score", scale=alt.Scale(domain=[0.5, 1.0])), x2="training_r2:Q")
    testing = base.mark_circle(color=BLUE, size=150).encode(x="testing_r2:Q")
    training = base.mark_circle(color=ORANGE, size=150).encode(x="training_r2:Q")
    return (connector + testing + training).properties(height=260)


def weak_spot_heatmap(comparison: pd.DataFrame) -> alt.Chart:
    """Heatmap comparing each model's worst operational segment errors."""

    data = comparison[["model", "worst_hour_mae", "worst_season_mae", "worst_holiday_group_mae", "worst_functioning_day_group_mae"]].melt(
        "model", var_name="weak_spot", value_name="mean_absolute_error"
    )
    labels = {
        "worst_hour_mae": "Worst hour",
        "worst_season_mae": "Worst season",
        "worst_holiday_group_mae": "Worst holiday group",
        "worst_functioning_day_group_mae": "Worst operating group",
    }
    data["weak_spot"] = data["weak_spot"].map(labels)
    data["model_label"] = data["model"].map(MODEL_SHORT_LABELS)
    return (
        alt.Chart(data)
        .mark_rect(cornerRadius=3)
        .encode(
            x=alt.X("weak_spot:N", title=None, sort=list(labels.values()), axis=alt.Axis(labelAngle=-15)),
            y=alt.Y(
                "model_label:N",
                title=None,
                sort=[MODEL_SHORT_LABELS[model] for model in comparison["model"]],
            ),
            color=alt.Color("mean_absolute_error:Q", title="MAE", scale=alt.Scale(scheme="orangered")),
            tooltip=["model:N", "weak_spot:N", alt.Tooltip("mean_absolute_error:Q", title="MAE", format=",.1f")],
        )
        .properties(height=260)
    )


def supply_buffer_chart(scenarios: pd.DataFrame) -> alt.LayerChart:
    """Horizontal lollipop view of operational supply buffer scenarios."""

    data = scenarios.copy()
    data["zero"] = 0.0
    order = list(data["scenario"])
    base = alt.Chart(data).encode(
        y=alt.Y("scenario:N", title=None, sort=order),
        tooltip=["scenario:N", alt.Tooltip("bikes:Q", title="Planned bikes", format=",.0f")],
    )
    stems = base.mark_rule(color=LIGHT_BLUE, strokeWidth=8, opacity=0.65).encode(x=alt.X("zero:Q", title="Bikes"), x2="bikes:Q")
    dots = base.mark_circle(size=190, color=ORANGE, stroke="#FFFFFF", strokeWidth=1.2).encode(x="bikes:Q")
    labels = base.mark_text(align="left", dx=10, fontWeight="bold").encode(x="bikes:Q", text=alt.Text("bikes:Q", format=",.0f"))
    return (stems + dots + labels).properties(height=190)


def demand_profile_chart(profile: pd.DataFrame) -> alt.LayerChart:
    """Interactive 24-hour prediction profile for the current scenario."""

    base = alt.Chart(profile).encode(
        x=alt.X("hour:Q", title="Hour of day", scale=alt.Scale(domain=[0, 23]), axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("predicted_bikes:Q", title="Predicted rented bikes", scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip("hour:Q", title="Hour"), alt.Tooltip("predicted_bikes:Q", title="Predicted bikes", format=",.0f")],
    )
    area = base.mark_area(color=BLUE, opacity=0.2, line=False)
    line = base.mark_line(color=BLUE, strokeWidth=3)
    points = base.mark_circle(color=GOLD, size=75, stroke=BLUE, strokeWidth=1)
    return (area + line + points).properties(height=300).interactive(bind_y=False)


def temperature_sensitivity_chart(sensitivity: pd.DataFrame, selected_temperature: float) -> alt.LayerChart:
    """Model-response curve while all non-temperature inputs stay fixed."""

    base = alt.Chart(sensitivity).encode(
        x=alt.X("temperature_c:Q", title="Temperature (C)"),
        y=alt.Y("predicted_bikes:Q", title="Predicted rented bikes", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("temperature_c:Q", title="Temperature (C)", format=".1f"),
            alt.Tooltip("predicted_bikes:Q", title="Predicted bikes", format=",.0f"),
        ],
    )
    line = base.mark_line(color=PINK, strokeWidth=3)
    points = base.mark_circle(color=GOLD, size=70, stroke=PINK, strokeWidth=1)
    current = alt.Chart(pd.DataFrame({"temperature_c": [selected_temperature]})).mark_rule(color=NEUTRAL, strokeDash=[5, 4]).encode(x="temperature_c:Q")
    return (line + points + current).properties(height=300).interactive(bind_y=False)
