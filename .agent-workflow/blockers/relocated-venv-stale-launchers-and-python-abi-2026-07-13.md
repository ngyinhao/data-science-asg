# Relocated virtual environment retained stale launchers and Python ABI artifacts

## Context and intended action

After moving the repository from a OneDrive directory to `C:\Dev\data-science-asg`, the local Streamlit launcher was run from a newly activated `.venv`. The intended action was to install `requirements.txt` and start the app.

## Observable symptoms

- Running `pip install -r requirements.txt` failed because `.venv\Scripts\pip.exe` attempted to launch Python from the repository's former OneDrive location.
- `scripts\run_streamlit.ps1` reported that Python dependencies could not be imported.
- Directly importing the dependency set with `.venv\Scripts\python.exe` showed Python 3.14 loading NumPy extension files tagged for CPython 3.12 (`*.cp312-win_amd64.pyd`), followed by `No module named 'numpy._core._multiarray_umath'`.

## Impact

The local virtual environment cannot reliably install or import dependencies, so the Streamlit app cannot start through the repository launcher. This does not by itself affect a clean remote deployment that creates its own environment from `requirements.txt`.

## Cause

Python virtual environments are not portable across directory moves. Their generated executables contain absolute paths. In addition, running `python -m venv .venv` over an existing environment does not guarantee removal of stale executables or compiled packages. Here it left an old `pip.exe` launcher and CPython 3.12 binary extensions while updating the environment to Python 3.14.

## Troubleshooting and results

- Inspected `.venv\pyvenv.cfg`: it identified the current base interpreter as Python 3.14 and the current repository path.
- Ran `.venv\Scripts\python.exe -m pip --version`: module-based pip worked and resolved inside the current `.venv`, proving that the standalone `pip.exe` failure was launcher-specific.
- Ran the launcher's dependency import directly: it exposed the CPython 3.12 versus 3.14 NumPy ABI mismatch hidden by the PowerShell script's redirected output.
- Inspected `requirements.txt`: it contains package/version pins and no local absolute paths.
- Checked installed interpreters: the Windows `py` launcher was unavailable, but `python3.12` resolved to Python 3.12.10. The repository's rebuild script already falls back from `py -3.12` to `python3.12`, so the missing launcher does not block recovery.

## Workaround / resolution

Use the repository's guarded Python 3.12 rebuild script, which verifies the target path before deleting `.venv`, recreates it, installs with interpreter-bound pip, and checks imports:

```powershell
deactivate
.\scripts\rebuild_venv_python312.ps1
.\.venv\Scripts\Activate.ps1
.\scripts\run_streamlit.ps1
```

The script selects the installed `python3.12` fallback when the Windows `py` launcher is absent. Use Python 3.12 consistently for this project rather than overlaying Python 3.14 onto packages built for Python 3.12.

## Prevention

- Exclude `.venv/` from source control and never move or copy it with the repository.
- Delete and recreate `.venv` after moving a project or changing Python minor versions.
- Prefer `python -m pip` so pip is tied to the active interpreter instead of a potentially stale Windows launcher.
- Pin the deployment Python version separately from package dependencies; `requirements.txt` does not select the Python runtime.

## Recurrence: standalone test diagnosis (2026-07-15)

- **Context:** Attempted to reproduce `test/preprocess.py` without modifying the unrelated project environment.
- **Symptom:** The installed `python3.12` executable starts successfully but raises `ModuleNotFoundError: No module named 'pandas'` when importing the plotting script's dependencies.
- **Impact:** The system Python 3.12 installation cannot directly execute the test script, while the repository `.venv` remains unsuitable because of the ABI mismatch documented above.
- **Workaround:** Use a separate already-provisioned runtime if available, or perform read-only CSV diagnostics with tools that do not depend on the broken environment. Avoid installing packages or rebuilding `.venv` for an unrelated test unless the user explicitly requests environment repair.
- **Additional evidence:** The Codex bundled Python runtime can import `pandas` but not `matplotlib` (`ModuleNotFoundError`), so it can support numerical CSV analysis but cannot directly render the original chart.
- **Additional evidence:** `pandas.Series.corr(method="spearman")` also fails in that bundled runtime because it imports the absent optional `scipy` package. An equivalent dependency-free workaround for untied/tied numeric data is `x.rank().corr(y.rank())`.
