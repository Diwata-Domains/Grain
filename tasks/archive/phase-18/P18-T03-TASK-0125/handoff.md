# Handoff: TASK-0125

## Final State
`Migrate notebook ownership into data_adapter` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0125
- **Phase:** Phase 18 — Data Adapter
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Migrated notebook ownership into `data_adapter` without breaking existing notebook extraction behavior. The runtime adapter profiles now treat `.ipynb` files as part of `data_adapter`, `code_adapter` no longer claims notebook ownership, and the context service now allows `data_adapter` notebook sources to remain selectable without graph traces until the broader Phase 18 integration slice lands.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm treating `data_adapter` like `docs_adapter`/`spreadsheet_adapter` for graph-trace gating is the right temporary compatibility posture until broader integration lands.
- - Confirm notebook extraction content itself stayed unchanged and only ownership/selection moved.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `docs/runtime/adapter_profiles.md` — moved `.ipynb` ownership from `code_adapter` to `data_adapter` and updated notebook-specific hints
- - `src/grain/services/context_service.py` — exempted `data_adapter` from graph-trace requirements to preserve current notebook selection behavior
- - `tests/test_notebook_extractor.py` — validated notebook selection and export under `data_adapter`
- - `tests/test_adapter_config_loader.py` — asserted runtime profile ownership moved off `code_adapter` and onto `data_adapter`
- - `tasks/P18-T03-TASK-0125/task.md` — populated packet metadata and scope
- - `tasks/P18-T03-TASK-0125/context.md` — recorded required docs and exclusions
- - `tasks/P18-T03-TASK-0125/plan.md` — captured the implementation plan
- - `tasks/P18-T03-TASK-0125/deliverable_spec.md` — defined acceptance criteria and non-goals
- 

## Reviewer Notes
- - Confirm treating `data_adapter` like `docs_adapter`/`spreadsheet_adapter` for graph-trace gating is the right temporary compatibility posture until broader integration lands.
- - Confirm notebook extraction content itself stayed unchanged and only ownership/selection moved.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
