# Git push rejected because remote branch advanced

## Context

On 2026-08-24, a completed local commit was pushed from `main` to `origin/main`.

## Observable symptom

The remote rejected the push with a non-fast-forward `fetch first` error because `origin/main` contained work not present in the local branch.

## Impact

The local commit was created successfully but was not published by the first push attempt.

## Likely cause

Another workflow updated the shared remote branch after the local repository's last fetch.

## Workaround

Fetch the current remote branch, integrate the local commit on top of it in an isolated temporary Git worktree, verify the result, and push the resulting fast-forward update. This avoids stashing, overwriting, or otherwise disturbing unrelated edits in the primary worktree.

## Prevention

Before committing to a shared branch, fetch the remote and inspect divergence. When the primary worktree contains unrelated uncommitted changes, use an isolated worktree for integration rather than rebasing with an automatic stash.
