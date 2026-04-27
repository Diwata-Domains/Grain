# Deliverable Spec: TASK-0123

## Required Output

### New Files
- none

### Modified Files
- `tasks/P18-T01-TASK-0123/task.md` — populated task metadata and execution boundaries
- `tasks/P18-T01-TASK-0123/context.md` — declared required docs and excluded implementation areas
- `tasks/P18-T01-TASK-0123/plan.md` — execution plan for the contract slice
- `docs/runtime/adapter_profiles.md` — add `data_adapter` contract and metadata-only handling guidance
- `docs/working/current_focus.md` — reflect that the Phase 18 extraction boundary is resolved and execution can move to adapter-definition work
- `tests/test_adapter_config_loader.py` — parser coverage for the new adapter profile contract

## Acceptance Checklist
- [ ] `data_adapter` is documented in the runtime adapter inventory and profile section
- [ ] metadata-only extraction boundaries for data/model artifacts are explicit and inspectable in repo docs
- [ ] notebook migration is called out as deferred to a later Phase 18 task, not implemented here
- [ ] focused adapter-profile tests cover the new contract
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- implementing artifact extraction or parsing libraries
- migrating `.ipynb` ownership out of `code_adapter`
- context-service, orchestration, or scanner behavior changes
