# Deliverable Spec: TASK-0036

## Required Deliverables

- [x] `forge context build` command implemented in `src/forge/cli/context.py`
- [x] bundle assembly service exists in `src/forge/services/context_service.py`
- [x] text output shows selected source summary
- [x] JSON output serializes the assembled context bundle
- [x] command tests in `tests/test_context_build_cmd.py`
- [x] no regressions in test suite

## Acceptance Criteria

- [x] `forge context build --id TASK-####` succeeds for an existing packet and manifest
- [x] text mode displays selected source counts and source paths
- [x] JSON mode includes a serialized `bundle` object with selected packet/doc sources
- [x] unknown packet ID returns usage-style failure (exit code 2)
- [x] existing context selection tests remain passing
