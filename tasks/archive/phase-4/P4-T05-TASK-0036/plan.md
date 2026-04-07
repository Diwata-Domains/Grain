# Plan: TASK-0036

## Steps

1. Add `build_context_bundle(root, task_id, include_working_docs, context_tags)` in `context_service` using packet source discovery + document selection helpers.
2. Implement `forge context build` with `--id`, optional `--include-working`, and optional repeated `--tag`.
3. Add command tests for text/json success, working-doc inclusion, and unknown task behavior.
4. Run targeted tests and then full suite.
