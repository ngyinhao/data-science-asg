# Streamlit docs fails under the Windows console encoding

- **Date:** 2026-07-10
- **Context and intended action:** Inspect the exact Streamlit 1.59.1 signatures and local docstrings with `streamlit docs st.<command>` before implementing a new Streamlit page.
- **Symptom:** The command exits with `UnicodeEncodeError: 'charmap' codec can't encode character` while Click writes the generated documentation.
- **Impact:** The local CLI reference cannot be printed with the default console encoding, interrupting the documented API-discovery workflow. The Streamlit application runtime is not affected.
- **Cause:** The Windows process uses the `cp1252` output encoding, while the generated documentation contains a Unicode symbol that encoding cannot represent.
- **Troubleshooting:** The failure reproduced for API documentation commands launched from the project virtual environment. UTF-8 output successfully printed the full `st.pills` reference. Piping several documentation commands through `Select-Object -First` caused a separate nonzero exit because the downstream command closed the output pipe early; avoid truncating these CLI commands in a batch.
- **Workaround:** Set `PYTHONIOENCODING=utf-8` for the documentation command, then rerun it from the same virtual environment. For a concise signature check, inspect the installed callable directly instead of prematurely closing the CLI output pipe.
- **Prevention:** On Windows, invoke Streamlit documentation commands with UTF-8 process output enabled when the active console encoding is not UTF-8.
