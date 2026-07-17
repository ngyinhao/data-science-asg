# Browser locator scroll method unavailable

- **Date:** 2026-07-17
- **Context:** Scrolling the live Streamlit chosen-model page to the paired chart grid for screenshot QA.
- **Symptom:** The browser locator returned by `getByRole(...)` did not expose `scrollIntoViewIfNeeded()`.
- **Impact:** The first screenshot-positioning attempt failed; no application state or source was affected.
- **Cause:** The browser-control locator API supports a narrower method set than standard Playwright locators.
- **Recovery:** Use the supported DOM-backed evaluation surface to find the visible heading and call the browser DOM element's native `scrollIntoView()` method, then take the screenshot.
- **Prevention:** Do not assume every standard Playwright locator method is available in the in-app browser wrapper; use documented methods or DOM-backed evaluation for simple viewport positioning.
