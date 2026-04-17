# Results: TASK-0067

## Packet State
- **Current Task Status:** done
- **Review Readiness:** ready
- **Recommended Next Status:** done

## Files Changed
- `src/forge/services/prompt_service.py` (new) — workflow-state-aware prompt recommendation with metadata parsing
- `src/forge/cli/prompt.py` (new) — `prompt show` subcommand with text and JSON output
- `src/forge/cli/__init__.py` — registered prompt_group
- `prompts/README.md` — Machine-Readable Prompt Surface section added
- `tests/test_prompt_show_cmd.py` (new) — 11 tests

## Summary
Added `forge prompt show`: a read-only command that calls `evaluate_workflow_state`, extracts the `recommended_prompt`, parses the prompt file's `Metadata:` block for `model_class`, `scope`, and `stage`, and returns a structured payload. Stopped states exit 0 with `stop_reason` surfaced. JSON output nests the payload under `prompt` key, consistent with Phase 8 machine-readable output conventions. Text output prints key/value lines. Prompts remain execution aids — canonical authority is not changed.

## Test Results
11/11 in test_prompt_show_cmd.py. 465/465 total passing.

## Efficiency

### Execute
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Files Read (estimated):** 15
- **Notes:** Single pass. One test fix required (review state test needed all four required packet files). No rework otherwise.

### Review
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Notes:** Verified the prompt-surface wrapper, JSON envelope, and metadata parsing against the evaluator contract.

### Close
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Notes:** Closed after review acceptance; current task pointer cleared.

## Review Notes
- `_parse_prompt_metadata` stops at the first blank or `#`-prefixed line after `Metadata:`. Reviewer should confirm this terminates correctly for prompts that have subsections before the first blank line.
- Stopped workflow states return `ok=False` from `evaluate_workflow_state` but the `prompt show` command exits 0 (consistent with `workflow next` behavior). Reviewer should confirm this is the intended contract.
- The `recommended_prompt` falls back to `"prompts/task.execute.md"` when `evaluation.recommended_prompt` is empty. This covers the edge case where a stopped state has no specific prompt recommendation.

## Review Intake
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **Review Decision:** ready
- **Definition of Done Met:** yes
- **Recommended Next Status:** done

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Deliverable Checklist
- [x] forge prompt show exits 0 for ready-task state
- [x] Text output includes recommended_prompt and next_action
- [x] JSON output has prompt key with all required fields
- [x] Prompt metadata populated from prompt file
- [x] Graceful degradation when prompt file missing
- [x] Stopped state exits 0 with stop_reason
- [x] Review state recommends task.close.md
- [x] forge prompt show registered on CLI
- [x] prompts/README.md updated
- [x] 465/465 tests passing

## Blockers
None.
