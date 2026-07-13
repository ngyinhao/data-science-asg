# Imported Streamlit navigation renders a blank page

## Context and intended action

A conventional root `streamlit_app.py` launcher initially delegated to the existing application with `from app.streamlit_app import *`. The goal was to preserve one navigation implementation while supporting a root Community Cloud entry point.

## Observable symptom

`streamlit run streamlit_app.py` served the Streamlit header but no page title, controls, charts, or exception. `AppTest` also reported zero exceptions, so the issue was only visible in a real browser-backed runtime.

## Impact

The initial compatibility launcher was unusable and could have replaced the public startup error with a blank application.

## Confirmed cause

The `st.navigation(...).run()` call was executed inside an imported module rather than directly in the script Streamlit registered as its entry point. Streamlit did not render the selected page body through that imported navigation boundary.

## Troubleshooting and workaround

- Confirmed the original `app/streamlit_app.py` entry point rendered correctly.
- Confirmed the import-based root launcher rendered only the Streamlit shell.
- Define `st.set_page_config`, `st.navigation`, and `page.run()` directly in the root entry-point script, using absolute page paths under `app/app_pages`.

## Prevention

Do not implement a Streamlit multipage launcher by importing another script that immediately calls `page.run()`. Validate entry-point changes with a real Streamlit server and browser, not only `AppTest` or compilation.
