# PowerShell ripgrep regex escaping failure

- **Date:** 2026-07-17
- **Context:** Verifying which chart function received a compact model-label mapping after a patch.
- **Symptom:** `rg` reported an unclosed regex group because embedded quotes and brackets were altered by PowerShell command-string parsing.
- **Impact:** The verification search failed; application source was not changed.
- **Cause:** A complex regular expression containing escaped quotes and square brackets was passed through multiple quoting layers.
- **Recovery:** Use multiple fixed-string (`rg -F`) searches or single-quoted PowerShell arguments for literal source fragments.
- **Prevention:** Prefer `rg -F` for exact code-token verification on Windows instead of nesting complex regex escaping inside JSON and PowerShell strings.

## Recurrence detail

A follow-up command used several semicolon-separated `rg -F` checks. The useful matches printed, but the overall command exited with code 1 because the final literal pattern did not match. Run independent searches when exit status matters, or ensure the last check is expected to match.
