# Windows denied TCP listener ownership query

## Context and intended action

The local Streamlit server needed a controlled restart so the new theme configuration would load. Before stopping anything, the workflow attempted to resolve the exact process listening on port 8501 and verify its executable path.

## Observable symptom

`Get-NetTCPConnection -LocalPort 8501 -State Listen` failed with an access-denied CIM error under the default sandbox permissions.

## Impact

The workflow could not safely identify the exact server process under default permissions and therefore did not attempt to stop it.

## Confirmed cause

The active Windows permission profile does not allow the CIM TCP connection query without elevated command access.

## Workaround

Rerun the read-only listener lookup with elevated permission, verify that the resolved process path belongs to the repository virtual environment, and only then stop that exact process ID.

## Prevention

Expect an approval requirement for Windows TCP ownership queries in this environment. Always verify both the port and executable path before restarting a local development server.
