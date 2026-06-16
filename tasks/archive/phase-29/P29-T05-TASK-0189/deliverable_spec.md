# Deliverable Spec: TASK-0189

## Required Output

### New Files
- None

### Modified Files
- `src/grain/services/workflow_service.py` — stop backlog parsing at non-phase section boundaries
- `tests/test_workflow_state_service.py` — add coverage for the section-boundary parser edge
- `README.md` — document `workflow explain` / `workflow reconcile --dry-run` in the hardened loop
- `docs/runtime/AGENTS.md` — document drift recovery steps for long sessions
- `docs/runtime/PROJECT_RULES.md` — document blocked-state and drift recovery rules
- `src/grain/data/runtime/PROJECT_RULES.md` — keep shipped runtime guidance aligned
- `tests/test_release_surface.py` — assert the new operator guidance ships

## Acceptance Checklist
- [x] parser no longer lets non-phase sections overwrite the final task in the active phase
- [x] Phase 29 hardening loop has focused smoke coverage
- [x] README and runtime docs route blocked sessions through explain/reconcile
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New feature work outside Phase 29
- Autonomous remediation beyond existing reconcile flows
