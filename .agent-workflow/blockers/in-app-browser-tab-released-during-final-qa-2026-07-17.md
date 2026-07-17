# In-app browser tab was released during final QA

## Context and intended action

After visually verifying the compact Streamlit overview cards, the workflow attempted to reuse the same controlled in-app browser tab for a final cross-page metric-count and exception sweep.

## Observable symptom

The browser reported that the tab was no longer part of the active browser session.

## Impact

The final automated route sweep could not proceed on that tab, although the prior visual checks had completed successfully.

## Likely cause

The tab was released, replaced, or otherwise detached from the current browser-control session while the user-facing browser remained open.

## Workaround

Keep the existing browser binding, discard the stale tab reference, create a fresh controlled tab, and rerun only the remaining final checks. Do not reinitialize or switch browser surfaces for a missing tab.

## Prevention

Treat browser bindings and tab bindings separately. Before a multi-route final QA pass, obtain a fresh controlled tab if the previously used tab has been visible to the user or may have been released between interactions.

## Recurrence: visible user tab not yet claimed

During later prediction-page QA, `browser.user.openTabs()` listed the visible tab, but `browser.tabs.get(id)` could not find it because it had not been claimed into the controlled tab collection. The safe recovery is `browser.user.claimTab(id)`, followed by operations on the returned tab binding. A user-tab ID is not interchangeable with a controlled-tab ID until that claim succeeds.

## Claimed-tab deliverable annotation limitation

After successful interaction and validation on a claimed user tab, the optional `markDeliverable()` annotation was not callable on that binding even though its prototype inspection listed the method. This did not affect navigation, DOM inspection, user-visible state, or QA results. Leave the already-visible user tab open and treat deliverable annotation as nonessential for a claimed tab.

## Recurrence after local server restart

During residual-axis QA, a previously claimed tab became detached after the verified Streamlit process restarted. The browser binding remained valid and the user-visible tab remained open. Discard the stale tab binding, list `browser.user.openTabs()`, and claim the current visible tab before continuing.
