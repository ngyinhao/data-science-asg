# PowerShell ripgrep regex quoting failure

## Context and intended action

While investigating a device-specific Streamlit issue, a diagnostic command attempted to search the `app/` directory for several potentially version-sensitive API patterns with one alternation regex.

## Observable symptom

`rg` stopped before searching and reported `regex parse error` with `unclosed group`. The pattern shown in the error was truncated at the quoted `width="stretch"` term.

## Impact

Only that diagnostic search was interrupted. No application or dependency files were changed, and investigation continued with safer commands.

## Likely cause

PowerShell consumed or altered embedded double quotes inside the regex argument before passing it to `rg`, leaving an incomplete expression.

## Troubleshooting and workaround

- Confirmed that earlier simple `rg` searches worked normally.
- Avoid embedded double-quoted literals in a larger PowerShell double-quoted regex.
- Use single quotes around the entire regex, escape only for ripgrep, or split the search into multiple fixed-string (`rg -F`) searches.

## Prevention

For Windows PowerShell diagnostics, prefer single-quoted regex arguments or `rg -F -e pattern1 -e pattern2` when searching for source-code strings that contain double quotes.
