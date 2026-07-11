# Active goal already exists

- **Date:** 2026-07-10
- **Context and intended action:** The user invoked `/goal` for `planning/demand-drivers-implementation-plan.md`; the agent attempted to create the requested tracked goal before beginning implementation.
- **Symptom:** Goal creation failed with `cannot create a new goal because this thread has an unfinished goal; complete the existing goal first`.
- **Impact:** A duplicate goal could not be created, briefly interrupting normal startup.
- **Cause:** This task already had an active goal with the same implementation objective.
- **Troubleshooting:** Queried the current goal and confirmed that its objective exactly matches the user's request and its status is active.
- **Workaround:** Continue the existing matching goal instead of creating a replacement.
- **Prevention:** Before creating a goal in a resumed task, query the current goal when prior goal state is uncertain; reuse an active matching goal.

