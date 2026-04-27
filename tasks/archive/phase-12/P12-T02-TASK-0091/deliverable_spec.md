# Deliverable Spec: TASK-0091

## Required Output

### New Files
- `src/grain/services/workflow_loop_service.py` — workflow loop execution service
- `tests/test_workflow_loop_cmd.py` — loop command tests
- `tasks/P12-T02-TASK-0091/task.md` — packet metadata/scope
- `tasks/P12-T02-TASK-0091/context.md` — packet context contract
- `tasks/P12-T02-TASK-0091/plan.md` — implementation plan
- `tasks/P12-T02-TASK-0091/deliverable_spec.md` — deliverable contract
- `tasks/P12-T02-TASK-0091/results.md` — execution results
- `tasks/P12-T02-TASK-0091/handoff.md` — review handoff

### Modified Files
- `src/grain/cli/workflow.py` — adds `workflow loop` command
- `docs/working/backlog.md` — move `P12-T02` to review and advance `P12-T03`
- `docs/working/current_focus.md` — update immediate goals after `P12-T02`
- `docs/working/current_task.md` — active packet pointer/state

## Acceptance Checklist
- [ ] `grain workflow loop` command added with step limit and supervision override options
- [ ] Loop service supports supervised/gated/autonomous stop behavior
- [ ] Command outputs structured per-step progress in text and JSON
- [ ] New loop command tests pass
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `--dry-run` guardrail mode and expanded safety docs (P12-T03)
- orchestrator-plan integration (P12-T04)
