"""Regression tests for prediction-page weather feedback."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import unittest

from app.app_utils import snowfall_effect_feedback
from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SnowfallEffectFeedbackTests(unittest.TestCase):
    def test_nonzero_snowfall_with_unchanged_displayed_prediction_is_explicit(self) -> None:
        feedback = snowfall_effect_feedback(
            snowfall_cm=0.6,
            prediction=1743.2,
            no_snow_prediction=1743.4,
        )

        self.assertEqual(
            feedback,
            (
                "info",
                "Snowfall effect for this scenario: 1,743.20 bikes with 0.6 cm "
                "versus 1,743.40 bikes at 0 cm — 0.20 fewer bikes.",
            ),
        )

    def test_snowfall_reduction_reports_the_displayed_difference(self) -> None:
        feedback = snowfall_effect_feedback(
            snowfall_cm=1.0,
            prediction=1714.2,
            no_snow_prediction=1742.6,
        )

        self.assertEqual(
            feedback,
            (
                "info",
                "Snowfall effect for this scenario: 1,714.20 bikes with 1.0 cm "
                "versus 1,742.60 bikes at 0 cm — 28.40 fewer bikes.",
            ),
        )

    def test_snowfall_increase_reports_the_displayed_difference(self) -> None:
        feedback = snowfall_effect_feedback(
            snowfall_cm=1.0,
            prediction=1747.6,
            no_snow_prediction=1742.6,
        )

        self.assertEqual(
            feedback,
            (
                "info",
                "Snowfall effect for this scenario: 1,747.60 bikes with 1.0 cm "
                "versus 1,742.60 bikes at 0 cm — 5.00 more bikes.",
            ),
        )

    def test_zero_snowfall_has_no_comparison_feedback(self) -> None:
        self.assertIsNone(
            snowfall_effect_feedback(
                snowfall_cm=0.0,
                prediction=1743.0,
                no_snow_prediction=1743.0,
            )
        )


class PredictionPageSnowfallFeedbackTests(unittest.TestCase):
    def test_screenshot_scenario_renders_zero_bike_snowfall_effect(self) -> None:
        app = AppTest.from_file(
            PROJECT_ROOT / "app" / "app_pages" / "prediction.py",
            default_timeout=30,
        ).run(timeout=30)

        self.assertFalse(app.exception)
        app.date_input[0].set_value(date(2027, 1, 14))
        app.slider[1].set_value(15.0)
        app.slider[4].set_value(930)
        app.slider[6].set_value(1.5)
        app.slider[8].set_value(0.6)
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1,743")
        self.assertEqual(
            [message.value for message in app.info],
            [
                "Snowfall effect for this scenario: 1,743.36 bikes with 0.6 cm "
                "versus 1,743.36 bikes at 0 cm — difference 0.00 bikes. "
                "This tree-model scenario is unchanged."
            ],
        )
        self.assertNotIn("usually lowers demand", app.info[0].value)

    def test_snowfall_outside_winter_adds_season_warning(self) -> None:
        app = AppTest.from_file(
            PROJECT_ROOT / "app" / "app_pages" / "prediction.py",
            default_timeout=30,
        ).run(timeout=30)

        app.date_input[0].set_value(date(2026, 8, 27))
        app.slider[8].set_value(5.7)
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertIn("Snowfall effect for this scenario", app.info[0].value)
        self.assertEqual(
            [message.value for message in app.warning],
            [
                "Snowfall is unusual in summer. Check that the selected date and snowfall "
                "amount are correct before using this estimate."
            ],
        )

    def test_rainfall_uses_a_distinct_rain_message(self) -> None:
        app = AppTest.from_file(
            PROJECT_ROOT / "app" / "app_pages" / "prediction.py",
            default_timeout=30,
        ).run(timeout=30)

        app.slider[7].set_value(1.0)
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertEqual(
            [message.value for message in app.info],
            [
                "Rainfall usually lowers bike demand. Consider the wet-weather conditions "
                "when planning bike supply."
            ],
        )
        self.assertNotIn("Snowfall effect", app.info[0].value)

    def test_non_functioning_day_displays_model_prediction(self) -> None:
        app = AppTest.from_file(
            PROJECT_ROOT / "app" / "app_pages" / "prediction.py",
            default_timeout=30,
        ).run(timeout=30)

        app.date_input[0].set_value(date(2027, 1, 14))
        app.slider[1].set_value(15.0)
        app.slider[4].set_value(930)
        app.slider[6].set_value(1.5)
        app.slider[8].set_value(0.6)
        app.segmented_control[1].set_value("No")
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "17")
        self.assertEqual(
            [message.value for message in app.warning],
            [
                "The system is marked as non-functioning. The value shown is the model's "
                "actual prediction for the selected inputs and has not been forced to zero."
            ],
        )


if __name__ == "__main__":
    unittest.main()
