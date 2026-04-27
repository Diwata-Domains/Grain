# Deliverable Spec: TASK-0138

## Required Output

### New Files
- `tests/test_workflow_state_service.py` additions — terminal complete-state evaluator coverage
- `tests/test_phase_next_cmd.py` additions — phase-next no-op coverage for completed projects

### Modified Files
- `src/grain/services/workflow_service.py` — parse and surface a `project_complete` workflow state
- `src/grain/services/workflow_run_service.py` — map `project_complete` through the runner gate contract
- `src/grain/cli/phase.py` — describe the complete state as `no_phase_action`

## Acceptance Checklist
- [x] Current-focus terminal state parses as `complete`
- [x] `workflow next` returns `project_complete` instead of `required_docs_invalid`
- [x] `phase next` reports no phase action with a project-complete reason
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Introducing a new task action for complete projects
- Reworking close/phase-archive semantics beyond the terminal-state parse and stop signal
