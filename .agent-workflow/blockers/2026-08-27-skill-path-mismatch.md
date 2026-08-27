# Skill path mismatch

- **Context:** Reading the required Streamlit and bug-diagnosis skill instructions before investigating prediction behavior.
- **Intended action:** Load both `SKILL.md` files from their catalog-provided locations.
- **Symptom:** The initial command tried to read `diagnosing-bugs` under the repository-local `.agents/skills` directory and PowerShell reported that the path did not exist.
- **Impact:** The diagnosis workflow was briefly delayed; no application files were changed.
- **Cause:** The available-skills catalog points `developing-with-streamlit` into the repository, but `diagnosing-bugs` is installed under the user's Codex skills directory. The paths do not share a common root.
- **Resolution:** Use each exact absolute path from the skills catalog rather than assuming all skills are repository-local.
- **Prevention:** Copy catalog locations verbatim and validate each path independently when loading multiple skills.

## Recurrence — 2026-08-27

- The same incorrect repository-local assumption recurred while answering a follow-up about non-functioning predictions.
- The existing incident note immediately identified the correct installed location: `C:\Users\<user>\.agents\skills\diagnosing-bugs\SKILL.md`.
- No application files were affected. Future multi-skill reads should use each catalog-provided absolute path independently.
