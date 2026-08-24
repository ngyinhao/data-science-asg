# Git index lock permission denied

Date: 2026-07-11

## Context

Staging the repository changes before committing and pushing `main`.

## Symptom

`git add` failed with `fatal: Unable to create '.git/index.lock': Permission denied`.

## Impact

Git could not stage or commit the requested changes within the filesystem sandbox.

## Likely cause

The workspace allows writes to project files but restricts writes inside the `.git` metadata directory.

## Workaround

Run the required Git staging/commit command with elevated permission. If this recurs, grant elevated access for the narrowly scoped Git commands.

## Recurrence — 2026-07-13

Staging the Streamlit deployment recovery with `git add --all` again failed because the managed workspace could not create `.git/index.lock`. The repository files remained unchanged and unstaged. Reuse the validated workaround: rerun the narrowly scoped staging command with elevated permission.

## Recurrence — 2026-08-24

Staging an explicit set of files with `git add -- <paths>` failed with the same `.git/index.lock` permission error. The failed attempt did not stage files. Retrying the same narrowly scoped command with escalated permission succeeded, while unrelated working-tree changes remained unstaged. Future commit workflows in this managed workspace should inspect status first, stage explicit paths, and expect Git index writes to require approval.
