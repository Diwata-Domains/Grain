# Deliverable Spec: TASK-0067

## Acceptance Criteria

1. `forge prompt show` exits 0 for a ready-task workflow state.
2. Text output includes `recommended_prompt` and `next_action`.
3. JSON output has `prompt` key with `recommended_prompt`, `next_action`, `stop_reason`, `blocking_reasons`, `active_phase`, `model_class`, `scope`, `stage`.
4. Prompt metadata (`model_class`, `scope`, `stage`) is populated when the prompt file exists and has a `Metadata:` block.
5. Prompt metadata is empty strings when the prompt file does not exist on disk.
6. Stopped workflow state still exits 0 with `stop_reason` surfaced.
7. Review state with complete artifacts recommends `task.close.md`.
8. `forge prompt show` is registered on the main CLI (`forge prompt --help` works).
9. `prompts/README.md` has a Machine-Readable Prompt Surface section.
10. 11 tests pass. Full suite passes (465 tests).
