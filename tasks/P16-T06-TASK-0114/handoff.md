# Handoff: TASK-0114

## Final State
`Integrate semantic scoring into context selection` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0114
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Integrated the Phase 16 semantic provider layer into context selection. The context service now extracts the task objective from `task.md`, resolves the configured embedding provider with normal BM25 fallback behavior, reranks only graph-traced adapter candidates, and records provider/fallback/score details in the exported adapter context. Existing source boundaries and graph traces remain intact.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the bundle-level semantic metadata shape is sufficient for the planned `grain embedding show` and later integration coverage.
- - Confirm using the task objective as the semantic query is the intended long-term ranking input for context selection.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/context_service.py` — integrated semantic reranking into graph-assisted adapter source selection and added semantic metadata export
- - `tests/test_context_build.py` — added coverage proving traced adapter sources are reranked semantically without losing traceability
- 

## Reviewer Notes
- - Confirm the bundle-level semantic metadata shape is sufficient for the planned `grain embedding show` and later integration coverage.
- - Confirm using the task objective as the semantic query is the intended long-term ranking input for context selection.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
