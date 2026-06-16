# Handoff: TASK-0167

## Final State
`Query and ORM surface hints` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0167
- **Phase:** Phase 25 — Database Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the persistence-oriented database context slice so Grain can surface query, repository, and db-layer files when the task objective points at persistence work.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify that persistence-oriented objectives now lift query and repository surfaces
- verify that schema/migration-first remains the default for other database tasks
- verify that unrelated application code is still excluded from the bundle

## What Was Not Done
- review/validation guidance remains out of scope
- runtime database tooling and dependency modeling remain deferred

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused adapter-profile, release-surface, and database integration tests only
- the next task (`P25-T04`) should formalize review and validation guidance

## Files Changed
- `src/grain/services/context_service.py` — extended database objective-sensitive source prioritization
- `docs/runtime/adapter_profiles.md` — added query and repository patterns to the database adapter contract
- `src/grain/data/runtime/adapter_profiles.md` — aligned the shipped runtime copy with the updated database adapter patterns
- `tests/test_adapter_config_loader.py` — added parser assertions for the query and repository pattern coverage
- `tests/test_document_adapters_integration.py` — added persistence-oriented database integration coverage
- `tasks/P25-T03-TASK-0167/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P25-T03-TASK-0167/context.md` — recorded the scoped database context for the task
- `tasks/P25-T03-TASK-0167/plan.md` — recorded the implementation and verification approach
- `tasks/P25-T03-TASK-0167/deliverable_spec.md` — recorded the deliverable boundary for the query/ORM slice

## Reviewer Notes
- verify the persistence-aware ordering
- verify the default database bundle remains narrow
- verify the contract/tests stay aligned

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry review and validation guidance into `P25-T04`
