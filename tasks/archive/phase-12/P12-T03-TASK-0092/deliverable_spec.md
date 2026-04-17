# Deliverable Spec: TASK-0092

## Required Output

### New Files
- `tasks/P12-T03-TASK-0092/task.md` — packet metadata/scope
- `tasks/P12-T03-TASK-0092/context.md` — packet context contract
- `tasks/P12-T03-TASK-0092/plan.md` — implementation plan
- `tasks/P12-T03-TASK-0092/deliverable_spec.md` — deliverable contract
- `tasks/P12-T03-TASK-0092/results.md` — execution results
- `tasks/P12-T03-TASK-0092/handoff.md` — review handoff

### Modified Files
- `src/grain/services/workflow_loop_service.py` — dry-run and default step guardrails
- `src/grain/cli/workflow.py` — `workflow loop --dry-run` option and output updates
- `tests/test_workflow_loop_cmd.py` — guardrail/output tests
- `docs/runtime/workflow_loop.yaml` — autonomous risk clarification
- `README.md` — loop guardrail/supervision documentation
- `docs/working/backlog.md` — move `P12-T03` to review and advance `P12-T04`
- `docs/working/current_focus.md` — immediate goals update
- `docs/working/current_task.md` — active task pointer/state

## Acceptance Checklist
- [ ] `workflow loop` supports `--dry-run` and does not mutate task state in preview mode
- [ ] Loop has an explicit default max-step safety cap when `--steps` is omitted
- [ ] Loop output includes clear per-step invocation detail fields
- [ ] Docs clarify supervision levels and autonomous risk model
- [ ] Updated loop tests pass
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Orchestrator-plan consumption in loop ordering
- Additional telemetry/token-capture integration
