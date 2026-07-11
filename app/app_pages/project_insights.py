"""Interactive historical demand-driver analysis for the Seoul bike project."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app_utils import (
    SEASON_ORDER,
    filter_insights_data,
    filtered_data_csv,
    load_prepared_bike_data,
    summarise_demand_insights,
)
from eda_chart_utils import (
    SPARSE_BAND_THRESHOLD,
    VARIABLE_OPTIONS,
    build_variable_chart,
    correlation_heatmap,
    default_functioning_scope,
    hour_season_heatmap,
    hour_season_scale_max,
    hour_season_takeaway,
    sparse_exposure_bands,
    variable_question,
    variable_takeaway,
    variable_unit,
)


VARIABLE_KEY = "insights_variable"
SEASONS_KEY = "insights_seasons"
FUNCTIONING_SCOPE_KEY = "insights_functioning_scope"
FUNCTIONING_SCOPE_OPTIONS = ["Functioning days", "All days", "Not functioning"]


def _sync_scope_to_variable() -> None:
    """Apply the analysis default when the explorer variable changes."""

    variable = str(st.session_state[VARIABLE_KEY])
    st.session_state[FUNCTIONING_SCOPE_KEY] = default_functioning_scope(variable)


def _reset_filters() -> None:
    """Restore every season and the selected variable's population default."""

    st.session_state[SEASONS_KEY] = list(SEASON_ORDER)
    st.session_state[FUNCTIONING_SCOPE_KEY] = default_functioning_scope(
        str(st.session_state[VARIABLE_KEY])
    )


st.session_state.setdefault(VARIABLE_KEY, "Hour")
st.session_state.setdefault(SEASONS_KEY, list(SEASON_ORDER))
st.session_state.setdefault(
    FUNCTIONING_SCOPE_KEY,
    default_functioning_scope(str(st.session_state[VARIABLE_KEY])),
)
if st.session_state[VARIABLE_KEY] == "Functioning-day status":
    st.session_state[FUNCTIONING_SCOPE_KEY] = "All days"


st.title("Project insights")
st.caption(
    "Explore historical associations with hourly rented-bike demand; these comparisons do not prove that a variable causes demand to change."
)

data = load_prepared_bike_data()
headline = summarise_demand_insights(data)

st.subheader("Full-year findings")
st.caption("One row represents one hour, and the target is the number of bikes rented in that hour.")

with st.container(horizontal=True):
    st.metric(
        "Peak mean-demand hour",
        f"{int(headline['peak_hour']):02d}:00",
        border=True,
        help=f"Mean demand: {float(headline['peak_hour_mean']):,.1f} bikes per hour.",
    )
    st.metric(
        "Lowest mean-demand hour",
        f"{int(headline['lowest_hour']):02d}:00",
        border=True,
        help=f"Mean demand: {float(headline['lowest_hour_mean']):,.1f} bikes per hour.",
    )
    st.metric(
        "Highest-demand season",
        str(headline["highest_season"]),
        border=True,
        help=(
            f"Mean demand: {float(headline['highest_season_mean']):,.1f}. "
            f"{headline['lowest_season']} is lowest at {float(headline['lowest_season_mean']):,.1f}."
        ),
    )
    st.metric(
        "Temperature correlation",
        f"{float(headline['temperature_correlation']):+.2f}",
        border=True,
        help="Pearson correlation with hourly rented-bike demand.",
    )

with st.container(horizontal=True):
    st.metric(
        "Dry-hour mean",
        f"{float(headline['dry_hour_mean']):,.0f} bikes",
        border=True,
        help="Hours with exactly 0 mm of rainfall.",
    )
    st.metric(
        "At least 5 mm rain",
        f"{float(headline['heavy_rain_mean']):,.0f} bikes",
        border=True,
        help="Mean demand during hours with rainfall greater than or equal to 5 mm.",
    )
    st.metric(
        "No snow vs snow",
        f"{float(headline['no_snow_mean']):,.0f} vs {float(headline['snow_mean']):,.0f}",
        border=True,
        help="Mean hourly demand with 0 cm of snow compared with any recorded snow.",
    )
    st.metric(
        "Non-functioning mean",
        f"{float(headline['non_functioning_mean']):,.0f} bikes",
        border=True,
        help=f"All {int(headline['non_functioning_rows']):,} non-functioning records have zero rentals.",
    )

with st.container(border=True):
    st.subheader("Explorer filters")
    st.caption(
        "Weather views start with functioning days to avoid mixing operating closures into weather comparisons."
    )
    with st.container(horizontal=True, vertical_alignment="bottom"):
        selected_variable = st.selectbox(
            "Variable",
            VARIABLE_OPTIONS,
            key=VARIABLE_KEY,
            on_change=_sync_scope_to_variable,
            filter_mode="fuzzy",
            help="Type to search or choose any of the twelve required variables.",
        )
        selected_seasons = st.pills(
            "Seasons",
            SEASON_ORDER,
            selection_mode="multi",
            key=SEASONS_KEY,
            help="All seasons are selected by default.",
        )
        functioning_scope = st.segmented_control(
            "Functioning-day population",
            FUNCTIONING_SCOPE_OPTIONS,
            key=FUNCTIONING_SCOPE_KEY,
            required=True,
            disabled=selected_variable == "Functioning-day status",
            help="The functioning-day comparison always uses all days so both groups remain visible.",
        )
        st.button(
            "Reset filters",
            icon=":material/restart_alt:",
            on_click=_reset_filters,
        )

