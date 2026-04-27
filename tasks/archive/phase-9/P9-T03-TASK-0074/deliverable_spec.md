# Deliverable Spec: TASK-0074

## Required Output

### New Files
- `src/grain/services/orchestration_service.py` — task-level orchestration proposal generator
- `tests/test_orchestration_service.py` — orchestration service behavior coverage
- `tasks/P9-T03-TASK-0074/results.md` — execution results
- `tasks/P9-T03-TASK-0074/handoff.md` — review handoff

### Modified Files
- `docs/working/backlog.md` — set `P9-T03` review and `P9-T04` ready
- `docs/working/current_focus.md` — update immediate goals to next Phase 9 slice
- `docs/working/current_task.md` — set active task pointer/status
- `tasks/P9-T03-TASK-0074/task.md` — finalized packet metadata/scope
- `tasks/P9-T03-TASK-0074/context.md` — finalized context contract
- `tasks/P9-T03-TASK-0074/plan.md` — finalized implementation plan
- `tasks/P9-T03-TASK-0074/deliverable_spec.md` — finalized deliverable contract

## Acceptance Checklist
- [ ] Task-level orchestration service builds `OrchestratorPlan` proposals from scope text
- [ ] Adapter relevance detection uses adapter profiles and capability signals with graceful fallback
- [ ] Multi-adapter scopes produce split recommendations and dependency links
- [ ] No state mutation occurs (no packet creation/backlog edits by service itself)
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge orchestrate` CLI commands (`P9-T06`)
- phase-level orchestration features (`P9-T04`)
- canonical document edits
