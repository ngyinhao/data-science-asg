# Git index lock creation blocked by sandbox permissions

## Context and intended action

After the user approved committing all working-tree changes, the workflow ran `git add --all` to stage the repository.

## Observable symptom

Git failed with `fatal: Unable to create '.git/index.lock': Permission denied`.

## Impact

The sandbox can edit working-tree files but cannot update the Git index without elevated command permission. Staging and committing cannot proceed inside the default sandbox.

## Confirmed cause

The repository `.git` directory is readable but not writable under the active workspace permission profile.

## Troubleshooting and results

- `git diff --check` completed successfully before staging.
- `git add --all` failed immediately while creating `.git/index.lock`.
- No files were staged by the failed attempt.

## Workaround

Rerun the explicitly authorized Git staging and commit operations with elevated sandbox permission. Keep the command scope limited to this repository and the approved changes.

## Prevention

When the active permission profile exposes `.git` as read-only, anticipate an approval request for commands that update repository metadata, including staging, committing, branch creation, and some merge operations.
