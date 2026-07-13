# Streamlit Cloud process segfaults after startup

## Context and intended action

The Community Cloud runtime was corrected from Python 3.14 to Python 3.12 and rebooted to restore the public Seoul bike application.

## Observable symptom

Cloud logs show a clean repository clone, successful installation of all 57 pinned packages in Python 3.12.13, and `Uvicorn server started on :::8501`. Immediately afterward, `/app/scripts/run-streamlit.sh` reports that the Streamlit process terminated with `Segmentation fault` and no Python traceback.

## Impact

The public application remains unavailable even though dependency resolution and server startup succeed. The failure occurs in native code and bypasses normal Streamlit exception rendering.

## Likely cause

A compiled scientific dependency or serialized model-loading path is crashing during the first page execution. The leading boundary is initial loading of the scikit-learn Random Forest pipeline; further isolation or dependency pinning is required.

## Troubleshooting so far

- Changed Cloud Python from unsupported project runtime 3.14 to the locally intended 3.12.
- Rebooted and confirmed Cloud actually uses Python 3.12.13.
- Confirmed all pinned packages install successfully.
- Captured the native termination after Uvicorn startup.

## Remaining work

Isolate whether the crash occurs before or during `joblib.load(models/best_model.pkl)`, then remove the incompatible native boundary or pin a known-compatible Linux wheel set. Reboot and verify the public Prediction page after each evidence-based change.
