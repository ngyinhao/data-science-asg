"""Prediction page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.app_utils import build_input_frame, load_metadata, load_model
from app.chart_utils import demand_profile_chart, supply_buffer_chart, temperature_sensitivity_chart


st.title("Prediction")
st.caption("Estimate hourly rented-bike demand from time, weather, season, holiday, and operating status.")

metadata = load_metadata()
model = load_model()

st.badge(f"Prediction model: {metadata['selected_model']}", icon=":material/check:", color="green")

with st.container(border=True):
    st.subheader("Demand inputs")
    left, right = st.columns(2, gap="large")

    with left:
        hour = st.slider("Hour", 0, 23, 18)
        month = st.slider("Month", 1, 12, 7)
        day = st.slider("Day", 1, 31, 15)
        weekday = st.selectbox(
            "Weekday",
            options=list(range(7)),
            format_func=lambda x: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][x],
            index=4,
        )
        is_weekend = 1 if weekday in [5, 6] else 0
        seasons = st.selectbox("Season", ["Spring", "Summer", "Autumn", "Winter"], index=1)
        holiday = st.segmented_control("Holiday", ["No Holiday", "Holiday"], default="No Holiday")
        functioning_day = st.segmented_control("Functioning day", ["Yes", "No"], default="Yes")

    with right:
        temperature_c = st.slider("Temperature (C)", -20.0, 40.0, 24.0, 0.5)
        humidity_pct = st.slider("Humidity (%)", 0, 100, 55)
        wind_speed_m_per_s = st.slider("Wind speed (m/s)", 0.0, 8.0, 1.5, 0.1)
        visibility_10m = st.slider("Visibility (10m)", 0, 2000, 1500, 10)
        dew_point_temperature_c = st.slider("Dew point temperature (C)", -30.0, 30.0, 14.0, 0.5)
        solar_radiation_mj_per_m2 = st.slider("Solar radiation (MJ/m2)", 0.0, 4.0, 0.6, 0.1)
        rainfall_mm = st.slider("Rainfall (mm)", 0.0, 40.0, 0.0, 0.1)
        snowfall_cm = st.slider("Snowfall (cm)", 0.0, 10.0, 0.0, 0.1)

input_frame = build_input_frame(
    {
        "hour": hour,
        "temperature_c": temperature_c,
        "humidity_pct": humidity_pct,
        "wind_speed_m_per_s": wind_speed_m_per_s,
        "visibility_10m": visibility_10m,
        "dew_point_temperature_c": dew_point_temperature_c,
        "solar_radiation_mj_per_m2": solar_radiation_mj_per_m2,
        "rainfall_mm": rainfall_mm,
        "snowfall_cm": snowfall_cm,
        "month": month,
        "day": day,
        "weekday": weekday,
        "is_weekend": is_weekend,
        "seasons": seasons,
        "holiday": holiday,
        "functioning_day": functioning_day,
    }
)

prediction = max(float(model.predict(input_frame)[0]), 0)

result_col, chart_col = st.columns([0.8, 1.2], gap="large")

with result_col:
    st.metric("Predicted rented bikes", f"{prediction:,.0f}", border=True)

    if functioning_day == "No":
        st.warning(
            "The system is marked as non-functioning. Interpret this as a closure or near-zero demand scenario.",
            icon=":material/warning:",
        )
    elif rainfall_mm >= 5 or snowfall_cm > 0:
        st.info(
            "Wet or snowy weather usually lowers demand, so supply can be planned more conservatively.",
            icon=":material/water_drop:",
        )
    elif hour in [8, 17, 18, 19] and temperature_c >= 10:
        st.success(
            "This looks like a likely peak-demand situation. Prepare extra bike supply around busy stations.",
            icon=":material/trending_up:",
        )
    else:
        st.info(
            "Use this estimate with current station inventory before deciding relocation volume.",
            icon=":material/info:",
        )

with chart_col:
    with st.container(border=True):
        st.subheader("Supply buffer view")
        chart_frame = pd.DataFrame(
            {
                "scenario": ["Current estimate", "10% buffer", "20% buffer"],
                "bikes": [prediction, prediction * 1.1, prediction * 1.2],
            }
        )
        st.caption("Lollipop markers show the current estimate and two practical stock buffers.")
        st.altair_chart(supply_buffer_chart(chart_frame), width="stretch")

st.subheader("Interactive scenario analysis")
st.caption("These views hold the other inputs constant, so they describe the model's response—not a causal effect.")

profile_rows = []
for profile_hour in range(24):
    profile_input = input_frame.copy()
    profile_input.loc[0, "hour"] = profile_hour
    profile_rows.append(
        {"hour": profile_hour, "predicted_bikes": max(float(model.predict(profile_input)[0]), 0)}
    )
hourly_profile = pd.DataFrame(profile_rows)

temperature_rows = []
for profile_temperature in range(-15, 36, 3):
    temperature_input = input_frame.copy()
    temperature_input.loc[0, "temperature_c"] = float(profile_temperature)
    temperature_rows.append(
        {
            "temperature_c": float(profile_temperature),
            "predicted_bikes": max(float(model.predict(temperature_input)[0]), 0),
        }
    )
temperature_profile = pd.DataFrame(temperature_rows)

profile_col, sensitivity_col = st.columns(2, gap="large")
with profile_col:
    with st.container(border=True):
        st.subheader("Demand across the day")
        st.caption("Predicted demand by hour for the selected date, weather, season, and operating status.")
        st.altair_chart(demand_profile_chart(hourly_profile), width="stretch")

with sensitivity_col:
    with st.container(border=True):
        st.subheader("Temperature response")
        st.caption("Predicted demand across temperature scenarios; the dashed line marks the selected temperature.")
        st.altair_chart(
            temperature_sensitivity_chart(temperature_profile, temperature_c),
            width="stretch",
        )
