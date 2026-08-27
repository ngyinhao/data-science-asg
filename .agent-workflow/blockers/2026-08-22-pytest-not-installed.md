# Pytest is not installed in the project environment

- **Date:** 2026-08-22
- **Context / intended action:** Add a focused regression test for misleading snowfall feedback on the Streamlit prediction page.
- **Observed symptom:** `.venv\Scripts\python.exe -m pytest --version` failed with `No module named pytest`.
- **Impact:** The usual pytest feedback loop is unavailable without changing project dependencies.
- **Cause:** The repository environment does not include pytest.
- **Troubleshooting:** Confirmed the project also had no conventional test suite; consulted the existing `repository-tests-directory-missing-2026-07-17.md` incident.
- **Workaround:** Use Python's built-in `unittest` framework and runner for the focused regression test.
- **Prevention:** Add a documented test dependency and standard test command if the project adopts a broader automated test suite.

## Recurrence: 2026-08-27

- **Context:** Verify that non-functioning-day predictions display the model output instead of a hard-coded zero.
- **Observed symptom:** `.venv\Scripts\python.exe -m pytest tests\test_prediction_feedback.py -q` again failed with `No module named pytest`.
- **Result:** Reused the documented workaround and ran the focused test module with the standard-library `unittest` runner.
