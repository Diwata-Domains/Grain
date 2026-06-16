# Deliverable Spec: TASK-0187

## Required Output

### New Files
- `src/grain/services/workflow_diagnostics_service.py`
- `tests/test_workflow_explain_cmd.py`

### Modified Files
- `src/grain/cli/workflow.py` — add `workflow explain`
- `tests/test_command_groups.py` — register the new workflow subcommand

## Acceptance Checklist
- [x] `grain workflow explain` stays thin over the existing evaluator
- [x] common stop reasons and actionable states produce concrete operator guidance
- [x] focused workflow diagnostic tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New workflow state mutation logic
- Background services, daemons, or hidden state
- Full docs closeout for the phase
