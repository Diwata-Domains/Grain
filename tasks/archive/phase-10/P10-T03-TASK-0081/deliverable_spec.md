# Deliverable Spec: TASK-0081

## Required Output

### New Files
- `tasks/P10-T03-TASK-0081/results.md` — execution results
- `tasks/P10-T03-TASK-0081/handoff.md` — review handoff

### Modified Files
- `src/grain/services/context_service.py` — graph-assisted adapter source selection and trace output
- `src/grain/services/graph_service.py` — graph edge support needed for context traversal anchoring
- `tests/test_context_build.py` — traceability assertions for adapter source selection
- `docs/working/backlog.md` — set `P10-T03` review and `P10-T04` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P10-T03-TASK-0081/task.md` — packet metadata/scope
- `tasks/P10-T03-TASK-0081/context.md` — packet context
- `tasks/P10-T03-TASK-0081/plan.md` — packet plan
- `tasks/P10-T03-TASK-0081/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] Context selection uses graph traversal for adapter source inclusion
- [ ] Packet-local files remain preferred context sources
- [ ] Included adapter files are graph-connected to packet-local files
- [ ] Each included adapter source includes a traceable graph path
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Orchestration adapter capability rewiring (`P10-T04`)
- Full path integration test suite (`P10-T05`)
