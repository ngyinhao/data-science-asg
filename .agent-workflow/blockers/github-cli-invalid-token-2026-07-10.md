# GitHub CLI active token is invalid

- **Date:** 2026-07-10
- **Context and intended action:** Publish the completed Project insights implementation by creating a feature branch, committing the scoped changes, pushing to `origin`, and opening a draft pull request.
- **Symptom:** `gh auth status` reports that the active `github.com` account is `ngyinhao`, but its default token is invalid. The CLI recommends `gh auth login -h github.com`.
- **Impact:** The authenticated GitHub publish workflow cannot proceed. No branch, staging, commit, push, or pull request was created.
- **Cause:** The locally stored GitHub CLI credential has expired, been revoked, or is otherwise no longer accepted.
- **Troubleshooting:** Confirmed that GitHub CLI 2.96.0 is installed; authentication is the failing prerequisite.
- **Recurrence:** A follow-up `gh auth status` check produced the same invalid-token result while investigating how earlier pushes succeeded, confirming this is persistent rather than a transient network failure.
- **Remaining limitation:** The user must re-authenticate GitHub CLI interactively before publishing can resume.
- **Prevention:** Run `gh auth status` before starting branch or staging operations, and refresh credentials with `gh auth login -h github.com` when the active token is invalid.
