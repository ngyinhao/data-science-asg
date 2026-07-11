# Git index lock permission denied

Date: 2026-07-11

## Context

Staging the repository changes before committing and pushing `main`.

## Symptom

`git add --all` failed with `fatal: Unable to create '.git/index.lock': Permission denied`.

## Impact

Git could not stage or commit the requested changes within the filesystem sandbox.

## Likely cause

The workspace allows writes to project files but restricts writes inside the `.git` metadata directory.

## Workaround

Run the required Git staging/commit command with elevated permission. If this recurs, grant elevated access for the narrowly scoped Git commands.
