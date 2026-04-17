# Deliverable Spec: TASK-0096

## Required Output

### New Files
- `tasks/P13-T03-TASK-0096/task.md` — packet metadata and scope
- `tasks/P13-T03-TASK-0096/context.md` — context contract
- `tasks/P13-T03-TASK-0096/plan.md` — implementation plan
- `tasks/P13-T03-TASK-0096/deliverable_spec.md` — deliverable checklist
- `tasks/P13-T03-TASK-0096/results.md` — execute-stage outcomes
- `tasks/P13-T03-TASK-0096/handoff.md` — review handoff
- `src/grain/services/onboard_doc_generator.py` — draft generation service
- `tests/test_onboard_doc_generator.py` — generator tests

### Modified Files
- `docs/working/backlog.md` — status sequencing updates (`P13-T03`, `P13-T04`)
- `docs/working/current_focus.md` — immediate goals update
- `docs/working/current_task.md` — active packet pointer/status

## Acceptance Checklist
- [ ] `OnboardDocGenerator.generate()` consumes `ScanResult` and returns a generation manifest
- [ ] Generates additive draft files for canonical + working docs required by task
- [ ] Never overwrites existing files
- [ ] Supports `dry_run` without writing files
- [ ] Every generated doc includes a `# DRAFT` marker
- [ ] Open questions draft includes gap-driven entries when scan signals are sparse
- [ ] New generator tests pass
- [ ] Full test suite passes with no regressions
- [ ] Review bundle complete in `results.md` and `handoff.md`

## Not Required
- `workflow.onboard.existing.md` prompt changes (P13-T04)
- Phase 13 integration suite (P13-T05)
