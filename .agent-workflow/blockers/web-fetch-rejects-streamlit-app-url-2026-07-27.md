# Web fetch rejects Streamlit application URL

## Context and intended action

A read-only consistency audit needed to inspect the public Streamlit deployment and compare its user-facing model results with the repository's current 70/30 train-test split source.

## Observable symptom

Opening the documented live application URL with the lightweight web-fetch tool returned an internal error stating that the Streamlit URL was not safe to open. No page content was retrieved.

## Impact

The lightweight fetch path cannot establish what the public deployment currently renders. Repository inspection can still establish what the deployed `main` branch contains, but direct runtime verification requires a browser-capable inspection path.

## Likely cause

The fetch service's URL-safety policy rejected the Streamlit Community Cloud application address. This is a tool limitation rather than evidence that the application itself is unavailable.

## Troubleshooting and result

- Confirmed that the URL is the deployment address documented in `README.md`.
- Did not retry the same rejected fetch because the error was marked non-retryable.

## Workaround or remaining limitation

Use the in-app browser or another browser-capable tool to inspect the public Streamlit application. If browser inspection is unavailable, report the deployed-branch artifact state separately from direct live-runtime verification.

## Prevention

For future deployment audits, prefer browser-based inspection for Streamlit Community Cloud applications and reserve lightweight fetches for static pages or APIs known to be accepted by the fetch safety layer.
