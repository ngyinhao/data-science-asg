# Streamlit deployment incident — 2026-07-13

## Reported symptom

The public Streamlit application displayed a device-associated error. Direct testing
showed the public URL returning Streamlit's generic **“Oh no. Error running app”**
screen.

## Investigation results

- The local application started successfully with Python 3.12.10 and Streamlit
  1.59.1.
- The full project validation passed, including model loading, sample prediction,
  prepared-data checks, and chart generation.
- All four pages rendered without a Streamlit exception at desktop width, a 390 px
  phone viewport, and a 320 px narrow-phone viewport.
- No tested mobile page caused horizontal document overflow.
- The public deployment failed before rendering an application page. Streamlit
  Community Cloud suppresses server exception details on the public error screen;
  the full traceback is available only in the app-management logs.

## Issues identified

1. **Public deployment is unavailable.** This is an environment or startup-path
   failure, not a responsive-layout failure.
2. **The repository lacked the conventional root launcher.** Only
   `app/streamlit_app.py` existed. A Community Cloud app configured for the common
   `streamlit_app.py` root path would fail before the app could run.
3. **Transient Vega warnings occur during first paint.** The browser briefly logged
   infinite-extent warnings while chart data was arriving, but every chart rendered
   with finite dimensions after initialization. No blank chart or user-visible error
   was reproduced, so these warnings are recorded as non-blocking rather than treated
   as the deployment cause.

## Fix applied

- Added a root `streamlit_app.py` that defines navigation directly and loads page
  implementations from `app/app_pages`.
- Kept `app/streamlit_app.py` intact so existing local and cloud configurations remain
  compatible.
- Updated project validation to require the deployment launcher.
- Updated the README to recommend `streamlit_app.py` for local and Community Cloud
  startup.

## Cloud follow-up

- Owner access confirmed that the existing deployment correctly targets
  `main/app/streamlit_app.py`; the missing root launcher was a resilience gap but not
  the active deployment path.
- Community Cloud was configured for Python 3.14 even though the project runtime is
  Python 3.12. The setting was changed to Python 3.12 and the app was rebooted.
- The clean Python 3.12.13 rebuild installed all pinned dependencies, started Uvicorn,
  and then terminated the Streamlit process with a native segmentation fault.
- The selected Random Forest had been serialized with `n_jobs=-1`, and the prediction
  page invoked it repeatedly during initial rendering. Model loading now forces
  single-worker inference, and scenario profiles are predicted in two batches instead
  of 41 separate calls to avoid native thread-pool pressure in the constrained Cloud
  runtime.

## Verification and remaining owner action

Both entry points must pass local startup and page checks before this incident is
closed. After the change is pushed, Community Cloud should redeploy automatically.
If the public page still fails, open **Manage app**, download the owner-only log, and
use its first Python traceback or dependency-install error as the authoritative next
diagnostic. Confirm that the deployment coordinates are repository `main` with main
file path `streamlit_app.py` and Python 3.12.

## Final hosted verification

Community Cloud remains configured for its existing `app/streamlit_app.py` entry
point on `main`, with Python 3.12. After commit `ad051e4` and a full worker reboot:

- the public URL rendered the **Prediction** page,
- the prediction result section was present,
- all three expected Vega charts rendered, and
- no Streamlit exception element was present.

The hosted application is operational at
<https://data-science-asg.streamlit.app/>.
