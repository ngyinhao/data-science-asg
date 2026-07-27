# Parallel exec discards sibling results when one command fails (2026-07-27)

## Context and intended action

Several independent, read-only GitHub authentication probes were launched in parallel through the JavaScript orchestration wrapper.

## Observable symptom

One expected nonzero result from `gh auth status` caused the wrapper to return only that failure. Outputs from the other successful sibling probes were not available.

## Impact

The probes had to be rerun sequentially, increasing latency and obscuring otherwise useful diagnostic evidence.

## Likely cause

The orchestration wrapper rejects the combined execution when one `Promise.all` member returns a failed command result.

## Troubleshooting and result

The investigation switched to individual shell calls so expected nonzero authentication checks could not suppress unrelated results.

## Workaround and prevention

Do not group expected-to-fail diagnostic commands with successful probes in `Promise.all`. Run the failure signal separately or catch each nested tool failure individually if the wrapper supports it.
