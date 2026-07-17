# Deferred tool metadata is not directly callable

- **Date:** 2026-07-17
- **Context:** Connecting to the in-app browser after locating the deferred Node browser-control tool in `ALL_TOOLS`.
- **Symptom:** Calling `.call(...)` on the matching metadata entry failed with `TypeError: jstool.call is not a function`.
- **Impact:** The first browser QA setup attempt did not run.
- **Cause:** `ALL_TOOLS` entries describe deferred tools but are not callable function handles.
- **Recovery:** Invoke the normalized tool name from the `tools` namespace after discovery (for example, `tools.mcp__node_repl__js(...)`).
- **Prevention:** Treat `ALL_TOOLS` solely as discovery metadata and use the matching method exposed on `tools` for execution.
