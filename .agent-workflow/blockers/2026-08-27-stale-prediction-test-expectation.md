# Stale prediction test expectation

- **Context:** Reproducing prediction-page behavior with the existing regression suite.
- **Intended action:** Run `python -m unittest tests.test_prediction_feedback -v` as the feedback loop.
- **Symptom:** The Streamlit integration test expected `1,743`, but the checked-in model returned `1,608` for the same inputs.
- **Impact:** The existing test failed for an outdated exact prediction before the new behavior assertions were evaluated.
- **Likely cause:** The serialized model artifact changed without updating the model-coupled expected value in the UI test.
- **Resolution:** Update the expected value to match the checked-in artifact while retaining behavioral assertions.
- **Prevention:** Avoid fixed model outputs in UI tests unless that exact value is the behavior under test, or update fixtures whenever the serialized model changes.

## Recurrence after rebase — 2026-08-27

- Rebasing onto the latest `origin/main` replaced the local model artifact with the remote version.
- The snowfall scenario changed from `1,608` back to `1,743`, and the non-functioning scenario changed from `15` to `17`.
- The message behavior remained correct; only the model-coupled exact outputs failed.
- Refresh the two expected outputs against the rebased artifact, amend the commit, and rerun the full suite before pushing.
