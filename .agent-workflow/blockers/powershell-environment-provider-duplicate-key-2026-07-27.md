# PowerShell environment provider duplicate-key failure (2026-07-27)

## Context and intended action

While diagnosing GitHub CLI authentication, the workflow attempted to enumerate only the names of possible GitHub token environment variables without exposing their values.

## Observable symptom

`Get-ChildItem Env:` failed with `An item with the same key has already been added`.

## Impact

The combined diagnostic probe stopped before reporting whether token override variables were present.

## Likely cause

The process environment contains case-insensitive duplicate variable names, which the PowerShell environment provider cannot materialize as a keyed collection.

## Troubleshooting and result

The failing broad enumeration was abandoned. Direct calls to `[Environment]::GetEnvironmentVariable()` for a fixed allowlist avoid enumerating the environment and preserve secret safety.

## Workaround and prevention

On this Windows task host, do not use `Get-ChildItem Env:` for diagnostics. Query known variable names directly and report only presence or length when values may be sensitive.
