# Python compileall could not write existing bytecode cache

- **Date:** 2026-07-11
- **Context and intended action:** Run `python -m compileall -q app src` as a final syntax check after changing the Streamlit package imports.
- **Symptom:** `compileall` reported `PermissionError: [Errno 13] Permission denied` for temporary `.pyc` files under the existing `app/__pycache__`, `app/app_pages/__pycache__`, and `src/__pycache__` directories.
- **Impact:** The standard bytecode-writing syntax check could not complete in this managed Windows workspace. Streamlit `AppTest` runs and normal module imports were unaffected.
- **Likely cause:** The managed workspace or an existing process prevented replacement of files inside the existing bytecode-cache directories.
- **Troubleshooting:** The failure affected multiple source files and cache directories, indicating a cache-write constraint rather than a Python syntax error.
- **Workaround:** Compile each tracked Python source in memory with Python's `compile()` built-in, which verifies syntax without writing `.pyc` files. Retain the page-level `AppTest` and project validation runs as runtime checks.
- **Prevention:** In this workspace, prefer an in-memory syntax check when existing `__pycache__` directories may be locked. Only remove cache directories after verifying paths and when cleanup is explicitly necessary.
