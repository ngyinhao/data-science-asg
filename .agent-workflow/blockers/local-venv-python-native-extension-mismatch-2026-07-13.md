# Local virtual environment mixes Python 3.14 with Python 3.12 extensions

## Context and intended action

After Streamlit Community Cloud logged a native segmentation fault under Python 3.12, the investigation attempted a local direct load of `models/best_model.pkl` with faulthandler enabled to compare the model-loading boundary.

## Observable symptom

The interpreter loaded `pickle.py` from the system Python 3.14 installation while scikit-learn's compiled extension files in `.venv` were tagged `cp312`. Importing scikit-learn failed because `_check_build` could not load the mismatched native module.

## Impact

This local environment cannot provide a trustworthy native-binary comparison for the Cloud segmentation fault until it is rebuilt. It does not affect the already captured Cloud evidence, where dependencies were freshly installed into a Python 3.12.13 environment.

## Confirmed cause

The `.venv` interpreter/runtime and its installed compiled wheels target different Python minor versions (3.14 runtime versus CPython 3.12 extension modules).

## Troubleshooting and workaround

- Confirmed that the installed scikit-learn extension filename is tagged `cp312`.
- Confirmed the traceback uses the Python 3.14 standard library.
- Use the repository's `scripts/rebuild_venv_python312.ps1` before relying on local native-package tests.
- Continue deployment diagnosis from the clean Cloud Python 3.12 install and its owner logs.

## Prevention

After system Python upgrades, recreate `.venv` instead of reusing it. Add a preflight that compares `sys.version_info`, `sys.base_prefix`, and native wheel ABI tags before model validation.
