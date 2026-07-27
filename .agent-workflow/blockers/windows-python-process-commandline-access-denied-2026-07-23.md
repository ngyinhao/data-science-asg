# Windows process command-line inspection denied

## Context and intended action

Several Python processes were running while generated dataset and model files were locked. The workflow attempted to inspect Python command lines to identify which process belonged to this repository without stopping unrelated user processes.

## Observable symptom

`Get-CimInstance Win32_Process` failed with `HRESULT 0x80041003` and an `Access denied` error.

## Impact

The locking process cannot be safely identified from its command line in the current permission context. Stopping Python processes by name or executable path would risk interrupting unrelated user work.

## Likely cause

The current Windows session does not have permission to query process command-line details through WMI/CIM.

## Troubleshooting and results

`Get-Process` returned process IDs and executable paths, but several processes share the same Python installations and none exposed enough repository-specific context to select a safe target.

## Remaining limitation and safe workaround

Ask the user to close any running Streamlit app, notebook, spreadsheet viewer, or Python process using this repository's generated files. Do not terminate ambiguous Python processes automatically.

## Prevention

Launch long-running repository services through a tracked PID file or a dedicated task command so the owning process can later be identified and stopped safely.
