# Streamlit hot reload retained a previously imported chart module

- **Date:** 2026-07-10
- **Context and intended action:** Recheck a mobile correlation-chart fix in the already running local Streamlit QA server.
- **Symptom:** Reloading the browser continued to show the previous 10-by-10 matrix even though the current module generated a validated nine-row chart specification.
- **Impact:** Browser QA was temporarily testing stale imported code rather than the patched source.
- **Likely cause:** The active Streamlit process retained the imported helper module for this change instead of invalidating it during the rerun.
- **Troubleshooting:** A fresh Python process imported the same local file and produced one dataset with nine rows and the new 360-pixel chart height, confirming the source patch itself was correct.
- **Workaround:** Restart the temporary Streamlit server, then reload the local page before repeating visual QA.
- **Prevention:** After changing an imported Streamlit helper during visual QA, verify a distinctive spec property; restart the local server when the browser and a fresh-process import disagree.

