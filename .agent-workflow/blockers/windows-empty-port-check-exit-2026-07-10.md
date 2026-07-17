# Empty Streamlit port check returns a nonzero status

## Recurrence on 2026-07-17

- A combined syntax, `git diff --check`, and `Get-NetTCPConnection -ErrorAction SilentlyContinue` verification again exited with status 1 after the syntax check succeeded and `git diff --check` reported only its usual line-ending warning.
- The listener query produced no row or diagnostic, making it the status-producing segment and preventing the combined command from being treated as a clean validation.
- Continue with a separate browser request or `netstat` check, and keep listener discovery out of a combined pass/fail validation command unless its empty result is explicitly normalized.

- **Date:** 2026-07-10
- **Context and intended action:** Check whether a local Streamlit server was already listening on ports 8500-8599 before starting visual QA.
- **Symptom:** A `Get-NetTCPConnection` query with no matching listener produced no output but the shell command returned exit code 1.
- **Impact:** The first listener check could not distinguish a normal empty result from a suppressed cmdlet problem.
- **Likely cause:** The PowerShell networking query or its empty filtered result propagated a nonzero status while errors were hidden with `-ErrorAction SilentlyContinue`.
- **Troubleshooting:** No listener details were returned, so a second diagnostic is required before concluding the port is free.
- **Workaround:** Confirm with `netstat` filtering, which cleanly exposes matching listeners without suppressing the original diagnostic context.
- **Prevention:** Use a listener check that explicitly normalizes “no matches” to a successful result and reports an empty list.
