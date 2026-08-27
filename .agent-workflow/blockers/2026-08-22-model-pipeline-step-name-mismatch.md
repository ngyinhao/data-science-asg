# Diagnostic assumed the wrong model pipeline step name

- **Date:** 2026-08-22
- **Context / intended action:** Inspect the fitted snowfall transformation and Random Forest splits in `models/best_model.pkl`.
- **Observed symptom:** The diagnostic failed with `KeyError: 'preprocessor'` when accessing `model.named_steps`.
- **Impact:** Internal model inspection stopped before producing evidence.
- **Cause:** The training pipeline names the preprocessing step `preprocess`, while the initial diagnostic assumed `preprocessor`.
- **Troubleshooting:** Searched the training source and confirmed `make_model_pipeline()` registers `("preprocess", make_preprocessor())`.
- **Workaround:** Read pipeline step names from the training definition or print `named_steps` before addressing a step by name; use `model.named_steps["preprocess"]` for this artifact.
- **Prevention:** Reuse a shared step-name constant or access the preprocessing step through a small model-introspection helper.
