# Handoff: TASK-0166

## Final State
`Schema and migration context selection` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0166
- **Phase:** Phase 25 — Database Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the first real `database_adapter` context behavior so Grain can select schema, migration, and nearby model artifacts without relying on graph traces or dragging unrelated application code into the bundle.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify that `database_adapter` now behaves like a direct-selection artifact adapter rather than a graph-traced code adapter
- verify that schema and migration artifacts outrank model-adjacent files
- verify that unrelated application code is intentionally excluded from the bundle

## What Was Not Done
- broader query-file and ORM repository selection remains out of scope
- runtime database tooling and mutation helpers remain deferred

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused adapter-profile, release-surface, and database integration tests only
- the next task (`P25-T03`) should broaden into query and ORM surface hints

## Files Changed
- `src/grain/services/context_service.py` — added the first database-specific direct-selection and source-priority behavior
- `docs/runtime/adapter_profiles.md` — aligned the database adapter patterns with the implemented selection behavior
- `src/grain/data/runtime/adapter_profiles.md` — aligned the shipped runtime copy with the database adapter pattern updates
- `tests/test_document_adapters_integration.py` — added focused database context integration coverage
- `tasks/P25-T02-TASK-0166/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P25-T02-TASK-0166/context.md` — recorded the scoped database context for the task
- `tasks/P25-T02-TASK-0166/plan.md` — recorded the implementation and verification approach
- `tasks/P25-T02-TASK-0166/deliverable_spec.md` — recorded the deliverable boundary for the first database context slice

## Reviewer Notes
- verify the direct-selection database behavior
- verify the schema/migration-first ordering
- verify the bundle stays narrowly focused

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry broader query and ORM surface hints into `P25-T03`
