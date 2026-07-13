# Streamlit dashboard reboot click timed out

## Context and intended action

After Cloud hot-updated a previously crashed worker, the deployment dashboard needed a full reboot so the newly pushed inference fix would run in a fresh Python 3.12 process.

## Observable symptom

Browser automation located the deployment row and opened its menu, but clicking the `Reboot` action timed out while waiting for a browser evaluation command. No confirmation dialog was submitted.

## Impact

The intended reboot was not confirmed in that attempt. The deployment configuration and repository were unchanged.

## Likely cause

The Streamlit dashboard rerendered or the Chrome control connection briefly stalled between opening the menu and clicking its action.

## Workaround

Take a fresh DOM snapshot, rebuild the locator from the visible menu state, verify uniqueness, and retry once. Do not reuse the timed-out locator without refreshing page evidence.

## Prevention

Keep dashboard interactions short and state-based. After opening a transient menu, capture a fresh snapshot immediately before selecting a destructive or disruptive action.
