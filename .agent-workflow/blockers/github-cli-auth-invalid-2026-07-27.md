# GitHub CLI authentication invalid (2026-07-27)

## Context and intended action

The requested workflow was to verify the current 70:30 train/test split changes, commit only the intended files, and push the current branch to its configured GitHub remote.

## Observable symptom

`gh auth status` reported that the stored tokens for both configured GitHub accounts were invalid. The active account could not authenticate to `github.com`.

## Impact

The repository's GitHub publishing workflow requires a valid authenticated `gh` session before committing and pushing. No files were staged, committed, or pushed.

## Likely cause

The locally stored GitHub CLI credentials have expired, been revoked, or are otherwise no longer accepted.

## Troubleshooting and result

- Confirmed that GitHub CLI is installed and available.
- Confirmed the repository has an `origin` remote pointing to GitHub.
- Ran `gh auth status`; authentication failed for all configured accounts.
- Retried `gh auth status` after authentication was reported restored; both configured accounts still reported invalid tokens, including the active `ngyinhao` account. The commit-and-push workflow remained paused, with none of the intended files staged.
- Retried again after a terminal was reported to show the active account with repository scope. In the shell attached to this task, `gh auth status` still returned invalid-token failures for both accounts. No app terminal was attached to this task, so the successful terminal state could not be inspected or reused. This indicates the authentication update likely occurred in a different process environment, user context, or credential store from the task shell.

## Workaround or remaining limitation

Re-authenticate the intended GitHub account with:

```powershell
gh auth login -h github.com
```

Run this command from the same Codex task shell/environment that will perform the push, or ensure the repaired credential store and relevant environment variables are visible to that shell.

Then confirm success with:

```powershell
gh auth status
```

After authentication succeeds, resume the scoped commit and push. Explicitly stage only:

- `notebooks/02_data_preparation.ipynb`
- `src/create_project_artifacts.py`
- `src/train_models.py`

Do not stage unrelated files in `.agent-workflow/blockers/`.

## Prevention

Run `gh auth status` near the start of future GitHub publishing workflows so expired credentials are detected before staging or committing changes.

## Corrected diagnosis (2026-07-27)

Further investigation showed that the credentials were not invalid:

- In the restricted task shell, `gh api user --jq '.login'` failed before authentication with a Windows socket-access denial.
- The same API command, rerun with approved network access, succeeded and returned the active account `ngyinhao`.
- `gh auth status -h github.com`, rerun with approved network access, validated both stored keyring accounts. The active `ngyinhao` token includes `repo` scope.
- No `GH_TOKEN`, `GITHUB_TOKEN`, enterprise token, or `GH_HOST` process override was present.
- The restricted process identity was `CodexSandboxOffline`, confirming that the failed check ran in the offline sandbox context.

The high-level `invalid token` output from sandboxed `gh auth status` was therefore a misleading result caused by blocked outbound connectivity, not expired or revoked credentials.

### Updated workaround

Run GitHub authentication checks and the eventual push with the narrow, approved network escalation required by the managed shell. Do not ask the user to reauthenticate based only on sandboxed `gh auth status`; first distinguish network reachability with a read-only API probe.
