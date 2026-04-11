# Deliverable Spec: TASK-0082

## Required Output

### New Files
- `src/grain/adapters/capabilities.py` — graph-aware adapter capability implementation
- `tests/test_graph_adapter_capability.py` — capability behavior tests
- `tasks/P10-T04-TASK-0082/results.md` — execution results
- `tasks/P10-T04-TASK-0082/handoff.md` — review handoff

### Modified Files
- `src/grain/adapters/adapter_config.py` — register graph-aware capabilities on profile load
- `src/grain/services/orchestration_service.py` — consume impact signals in scoring and scope payload
- `src/grain/services/graph_service.py` — import decoupling/edge coverage used by capability flow
- `tests/test_orchestration_service.py` — payload assertions for impact signals
- `docs/working/backlog.md` — set `P10-T04` review and `P10-T05` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P10-T04-TASK-0082/task.md` — packet metadata/scope
- `tasks/P10-T04-TASK-0082/context.md` — packet context
- `tasks/P10-T04-TASK-0082/plan.md` — packet plan
- `tasks/P10-T04-TASK-0082/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] Graph-aware adapter capability implements `detect_scope` and `analyze_impact`
- [ ] Adapter profile loading registers graph-aware capability by default
- [ ] Orchestration scope analysis includes impact signal output
- [ ] Orchestration ranking consumes impact signals
- [ ] Graceful fallback remains when graph data is unavailable
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- End-to-end structural integration suite (`P10-T05`)
- Phase 10 closeout actions
