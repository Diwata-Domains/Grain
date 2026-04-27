# Handoff: TASK-0119

## Final State
`Integrate ranked scoring into context selection` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0119
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Integrated the Phase 17 ranking service into context selection. The context service still resolves semantic providers and preserves graph-trace filtering, but now converts traced adapter sources into ranking inputs and orders them through the shared weighted ranking engine. Bundle metadata now exposes both raw semantic scores and the final ranked score breakdown that drove source ordering.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the default packet-priority heuristic (source files before tests) is the right baseline inside the ranking layer.
- - Confirm unknown non-doc source authority should remain neutral until a stronger source-authority model exists.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/context_service.py` — replaced semantic-only path ordering with the shared ranking service and added ranked score metadata
- - `tests/test_context_build.py` — asserted ranked score breakdown metadata for context selection
- 

## Reviewer Notes
- - Confirm the default packet-priority heuristic (source files before tests) is the right baseline inside the ranking layer.
- - Confirm unknown non-doc source authority should remain neutral until a stronger source-authority model exists.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
