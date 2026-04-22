# Handoff: TASK-0127

## Final State
`Improve onboarding and scanner detection for data workflows` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0127
- **Phase:** Phase 18 — Data Adapter
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Updated Phase 18 onboarding and scanner behavior so `data_adapter` is treated as an official applicable adapter when notebooks or data files are present. The old custom-hint path for data workflows is removed, while existing devops/mobile custom-adapter hints remain intact. Generated onboarding drafts now surface `data_adapter` through the normal adapter list.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm removing the old data-adapter custom hint is correct now that `data_adapter` is official.
- - Confirm onboarding drafts should reflect `data_adapter` through `applicable_adapters` only, not an extra bespoke note.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/codebase_scanner.py` — promoted notebook/data-file signals into official `data_adapter` applicability
- - `tests/test_codebase_scanner.py` — asserted data workflows land in `applicable_adapters` instead of a custom hint
- - `tests/test_onboard_doc_generator.py` — verified generated draft docs surface `data_adapter`
- - `tasks/P18-T05-TASK-0127/task.md` — populated packet metadata and scope
- - `tasks/P18-T05-TASK-0127/context.md` — recorded required docs and exclusions
- - `tasks/P18-T05-TASK-0127/plan.md` — captured the implementation plan
- - `tasks/P18-T05-TASK-0127/deliverable_spec.md` — defined acceptance criteria and non-goals
- 

## Reviewer Notes
- - Confirm removing the old data-adapter custom hint is correct now that `data_adapter` is official.
- - Confirm onboarding drafts should reflect `data_adapter` through `applicable_adapters` only, not an extra bespoke note.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
