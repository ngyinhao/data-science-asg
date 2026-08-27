# Streamlit rerun invalidated a browser DOM node ID

- **Date:** 2026-08-22
- **Context / intended action:** After changing the live snowfall slider, edit the date field to compare an equivalent winter scenario.
- **Observed symptom:** Reusing the earlier date input's DOM node ID after the Streamlit rerun acted on stale page state and navigation landed on the Model comparison page.
- **Impact:** The live winter comparison was discarded; no application data or repository state was changed.
- **Likely cause:** Streamlit rerendered the iframe after the slider interaction, invalidating previously captured DOM node IDs.
- **Troubleshooting:** The post-action DOM snapshot showed the new page and confirmed the stale-node interaction was not a valid date edit.
- **Workaround:** Capture a fresh visible-DOM snapshot after every Streamlit rerun and resolve a new node ID before the next interaction.
- **Prevention:** Never retain Streamlit DOM node IDs across widget-triggered reruns; treat every interaction as invalidating the prior DOM map.
