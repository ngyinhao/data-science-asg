# Python compileall cannot update existing pycache files

## Context

On 2026-08-24, `python -m compileall -q app` was used to syntax-check a small Streamlit page edit.

## Observable symptom

Compilation reported `PermissionError: [Errno 13] Permission denied` for temporary `.pyc` paths beneath existing `app/__pycache__` and `app/app_pages/__pycache__` directories.

## Impact

The normal `compileall` verification could not complete because it attempted to write bytecode. The application source edit itself was unaffected.

## Likely cause

The current managed workspace permits source edits but the existing bytecode cache files or directories are not writable in this execution context, possibly because of inherited permissions or another process holding them.

## Troubleshooting and workaround

- `git diff --check` completed without source-format errors.
- Use Python's built-in `compile(source_text, filename, "exec")` on each changed file to validate syntax without writing `.pyc` files.
- Avoid deleting existing cache directories merely to run verification.

## Prevention

For read-only or managed workspaces, prefer an in-memory syntax check for small edits. Use `compileall` only when bytecode-cache directories are known to be writable.
