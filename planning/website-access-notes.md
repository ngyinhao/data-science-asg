# Website Access Notes

This note records the exact local path and method used to open and inspect the Streamlit website for the Seoul Bike project.

## Main app entry

- App file: `app/streamlit_app.py`
- Full path: `C:\Users\ngyh\OneDrive\TARUMT\Degree Y2S1\DATA SCIENCE\Assignment\app\streamlit_app.py`

## Preferred launcher

- Script file: `scripts/run_streamlit.ps1`
- Full path: `C:\Users\ngyh\OneDrive\TARUMT\Degree Y2S1\DATA SCIENCE\Assignment\scripts\run_streamlit.ps1`

This is the preferred way to reopen the website because it already sets the project root and the Streamlit environment values.

## Local website address

- URL: `http://127.0.0.1:8501`

If `127.0.0.1` does not respond, the equivalent local address is usually:

- `http://localhost:8501`

## Exact method used

1. Go to the project root:
   - `C:\Users\ngyh\OneDrive\TARUMT\Degree Y2S1\DATA SCIENCE\Assignment`
2. Start the launcher script:
   - `powershell -ExecutionPolicy Bypass -File scripts\run_streamlit.ps1`
3. Open the local website:
   - `http://127.0.0.1:8501`

## Direct fallback method

If the PowerShell launcher is not used, the app can be started directly from the project root with:

- `.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false`

## Screenshot path used

The latest clean screenshot of the running site was saved here:

- `tmp/website_screenshot_clean.png`
- Full path: `C:\Users\ngyh\OneDrive\TARUMT\Degree Y2S1\DATA SCIENCE\Assignment\tmp\website_screenshot_clean.png`

## What this path is for

Use this same launcher and URL when we need to:

- reopen the website,
- verify current UI behavior,
- take another screenshot,
- compare the live app with the report preview.
