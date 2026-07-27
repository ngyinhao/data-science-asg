# Git index lock denied in offline sandbox

## Context and intended action

After regenerating 70/30 outputs, a narrow `git restore` was used to remove incidental notebook ID/kernel-metadata churn and preserve unrelated report links before staging the intended changes.

## Observable symptom

Git failed with `Unable to create '.git/index.lock': Permission denied`.

## Impact

Git operations that update the index cannot run inside the restricted offline shell even though the worktree is writable. No paths were restored by the failed command.

## Likely cause

The managed sandbox exposes `.git` as read-only while allowing writes to the repository worktree.

## Troubleshooting and result

- The failure occurred before Git changed any worktree path.
- The restore targets were explicit files, not a broad directory or repository reset.

## Workaround

Run narrowly scoped Git index operations through the approved host-filesystem escalation path. Continue reviewing exact paths before staging or committing.

## Prevention

Expect `git restore`, `git add`, `git commit`, and related index-writing commands to require the host-filesystem path in this workspace. Keep path lists explicit and verify `git status` before and after each operation.
