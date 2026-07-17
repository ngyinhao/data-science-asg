# PowerShell `Select-String` does not accept byte encoding in this environment

## Context and intended action

While diagnosing a stale Windows `pip.exe`, a command attempted to search the binary launcher for an embedded former repository path using `Select-String -Encoding Byte`.

## Observable symptom

PowerShell rejected `Byte` because it is not included in the supported values for the `-Encoding` parameter in this host.

## Impact

The auxiliary binary-string inspection failed. The main virtual-environment diagnosis was unaffected because the user's launcher error already displayed the embedded path, and direct Python imports exposed the separate ABI mismatch.

## Cause

This PowerShell version's `Select-String` cmdlet only accepts its enumerated text encodings and does not support raw byte scanning through `-Encoding Byte`.

## Workaround

Use already surfaced launcher diagnostics, a binary-aware strings utility when available, or read bytes with a purpose-built non-mutating tool. Do not use `Select-String -Encoding Byte` in this environment.

## Prevention

Check `Get-Help Select-String -Parameter Encoding` before relying on version-specific encoding values, and prefer text-based evidence when the executable itself already reports its embedded path.
