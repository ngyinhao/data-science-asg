# GitHub remote check blocked by sandbox network access

- **Date:** 2026-07-10
- **Context and intended action:** Run the read-only `git ls-remote origin HEAD` command to determine whether Git Credential Manager—the likely path used by earlier pushes—still has working GitHub access.
- **Symptom:** Git failed immediately with `Could not connect to server` for `github.com:443`.
- **Impact:** The sandboxed check could not distinguish working Git credentials from network isolation.
- **Likely cause:** Network access is restricted in the managed shell sandbox; the failure occurred before GitHub authentication could be evaluated.
- **Troubleshooting:** The error is a connection failure, distinct from the explicit invalid-token result returned locally by `gh auth status`.
- **Workaround:** Re-run the narrow read-only Git remote command with approved network access.
- **Prevention:** Expect GitHub remote operations from the managed shell to require scoped network escalation even when local credentials are valid.

## Recurrence (2026-07-11)

- **Context:** Push commit `856196f` from `main` to `origin`.
- **Symptom:** `git push origin main` again failed before authentication with `Failed to connect to github.com:443`.
- **Workaround:** Re-run the scoped push command with approved network access.

## Recurrence and misleading auth output (2026-07-27)

- **Context:** Verify GitHub credentials before a scoped commit and push.
- **Symptom:** Sandboxed `gh auth status` labeled both keyring tokens invalid, while `gh api user` exposed the underlying socket-access denial.
- **Result:** With approved network access, `gh api user` returned `ngyinhao` and `gh auth status` validated both configured accounts.
- **Lesson:** In this environment, an `invalid token` result from sandboxed GitHub CLI checks is not conclusive. Re-run a narrow read-only authentication probe with approved network access before diagnosing credential expiry.

## GitHub app cannot create pull request (2026-07-27)

- **Context:** After successfully pushing `codex/refresh-70-30-artifacts`, the preferred GitHub app connector was used to open a draft pull request targeting `main`.
- **Symptom:** GitHub returned `403 Resource not accessible by integration` from the pull-request creation endpoint.
- **Impact:** The connector could not create the PR even though the branch was present on the remote.
- **Cause:** The installed GitHub integration lacks permission for this repository's pull-request creation operation. This is separate from CLI authentication, which had already been verified for `ngyinhao` with `repo` scope.
- **Workaround:** Use the publishing workflow's authenticated `gh pr create` fallback through the scoped network approval path.
- **Prevention:** Expect PR creation through this connector to fail until the GitHub integration is granted appropriate repository pull-request permissions; retain `gh` as the documented fallback.
