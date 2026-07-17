# Windows Python launcher unavailable

- **Date:** 2026-07-15
- **Context and intended action:** Enumerate installed Python interpreters with `py -0p` while diagnosing a virtual environment that unexpectedly runs Python 3.14.
- **Observable symptom:** PowerShell reports that `py` is not recognized as a cmdlet, function, script file, or executable.
- **Impact:** Commands such as `py -3.13 -m venv .venv` cannot be used until the launcher is installed or restored to `PATH`.
- **Likely cause:** The Windows Python Launcher is absent or its installation directory is not on `PATH`.
- **Troubleshooting performed:** Confirmed the repository virtual environment itself runs through `.venv\Scripts\python.exe`; attempted `py -0p`, which failed consistently.
- **Workaround:** Locate a specific Python executable with `Get-Command python -All` and known installation directories, then invoke that full path with `-m venv`.
- **Prevention:** Install the Windows Python Launcher when installing Python, verify `py -0p` after installation, and document the project's required Python version (for example in `.python-version` or setup instructions).

## Tool orchestration note

The failed `py -0p` call was initially grouped with independent diagnostics. Because one promise rejected, the orchestration wrapper did not return successful sibling outputs. Run diagnostics that may legitimately fail in separate calls or catch each result individually.
