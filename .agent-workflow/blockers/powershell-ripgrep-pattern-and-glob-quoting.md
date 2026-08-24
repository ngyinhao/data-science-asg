# PowerShell ripgrep pattern and glob quoting

## Context

While tracing duplicated model-evaluation fields on 2026-08-24, repository searches were run from PowerShell with `rg`.

## Symptoms

- Passing a Unix-style positional `*.py` glob caused Windows error 123 because PowerShell did not expand it as expected.
- A regex containing embedded double quotes was altered by shell/argument parsing, producing an `unclosed group` regex error.

## Impact

The initial searches failed and had to be reformulated; no repository data or source files were affected.

## Cause

Windows PowerShell argument and wildcard handling differs from a Unix shell, and nested quoting in a command string can strip characters before `rg` receives them.

## Workaround

Use ripgrep's own glob flags, such as `--glob '*.py'`, rather than positional wildcards. For multiple literal terms, prefer separate `-e` arguments with simple patterns instead of a compound regex containing nested quotes.

## Prevention

- Use `rg -n -S -e 'term_one' -e 'term_two' --glob '*.py' .` on PowerShell.
- Avoid embedded quote characters in regex patterns unless they are essential.
- Keep file filtering in `--glob` options so behavior is consistent across shells.
