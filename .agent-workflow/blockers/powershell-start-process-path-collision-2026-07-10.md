# PowerShell Start-Process fails on inherited Path key collision

- **Date:** 2026-07-10
- **Context and intended action:** Start the local Streamlit server in a hidden background process for browser-based visual QA.
- **Symptom:** `Start-Process` failed before launch with `Item has already been added. Key in dictionary: 'Path' Key being added: 'PATH'`.
- **Impact:** The requested local server did not start through PowerShell's detached-process path.
- **Likely cause:** The managed Windows environment exposes differently cased `Path`/`PATH` entries, and Windows PowerShell builds a case-insensitive environment dictionary for `Start-Process`.
- **Troubleshooting:** The exception occurred inside `Start-Process`; there was no Streamlit process or application error to diagnose.
- **Workaround:** Run Streamlit as a managed long-running shell command, retain its execution cell while testing, and terminate that cell after QA.
- **Prevention:** Avoid `Start-Process` in this managed Windows environment until environment-key normalization is guaranteed; prefer the execution tool's lifecycle management for temporary local servers.

