# Advertised skill path mismatch

- **Date:** 2026-08-22
- **Context / intended action:** Read the required `diagnosing-bugs` skill instructions before investigating a Streamlit prediction issue.
- **Observed symptom:** Reading `C:\Dev\data-science-asg\.agents\skills\diagnosing-bugs\SKILL.md` failed because the path does not exist.
- **Impact:** The normal repository-local skill-loading path could not be used.
- **Likely cause:** The available-skills catalog advertises the skill from a user-level directory, while another applicable skill is repository-local.
- **Troubleshooting:** Confirmed the Streamlit skill is readable from the repository-local path; the diagnosis skill is not present alongside it.
- **Workaround:** Load `diagnosing-bugs` from its catalogued user-level path, `C:\Users\<user>\.agents\skills\diagnosing-bugs\SKILL.md`.
- **Prevention:** Preserve and use each skill's exact catalogued locator rather than assuming all available skills share the same root.
