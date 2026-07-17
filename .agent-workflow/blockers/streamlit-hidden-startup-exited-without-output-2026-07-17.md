# Hidden Streamlit startup exited without diagnostics

## Context and intended action

The local Streamlit app was started on port 8501 with PowerShell `Start-Process`, a hidden window, and no output redirection so it could be opened for visual layout review.

## Observable symptom

The process ID was returned, but repeated HTTP checks never reached the app and the readiness command timed out. A follow-up process and port check showed no surviving process or listener, while the hidden launch provided no error output.

## Impact

The website could not be opened until the startup failure was reproduced with visible diagnostic output.

## Likely cause

The Streamlit process exited during initialization. The exact application error was unavailable because the background launch did not capture standard output or standard error.

## Troubleshooting and results

- Started the repository virtual-environment Python with `python -m streamlit run streamlit_app.py` on port 8501.
- Polled `http://localhost:8501` for readiness.
- Confirmed that the returned process ID and port listener were no longer present after the timeout.

## Workaround or remaining limitation

Reproduce the launch in the foreground or redirect output to repository-local diagnostic files before returning to a hidden background process. Once the application error is known, correct or work around it and retry.

## Prevention

For future hidden local-app launches, capture standard output and standard error to explicit repository-local diagnostic files until startup readiness is confirmed, then remove or ignore temporary diagnostics as appropriate.
