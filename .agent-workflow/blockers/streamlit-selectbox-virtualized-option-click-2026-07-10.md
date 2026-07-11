# First click on an offscreen Streamlit selectbox option only scrolled the list

- **Date:** 2026-07-10
- **Context and intended action:** Select the lower `Rainfall` option in the twelve-item Streamlit explorer while performing browser-based visual QA.
- **Symptom:** The first Playwright click left `Hour` selected and kept the list open; the option window shifted downward. A fresh snapshot showed `Rainfall` still present and a second verified click selected it.
- **Impact:** The interaction needed one recovery cycle before the rainfall chart could be inspected.
- **Likely cause:** The virtualized selectbox list first scrolled the lower option fully into view instead of activating it.
- **Troubleshooting:** Reading the combobox value after the click provided an authoritative failure signal. A new DOM snapshot showed the option list had moved and exposed the option as fully visible.
- **Workaround:** After targeting a lower virtualized option, verify the combobox value. If it did not change, take a fresh snapshot, rebuild the unique option locator, and click the now-visible option once.
- **Prevention:** Treat value verification as part of selectbox QA and avoid reusing a locator after the virtualized list scrolls.

