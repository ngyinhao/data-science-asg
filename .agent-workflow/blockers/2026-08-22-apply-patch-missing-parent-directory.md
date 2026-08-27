# Patch editor cannot create missing parent directories

- **Date:** 2026-08-22
- **Context / intended action:** Add a repository-local diagnostic repro under a new `.agent-workflow/repros/` directory.
- **Observed symptom:** `apply_patch` failed with `Failed to create parent directories`.
- **Impact:** The repro file could not be added in one patch operation.
- **Cause:** The patch editor creates files but does not create missing directory trees in this environment.
- **Troubleshooting:** A direct `New-Item` retry was denied by the sandbox. A subsequent multi-file patch that first added a file under the already-existing `blockers/` directory and then added the repro succeeded, including creation of the `repros/` directory.
- **Workaround:** When a single-file add under a new directory fails, use one patch that first writes to an existing directory and then adds the file under the new directory. Verify the resulting files afterward.
- **Prevention:** Prefer pre-existing workflow directories, and verify directory creation because patch behavior differs between single-file and multi-file operations in this environment.
