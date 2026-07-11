# Streamlit hot reload retained a previously imported chart module

- **Date:** 2026-07-10
- **Context and intended action:** Recheck a mobile correlation-chart fix in the already running local Streamlit QA server.
- **Symptom:** Reloading the browser continued to show the previous 10-by-10 matrix even though the current module generated a validated nine-row chart specification.
- **Impact:** Browser QA was temporarily testing stale imported code rather than the patched source.
- **Likely cause:** The active Streamlit process retained the imported helper module for this change instead of invalidating it during the rerun.
- **Troubleshooting:** A fresh Python process imported the same local file and produced one dataset with nine rows and the new 360-pixel chart height, confirming the source patch itself was correct.
- **Workaround:** Restart the temporary Streamlit server, then reload the local page before repeating visual QA.
- **Prevention:** After changing an imported Streamlit helper during visual QA, verify a distinctive spec property; restart the local server when the browser and a fresh-process import disagree.

## Recurrence: project-insights import failure (2026-07-11)

- **Context and intended action:** Open the newly deployed `Project insights` page through `st.navigation` on Streamlit Community Cloud.
- **Observable symptom:** `page.run()` failed while executing `app/app_pages/project_insights.py`; the visible traceback stopped at the multi-line `from app_utils import (...)` statement. The copied traceback did not include the terminal exception type or message.
- **Impact:** The Project insights page could not render in the deployed app.
- **Evidence:** In a fresh local Python 3.12 / Streamlit 1.59.1 process, every requested symbol existed in `app_utils`, the module imported successfully, and a direct `AppTest` run of the page reported zero exceptions. This is consistent with a stale or ambiguously resolved top-level module in the long-running deployment process, although the omitted terminal exception prevents definitive confirmation.
- **Recovery implemented:** Converted Streamlit helpers and pages into explicit packages (`app.*` and `src.*`) and changed page bootstrapping to add the repository root to `sys.path`. The new qualified module names avoid collisions with generic top-level names and force a fresh module namespace on deployment. All four page-level `AppTest` runs, the navigation entrypoint test, and `src/validate_project.py` then passed from a working directory outside the repository.
- **Remaining limitation:** The cloud app must redeploy or restart to load the changed modules. If the problem recurs, capture the final exception line and reboot the Streamlit app before deeper diagnosis.
- **Prevention:** Prefer qualified package imports for shared Streamlit modules. After deploying changes to imported helpers, restart the app if the page traceback disagrees with a fresh-process import test.
