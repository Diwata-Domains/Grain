# Deliverable Spec: TASK-0037

## Required Deliverables

- [x] `forge context show` command implemented in `src/forge/cli/context.py`
- [x] text output lists packet files and selected docs
- [x] JSON output serializes selected sources
- [x] tests in `tests/test_context_show_cmd.py`
- [x] no regressions in existing tests

## Acceptance Criteria

- [x] `forge context show --id TASK-####` succeeds for an existing packet and manifest
- [x] text output includes selected packet files and selected doc entries
- [x] JSON output includes `bundle` with packet files and selected docs
- [x] unknown packet ID returns usage-style failure (exit code 2)
- [x] existing context build and selection tests remain passing
