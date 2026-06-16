# Handoff: TASK-0171

## Final State
`Crawl config and selector context selection` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0171
- **Phase:** Phase 26 — Crawler Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the first real `crawler_adapter` context behavior so Grain can select crawl configs, selectors, and extraction-schema artifacts without relying on graph traces or dragging unrelated application code into the bundle.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify that `crawler_adapter` now behaves like a direct-selection artifact adapter rather than a graph-traced code adapter
- verify that crawl configs and selectors outrank extraction-schema artifacts
- verify that unrelated application code is intentionally excluded from the bundle

## What Was Not Done
- broader output-validation and extraction-quality prioritization remains out of scope
- runtime crawler tooling and execution helpers remain deferred

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused adapter-profile, release-surface, and crawler integration tests only
- the next task (`P26-T03`) should broaden into output-validation and extraction-surface hints

## Files Changed
- `src/grain/services/context_service.py` — added the first crawler-specific direct-selection and source-priority behavior
- `tests/test_document_adapters_integration.py` — added focused crawler context integration coverage
- `tasks/P26-T02-TASK-0171/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P26-T02-TASK-0171/context.md` — recorded the scoped crawler context for the task
- `tasks/P26-T02-TASK-0171/plan.md` — recorded the implementation and verification approach
- `tasks/P26-T02-TASK-0171/deliverable_spec.md` — recorded the deliverable boundary for the first crawler context slice

## Reviewer Notes
- verify the direct-selection crawler behavior
- verify the config/selector-first ordering
- verify the bundle stays narrowly focused

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry output-validation and extraction-surface hints into `P26-T03`