if not selected_seasons:
    st.warning("Select at least one season to display the analysis.", icon=":material/filter_alt:")
    st.stop()

filtered = filter_insights_data(data, list(selected_seasons), str(functioning_scope))
if filtered.empty:
    st.warning(
        "No historical rows match this season and functioning-day combination. Reset or broaden the filters.",
        icon=":material/filter_alt_off:",
    )
    st.stop()

season_population = ", ".join(selected_seasons)
population_description = (
    f"{functioning_scope.lower()} across {season_population}; "
    f"{len(filtered):,} of {len(data):,} hourly records."
)

st.subheader("Individual-variable explorer")
with st.container(border=True):
    st.markdown(f"**{selected_variable}**")
    st.caption(variable_question(str(selected_variable)))
    st.markdown(f"**Active population:** {population_description}")
    st.caption(f"Variable unit: {variable_unit(str(selected_variable))}. Hover for exact values and sample sizes.")
    st.altair_chart(
        build_variable_chart(filtered, str(selected_variable)),
        width="stretch",
    )
    st.markdown(f"**Takeaway:** {variable_takeaway(filtered, str(selected_variable))}")
    sparse_bands = sparse_exposure_bands(filtered, str(selected_variable))
    if sparse_bands:
        st.warning(
            f"Sparse post-filter band{'s' if len(sparse_bands) > 1 else ''} "
            f"(<{SPARSE_BAND_THRESHOLD} hours): {', '.join(sparse_bands)}. Interpret with caution.",
            icon=":material/warning:",
        )
    if selected_variable == "Functioning-day status":
        st.caption(
            "All days are required here: the zero-demand non-functioning records are operationally meaningful and must remain visible beside functioning days."
        )

st.subheader("Combined effects")
with st.container(border=True):
    st.markdown("**Average demand by hour and season**")
    st.caption(
        "At which hour-season combinations is demand highest? The colour scale is fixed to the full-year maximum so filtered views remain comparable."
    )
    st.markdown(f"**Active population:** {population_description}")
    st.altair_chart(
        hour_season_heatmap(filtered, hour_season_scale_max(data)),
        width="stretch",
    )
    st.markdown(f"**Takeaway:** {hour_season_takeaway(filtered)}")

st.subheader("Correlation overview")
with st.container(border=True):
    st.caption(
        "Pearson correlations summarise linear relationships between demand and each of the nine numeric explorer variables. A grey N/A cell means one variable is constant in the active population."
    )
    st.markdown(f"**Active population:** {population_description}")
    st.altair_chart(correlation_heatmap(filtered), width="stretch")
    st.caption("Correlation coefficients range from -1 to +1. Correlation does not prove causation.")

st.subheader("Interpretation and limitations")
with st.container(border=True):
    st.markdown(
        """
        These charts describe historical associations, and several variables can move together. Changing a filter changes the population, so it can also change the apparent relationship.

        Model **feature importance** on the selected-model page describes how the fitted Random Forest uses inputs. The prediction page's **sensitivity curves** describe model response while other inputs are held fixed. Neither those model views nor this EDA page establishes a causal effect.
        """
    )

methodology = st.expander(
    "Methodology and band definitions",
    icon=":material/science:",
    key="insights_methodology",
    on_change="rerun",
)
if methodology.open:
    with methodology:
        st.markdown(
            f"""
            - Continuous weather profiles use full-dataset quantile edges calculated before filtering. Duplicate edges are removed when repeated measurements require it, and the resulting bin definitions stay fixed as filters change.
            - Rainfall bands are: **No rain** (0 mm), **Light rain** (>0 to 1 mm), **Moderate rain** (>1 to 5 mm), and **Heavy rain** (>5 mm). The headline card uses at least 5 mm to remain consistent with the submitted EDA wording.
            - Snowfall bands are: **No snow** (0 cm), **Light snow** (>0 to 1 cm), and **Heavier snow** (>1 cm).
            - Mean is the primary report-consistent measure; median is retained because it is less sensitive to extreme values. Tukey whiskers show the non-outlier spread, the thicker interval shows the middle 50%, and tooltips retain the observed minimum and maximum.
            - Rain or snow bands with fewer than **{SPARSE_BAND_THRESHOLD}** post-filter observations are flagged as sparse.
            """
        )

download = st.expander(
    "Download filtered data",
    icon=":material/download:",
    key="insights_download",
    on_change="rerun",
)
if download.open:
    with download:
        st.caption(
            f"Download the {len(filtered):,} historical rows represented by the active filters. Derived display bins are excluded."
        )
        st.download_button(
            "Download filtered data (CSV)",
            data=filtered_data_csv(filtered),
            file_name="seoul_bike_filtered_data.csv",
            mime="text/csv",
            icon=":material/download:",
            on_click="ignore",
        )
