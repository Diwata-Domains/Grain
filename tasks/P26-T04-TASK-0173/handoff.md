# Handoff: TASK-0173

## Final State
`Crawler review and safety guidance` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0173
- **Phase:** Phase 26 — Crawler Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the shipped crawler review-guidance slice so Grain now calls out `crawler_adapter` and the core crawler review risks in operator-facing docs.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify the shipped docs mention `crawler_adapter`
- verify robots constraints, rate-limit/retry risks, selector brittleness, and extraction drift are explicit
- verify the guidance stays packet-first and does not imply live crawler execution features

## What Was Not Done
- new crawler commands or runtime tooling were not added
- phase-close smoke/docs work remains out of scope for this task

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused release-surface, adapter-profile, and crawler integration tests only
- the final closeout task (`P26-T05`) still needs to land

## Files Changed
- `README.md` — added packet-first crawler workflow guidance
- `docs/runtime/AGENTS.md` — added runtime crawler review and safety guidance
- `docs/runtime/CLAUDE.md` — added Claude-side crawler workflow guidance
- `tests/test_release_surface.py` — added regression assertions for the shipped crawler guidance
- `tasks/P26-T04-TASK-0173/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P26-T04-TASK-0173/context.md` — recorded the scoped crawler review-guidance context
- `tasks/P26-T04-TASK-0173/plan.md` — recorded the implementation and verification approach
- `tasks/P26-T04-TASK-0173/deliverable_spec.md` — recorded the deliverable boundary for the crawler safety-guidance slice

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
- carry the final smoke/docs closeout into `P26-T05`
