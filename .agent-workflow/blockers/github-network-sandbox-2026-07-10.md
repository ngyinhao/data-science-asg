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
