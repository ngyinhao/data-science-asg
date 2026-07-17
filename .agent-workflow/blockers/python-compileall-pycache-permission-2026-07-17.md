# Python compileall could not update existing bytecode files

## Context and intended action

The Streamlit layout changes were validated with `python -m compileall -q app streamlit_app.py` while the local app server was running.

## Observable symptom

Several modules reported `PermissionError` while attempting to replace files in existing `__pycache__` directories. The same run also surfaced a separate source indentation error.

## Impact

`compileall` could not serve as a clean syntax-validation command in the active Windows environment, even for source files without syntax errors.

## Likely cause

Existing bytecode files or their directories were not writable in the active environment, potentially because of permissions or concurrent use by the running server.

## Troubleshooting and workaround

Use an AST-based validation pass that reads each Python source file and calls `ast.parse` without generating bytecode. This still detects syntax and indentation errors while avoiding `__pycache__` writes.

## Prevention

Prefer a no-bytecode syntax check when validating source during a live local-app session. Reserve `compileall` for an environment where the repository bytecode cache is known to be writable.
