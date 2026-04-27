# Deliverable Spec: TASK-0080

## Required Output

### New Files
- `src/grain/services/graph_service.py` — Layer 3 graph build/persist service
- `tests/test_graph_service.py` — graph service tests
- `tasks/P10-T02-TASK-0080/results.md` — execution results
- `tasks/P10-T02-TASK-0080/handoff.md` — review handoff

### Modified Files
- `pyproject.toml` — add `networkx` dependency declaration
- `docs/working/backlog.md` — set `P10-T02` review and `P10-T03` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P10-T02-TASK-0080/task.md` — packet metadata/scope
- `tasks/P10-T02-TASK-0080/context.md` — packet context
- `tasks/P10-T02-TASK-0080/plan.md` — packet plan
- `tasks/P10-T02-TASK-0080/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] Graph service builds typed node/edge records from structural extraction data
- [ ] Edge confidence labels use EXTRACTED/INFERRED/AMBIGUOUS contract
- [ ] Graph artifacts persist as inspectable JSON on disk
- [ ] Graph build is deterministic and local-only
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Context traversal replacement (`P10-T03`)
- Orchestration adapter capability rewiring (`P10-T04`)
