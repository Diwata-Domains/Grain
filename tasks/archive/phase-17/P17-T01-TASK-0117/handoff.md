# Handoff: TASK-0117

## Final State
`Add ranking domain model and score breakdown contracts` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0117
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Defined the Phase 17 ranking contract layer. The new domain module introduces explicit score components, ranked candidates, default signal weights, and a normalized authority-scoring helper so later ranking services can remain deterministic and inspectable. The public `grain.domain` exports now include the ranking types and defaults.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the default weight split is the intended starting point for Phase 17 service work.
- - Confirm the normalized authority-score mapping is acceptable as a contract-layer default rather than only a service-layer concern.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/domain/ranking.py` — added deterministic ranking contracts, default weights, and authority scoring helper
- - `src/grain/domain/__init__.py` — exported ranking contracts through the public domain surface
- - `tests/test_ranking_domain.py` — added focused ranking-domain coverage
- 

## Reviewer Notes
- - Confirm the default weight split is the intended starting point for Phase 17 service work.
- - Confirm the normalized authority-score mapping is acceptable as a contract-layer default rather than only a service-layer concern.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
