# Streamlit iframe slider semantic locator timed out

- **Date:** 2026-08-22
- **Context / intended action:** Verify live snowfall sensitivity by locating the deployed Streamlit `Snowfall (cm)` range input through its accessible role and label.
- **Observed symptom:** `getByRole("slider", {name: /Snowfall/})` exceeded the browser selector deadline, although the DOM snapshot visibly contained the labelled snowfall slider inside the Streamlit iframe.
- **Impact:** Direct semantic Playwright interaction could not be used for this control.
- **Likely cause:** The Streamlit app is embedded in an iframe and the browser runtime's top-level semantic locator did not resolve the nested range input.
- **Troubleshooting:** Confirmed the full DOM snapshot exposes `group "Snowfall (cm)"` and a nested slider.
- **Workaround:** Use the visible DOM-node API or explicitly scope a locator to the Streamlit iframe after inspecting its selector.
- **Prevention:** For deployed Streamlit UI tests, capture the DOM snapshot first and keep a DOM-node or frame-scoped fallback for range inputs.
