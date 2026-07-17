# GitHub CLI authentication is invalid

## Context and intended action

While preparing to commit and push all repository changes, the GitHub publishing workflow checked the installed GitHub CLI and its authentication state.

## Observable symptom

`gh auth status` reported that the stored tokens for both configured GitHub accounts were invalid. The CLI recommended authenticating again with `gh auth login -h github.com`.

## Impact

GitHub API operations through `gh`, such as repository inspection or pull-request creation, are unavailable until authentication is repaired. A standard `git push` may still work independently through Git Credential Manager.

## Likely cause

The locally stored GitHub CLI tokens have expired, been revoked, or are otherwise no longer accepted by GitHub.

## Troubleshooting and results

- Confirmed GitHub CLI is installed (`gh` version 2.96.0).
- Ran `gh auth status`; both configured accounts failed validation.
- Confirmed the repository has an HTTPS `origin` remote.
- A normal `git push -u origin main` reached GitHub but was rejected with HTTP 403 because Git Credential Manager supplied the `FallenWolf10` account for a repository owned by `ngyinhao`.
- Retried against an HTTPS URL that explicitly named `ngyinhao`; no usable cached credential was available, and the non-interactive shell could not open a password prompt (`/dev/tty` unavailable).

## Workaround or remaining limitation

For Git transport, ensure Git Credential Manager selects an account with write access to the target repository. When multiple accounts exist, an HTTPS URL that explicitly includes the intended username may help select the correct cached credential. In this incident no valid credential existed, so the `ngyinhao` account must be reauthenticated in an interactive terminal before retrying the push. For GitHub API operations, reauthenticate with `gh auth login -h github.com`, then verify with `gh auth status`.

## Prevention

- Run `gh auth status` before workflows that require GitHub API access.
- Reauthenticate the intended GitHub account when tokens have expired or been revoked.
- Keep Git CLI credentials and GitHub CLI credentials conceptually separate, since one may work while the other does not.
