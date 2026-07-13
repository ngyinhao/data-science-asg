"""Deployment-compatible entry point for the Seoul bike Streamlit app."""

from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent / "app"

st.set_page_config(
    page_title="Seoul Bike Supply Planner",
    page_icon=":material/pedal_bike:",
    layout="wide",
)

page = st.navigation(
    [
        st.Page(
            APP_DIR / "app_pages" / "prediction.py",
            title="Prediction",
            icon=":material/query_stats:",
        ),
        st.Page(
            APP_DIR / "app_pages" / "project_insights.py",
            title="Project insights",
            icon=":material/insights:",
        ),
        st.Page(
            APP_DIR / "app_pages" / "model_comparison.py",
            title="Model comparison",
            icon=":material/bar_chart:",
        ),
        st.Page(
            APP_DIR / "app_pages" / "chosen_model.py",
            title="Why this model was chosen",
            icon=":material/check_circle:",
        ),
    ],
    position="top",
)

page.run()
