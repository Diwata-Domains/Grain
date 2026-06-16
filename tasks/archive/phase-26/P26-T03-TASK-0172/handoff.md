# Handoff: TASK-0172

## Final State
`Output-validation and extraction-surface hints` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0172
- **Phase:** Phase 26 — Crawler Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the extraction-quality crawler context slice so Grain can surface output fixtures and normalization files when the task objective points at output validation work.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify that extraction-quality objectives now lift output and normalization surfaces
- verify that config/selector-first remains the default for other crawler tasks
- verify that unrelated application code is still excluded from the bundle

## What Was Not Done
- review and safety guidance remains out of scope
- runtime crawler tooling and dependency modeling remain deferred

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused adapter-profile, release-surface, and crawler integration tests only
- the next task (`P26-T04`) should formalize crawler review and safety guidance

## Files Changed
- `src/grain/services/context_service.py` — extended crawler objective-sensitive source prioritization
- `docs/runtime/adapter_profiles.md` — added output and normalization patterns to the crawler adapter contract
- `src/grain/data/runtime/adapter_profiles.md` — aligned the shipped runtime copy with the updated crawler adapter patterns
- `tests/test_adapter_config_loader.py` — added parser assertions for the output and normalization pattern coverage
- `tests/test_document_adapters_integration.py` — added extraction-quality crawler integration coverage
- `tasks/P26-T03-TASK-0172/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P26-T03-TASK-0172/context.md` — recorded the scoped crawler context for the task
- `tasks/P26-T03-TASK-0172/plan.md` — recorded the implementation and verification approach
- `tasks/P26-T03-TASK-0172/deliverable_spec.md` — recorded the deliverable boundary for the output-validation slice

## Reviewer Notes
- verify the extraction-quality ordering
- verify the default crawler bundle remains narrow
- verify the contract/tests stay aligned

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry crawler review and safety guidance into `P26-T04`
