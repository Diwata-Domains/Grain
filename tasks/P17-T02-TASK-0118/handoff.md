# Handoff: TASK-0118

## Final State
`Build deterministic ranking service` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0118
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the shared Phase 17 ranking service. The service accepts normalized candidate inputs, converts graph depth into a stable score, clamps advisory inputs to `[0, 1]`, combines graph distance, semantic similarity, authority, and packet priority using the ranking contracts from P17-T01, and returns fully inspectable `RankedCandidate` results with deterministic tie-breaking.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the graph-distance normalization shape is the intended baseline for Phase 17 consumers.
- - Confirm out-of-range semantic and packet-priority inputs should continue clamping rather than erroring.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/ranking_service.py` — added deterministic weighted ranking logic and signal normalization helpers
- - `tests/test_ranking_service.py` — added focused coverage for ordering, tie-breaking, and score clamping
- 

## Reviewer Notes
- - Confirm the graph-distance normalization shape is the intended baseline for Phase 17 consumers.
- - Confirm out-of-range semantic and packet-priority inputs should continue clamping rather than erroring.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
