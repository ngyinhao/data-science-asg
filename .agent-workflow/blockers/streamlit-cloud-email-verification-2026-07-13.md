# Streamlit Cloud management requires email verification

## Context and intended action

After pushing the deployment recovery commit, the public app still returned Streamlit's generic startup-error page. Access to the owner-only Community Cloud logs and settings was needed to identify the remaining cause and restart or correct the deployment.

## Observable symptom

GitHub OAuth authorization succeeded, but Streamlit redirected to a six-digit email-verification form and sent the code to the account's registered email address.

## Impact

Owner-only deployment logs and settings remain unavailable until the account holder completes verification. The source fix is already committed and pushed to `main`, but the public application is still unavailable.

## Cause

Streamlit Community Cloud requires a fresh identity-verification step before granting access to its management dashboard.

## Workaround and remaining limitation

The account holder must enter the one-time code directly in the Streamlit verification page. The agent must not retrieve, expose, or handle the code. After verification, resume the existing browser session and inspect the deployment logs/settings.

## Prevention

Before time-sensitive deployment recovery, confirm that the Streamlit Community Cloud owner session is signed in and recently verified. Keep recovery work independent of email access and never record verification codes in repository notes.
