# In-app browser does not support `networkidle` load state

## Context and intended action

During responsive QA of the local Streamlit app, browser automation attempted to wait for the page's `networkidle` state before reading its DOM and console logs.

## Observable symptom

The browser tool rejected the wait with: `playwright_wait_for_load_state does not support networkidle`.

## Impact

The initial browser observation stopped before the DOM snapshot was collected. The Streamlit server and application remained running.

## Cause

This managed in-app browser exposes a limited Playwright-compatible API and does not implement the otherwise documented `networkidle` load-state option.

## Workaround

Use the supported `domcontentloaded` or `load` state, then verify Streamlit readiness with a concrete visible element or a fresh DOM snapshot. Avoid relying on a fixed sleep except as a short last resort.

## Prevention

For local Streamlit QA in this environment, wait for `domcontentloaded` and then target an expected heading or widget. Do not request `networkidle`.
