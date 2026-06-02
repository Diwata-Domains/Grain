# Handoff: TASK-0168

## Final State
`Database review and validation guidance` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0168
- **Phase:** Phase 25 — Database Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the shipped database review-guidance slice so Grain now calls out `database_adapter` and the core database review risks in operator-facing docs.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify the shipped docs mention `database_adapter`
- verify destructive migrations, rollback expectations, and schema/query drift are explicit
- verify the guidance stays packet-first and does not imply live database execution features

## What Was Not Done
- new database commands or runtime tooling were not added
- phase-close smoke/docs work remains out of scope for this task

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused release-surface, adapter-profile, and database integration tests only
- the final closeout task (`P25-T05`) still needs to land

## Files Changed
- `README.md` — added packet-first database workflow guidance
- `docs/runtime/AGENTS.md` — added runtime database review and validation guidance
- `docs/runtime/CLAUDE.md` — added Claude-side database workflow guidance
- `tests/test_release_surface.py` — added regression assertions for the shipped database guidance
- `tasks/P25-T04-TASK-0168/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P25-T04-TASK-0168/context.md` — recorded the scoped database review-guidance context
- `tasks/P25-T04-TASK-0168/plan.md` — recorded the implementation and verification approach
- `tasks/P25-T04-TASK-0168/deliverable_spec.md` — recorded the deliverable boundary for the database review-guidance slice

## Reviewer Notes
- verify the shipped-doc boundary
- verify the explicit risk language
- verify no live execution surface is implied

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry the final smoke/docs closeout into `P25-T05`
