# Ripgrep received an unexpanded Windows glob path

- **Date:** 2026-07-11
- **Context and intended action:** Search Markdown blocker notes for the newly added incident headings from PowerShell.
- **Symptom:** `rg ... .agent-workflow/blockers/*.md` failed with Windows error 123: the filename, directory name, or volume label syntax was incorrect.
- **Impact:** The final text-location check did not run on its first attempt; application code and tests were unaffected.
- **Cause:** PowerShell passed the wildcard path to `rg` without expanding it into file paths, and `rg` treated the literal asterisk in the path as invalid on Windows.
- **Workaround:** Pass the directory as the search path and use ripgrep's own glob option: `rg -g '*.md' PATTERN .agent-workflow/blockers`.
- **Prevention:** On Windows PowerShell, prefer `rg -g '<pattern>' <query> <directory>` over placing wildcard characters directly in a path argument.
