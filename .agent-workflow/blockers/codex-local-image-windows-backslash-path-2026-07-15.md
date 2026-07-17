# Codex local image failed to render with Windows backslash path

- **Date:** 2026-07-15
- **Context:** Embedded a generated diagnostic PNG in a Codex response using a local absolute Windows path.
- **Symptom:** The user reported that the image could not be seen even though the PNG existed and was readable.
- **Impact:** The diagnostic comparison was not visible in the final response.
- **Cause:** The Markdown image target used Windows backslashes (`C:\\...`), which the Codex renderer did not resolve as an image path.
- **Verification:** The file exists and has nonzero size at the expected visualization location.
- **Workaround:** Use an absolute local path with forward slashes in Markdown, for example `![description](C:/path/to/image.png)`.
- **Prevention:** Normalize local media paths to forward slashes before embedding them in Markdown responses.
