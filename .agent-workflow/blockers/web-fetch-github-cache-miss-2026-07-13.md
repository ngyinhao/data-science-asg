# Web fetch could not read public GitHub files

## Context and intended action

After reproducing the public Streamlit deployment failure, the investigation attempted a read-only comparison of `requirements.txt`, the app entry point, and recent commits on the repository's public GitHub `main` branch.

## Observable symptom

All three web opens returned an internal `Cache miss` fetch error rather than repository content.

## Impact

The web-fetch route could not independently verify the remote files. Local Git metadata still showed `HEAD`, `main`, and `origin/main` at the same commit, and browser-based inspection remained available.

## Likely cause

The managed web fetcher could not populate or access its cache for the GitHub and raw GitHub URLs. This was not an HTTP error emitted by the repository itself.

## Workaround

Use local Git refs when they are current, use the connected browser for visible public pages, or use `git fetch`/the GitHub CLI when network and authentication are available.

## Prevention

Do not rely on a single web-fetch call for deployment-state verification. Pair it with local `git log --decorate`, remote-ref inspection, or a browser-visible commit page.
