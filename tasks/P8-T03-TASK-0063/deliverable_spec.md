# Deliverable Spec: TASK-0063

## Required Output

### New Files
- `src/forge/cli/workflow.py` — workflow CLI group and `workflow next` command
- `tests/test_workflow_next_cmd.py` — CLI tests for workflow-next behavior
- `tasks/P8-T03-TASK-0063/results.md` — execution results
- `tasks/P8-T03-TASK-0063/handoff.md` — review handoff

### Modified Files
- `src/forge/cli/__init__.py` — register workflow command group
- `src/forge/services/workflow_service.py` — import-cycle-safe result construction
- `docs/working/backlog.md` — mark `P8-T03` status and next readiness transitions
- `docs/working/current_focus.md` — move immediate focus to review `P8-T03` and next task
- `docs/working/current_task.md` — set active packet pointer
- `tasks/P8-T03-TASK-0063/task.md` — packet metadata/scope
- `tasks/P8-T03-TASK-0063/context.md` — packet context
- `tasks/P8-T03-TASK-0063/plan.md` — packet plan
- `tasks/P8-T03-TASK-0063/deliverable_spec.md` — packet deliverable contract

## Acceptance Checklist
- [ ] `forge workflow next` command exists and is wired under `forge workflow`
- [ ] Text output reports either `next_action` or `stop_reason` with blockers
- [ ] JSON output includes structured evaluator payload for automation
- [ ] Command remains read-only and does not mutate workflow/task files
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge workflow run` execution behavior
- `forge task next`, `forge phase next`, `forge prompt show` commands
- Canonical documentation changes
