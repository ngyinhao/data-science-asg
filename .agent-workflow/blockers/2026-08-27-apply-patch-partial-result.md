# Apply-patch partial-result ambiguity

- **Context:** Adding regression expectations and a blocker note in one multi-file patch.
- **Symptom:** The patch command reported that an expected context was missing, but a subsequent read showed the test-file changes were present while the new incident file was absent.
- **Impact:** It was unclear which edits had landed, requiring a live-file and `git diff` verification before continuing.
- **Likely cause:** The working file changed during or immediately around the patch operation, and the multi-file operation did not yield an obvious all-or-nothing result.
- **Resolution:** Re-read every target and use smaller patches against current content.
- **Prevention:** Separate independent files into small patches when the working tree may be changing, and always verify targets after a context mismatch.
