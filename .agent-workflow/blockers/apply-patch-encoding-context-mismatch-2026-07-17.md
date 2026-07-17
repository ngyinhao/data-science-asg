# Apply-patch encoding context mismatch

## Recurrence

- Updating the empty-port incident note with context copied from terminal output failed because the expected line contained terminal-rendered mojibake quotation marks.
- Recovery again succeeded by anchoring the patch only on the ASCII heading and inserting the new section immediately below it.

- **Date:** 2026-07-17
- **Context:** Simplifying the Streamlit prediction page and replacing independent calendar controls with a single date input.
- **Symptom:** `apply_patch` could not find a large expected block even though the surrounding code was present. The failing context included a caption containing a mojibake-rendered em dash.
- **Impact:** The first combined patch was rejected atomically; application source remained unchanged.
- **Likely cause:** The terminal-rendered text and the file's exact encoded characters differed inside a large patch context.
- **Recovery:** Reinspect the file and apply smaller patches anchored on stable ASCII-only lines or replace bounded sections without including the affected caption.
- **Prevention:** Avoid using encoding-sensitive prose as patch context. Prefer short structural anchors such as function calls, headings, and import statements.
