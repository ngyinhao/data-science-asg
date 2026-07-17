# Missing `grill-me` skill path

- Context: The user invoked `C:\\Users\\ngyh\\.agents\\skills\\grill-me\\SKILL.md` and requested an interactive briefing.
- Intended action: Read the named skill instructions before proceeding.
- Observable symptom: The supplied path is not present in the available skill catalog; an initial lookup also attempted the wrong installed alias and returned `Cannot find path ... superpowers\\6.1.1\\skills\\grilling\\SKILL.md`.
- Impact: The exact named skill cannot be applied as written.
- Likely cause: The user-facing skill path is stale or not installed, and the available skill is exposed under a different root (`r0/grilling`).
- Troubleshooting: Checked the available skills list and identified `grilling` at `C:\\Users\\ngyh\\.agents\\skills\\grilling\\SKILL.md`; will read and use that fallback.
- Workaround: Use the installed `grilling` skill and continue the requested RMSE/MAE interactive briefing.
- Prevention: Validate the exact skill path against the current available-skills catalog before reading it; prefer the catalog path when a named path is stale.
