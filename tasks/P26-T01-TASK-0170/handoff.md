# Handoff: TASK-0170

## Final State
`crawler_adapter` profile and contract scaffold is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0170
- **Phase:** Phase 26 — Crawler Adapter
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the first dedicated `crawler_adapter` scaffold so Grain now ships an explicit crawler-oriented adapter profile for crawl-config, selector, extraction-schema, and output-validation work.

## What Was Built
- packet handoff support is ready

## What Review Should Check
- verify that `crawler_adapter` is clearly distinct from generic `code_adapter`
- verify that the contract covers crawl config, selectors, extraction schemas, and output-validation surfaces without overclaiming behavior
- verify that the shipped runtime copy includes the same crawler adapter surface

## What Was Not Done
- crawl-config and selector context-selection behavior remains out of scope for this task
- runtime crawler tooling and execution helpers remain deferred

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused adapter-profile and release-surface tests only
- the first real crawler context behavior belongs to `P26-T02`

## Files Changed
- `docs/runtime/adapter_profiles.md` — added the dedicated `crawler_adapter` profile and inventory entry
- `src/grain/data/runtime/adapter_profiles.md` — added the shipped `crawler_adapter` profile and aligned the bundled adapter inventory
- `tests/test_adapter_config_loader.py` — added focused parser assertions for the crawler adapter contract
- `tasks/P26-T01-TASK-0170/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P26-T01-TASK-0170/context.md` — recorded the scaffold context for the task
- `tasks/P26-T01-TASK-0170/plan.md` — recorded the implementation and verification approach
- `tasks/P26-T01-TASK-0170/deliverable_spec.md` — recorded the deliverable boundary for the crawler scaffold

## Reviewer Notes
- verify the dedicated adapter boundary
- verify the contract is scaffold-only and not broader than the task
- verify the bundled runtime copy stays aligned with the live runtime doc

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry the first crawl-config and selector context behavior into `P26-T02`
