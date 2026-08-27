"""Prediction page for the Seoul Bike Supply Planner."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.app_utils import (
    build_input_frame,
    load_metadata,
    load_model,
    season_for_month,
    snowfall_effect_feedback,
)
from app.chart_utils import (
    ocr_chart,
    supply_buffer_chart,
)


st.title("Prediction")
st.caption("Estimate hourly rented-bike demand from time, weather, season, holiday, and operating status.")

metadata = load_metadata()
model = load_model()

st.badge(f"Prediction model: {metadata['selected_model']}", icon=":material/check:", color="green")

with st.container(border=True):
    st.subheader("Demand inputs")
    calendar_col, weather_col, conditions_col = st.columns(3, gap="medium")

    with calendar_col:
        hour = st.slider("Hour", 0, 23, 18)
        selected_date = st.date_input(
            "Date",
            value=date.today(),
            format="DD/MM/YYYY",
            help="Month, day, weekday, weekend status, and season are derived from this date.",
        )
        month = selected_date.month
        day = selected_date.day
        weekday = selected_date.weekday()
        is_weekend = 1 if weekday in [5, 6] else 0
        seasons = season_for_month(month)
        weekday_label = selected_date.strftime("%A")
        st.caption(f"Derived calendar context: {weekday_label} · {seasons}")
        holiday = st.segmented_control("Holiday", ["No Holiday", "Holiday"], default="No Holiday")
        functioning_day = st.segmented_control("Functioning day", ["Yes", "No"], default="Yes")

    with weather_col:
        temperature_c = st.slider("Temperature (C)", -20.0, 40.0, 24.0, 0.5)
        humidity_pct = st.slider("Humidity (%)", 0, 100, 55)
        wind_speed_m_per_s = st.slider("Wind speed (m/s)", 0.0, 8.0, 1.5, 0.1)
        visibility_10m = st.slider("Visibility (10m)", 0, 2000, 1500, 10)

    with conditions_col:
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
snowfall_feedback = None
if snowfall_cm > 0 and functioning_day == "Yes":
    no_snow_input_frame = input_frame.copy()
    no_snow_input_frame.loc[0, "snowfall_cm"] = 0.0
    no_snow_prediction = max(float(model.predict(no_snow_input_frame)[0]), 0)
    snowfall_feedback = snowfall_effect_feedback(
        snowfall_cm=snowfall_cm,
        prediction=prediction,
        no_snow_prediction=no_snow_prediction,
    )

result_col, chart_col = st.columns([0.8, 1.2], gap="large")

with result_col:
    with st.container(border=True, height="stretch"):
        st.metric("Predicted rented bikes", f"{prediction:,.0f}")

        if functioning_day == "No":
            st.warning(
                "The system is marked as non-functioning. The value shown is the model's "
                "actual prediction for the selected inputs and has not been forced to zero.",
                icon=":material/warning:",
            )
        else:
            weather_message_displayed = False

            if snowfall_feedback is not None:
                feedback_level, feedback_message = snowfall_feedback
                getattr(st, feedback_level)(
                    feedback_message,
                    icon=":material/ac_unit:",
                )
                weather_message_displayed = True

                if seasons != "Winter":
                    st.warning(
                        f"Snowfall is unusual in {seasons.lower()}. Check that the selected "
                        "date and snowfall amount are correct before using this estimate.",
                        icon=":material/calendar_month:",
                    )

            if rainfall_mm > 0:
                rain_intensity = "Heavy rainfall" if rainfall_mm >= 5 else "Rainfall"
                st.info(
                    f"{rain_intensity} usually lowers bike demand. Consider the wet-weather "
                    "conditions when planning bike supply.",
                    icon=":material/water_drop:",
                )
                weather_message_displayed = True

            if not weather_message_displayed:
                if hour in [8, 17, 18, 19] and temperature_c >= 10:
                    st.success(
                        "This looks like a likely peak-demand situation. Prepare extra bike "
                        "supply around busy stations.",
                        icon=":material/trending_up:",
                    )
                else:
                    st.info(
                        "Use this estimate with current station inventory before deciding "
                        "relocation volume.",
                        icon=":material/info:",
                    )

with chart_col:
    with st.container(border=True, height="stretch"):
        st.subheader("Supply buffer view")
        chart_frame = pd.DataFrame(
            {
                "scenario": ["Current estimate", "10% buffer", "20% buffer"],
                "bikes": [prediction, prediction * 1.1, prediction * 1.2],
            }
        )
        st.caption("Lollipop markers show the current estimate and two practical stock buffers.")
        st.altair_chart(ocr_chart(supply_buffer_chart(chart_frame)), width="stretch")

st.caption(
    "This page gives one operational estimate for the selected date and hour. "
    "Use Project insights for broader historical demand patterns."
)
