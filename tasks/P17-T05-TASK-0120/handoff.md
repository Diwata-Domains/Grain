# Handoff: TASK-0120

## Final State
`Add ranked impacted-file advisory signals` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0120
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Added ranked impacted-file advisory signals for Phase 17. The graph-derived `affected_files` list remains unchanged, but orchestration scope payloads now also expose semantic-provider resolution, raw semantic scores, and weighted ranking breakdowns for impacted files through a dedicated advisory helper. This keeps the impact contract backward-compatible while making the ranking layer useful outside context selection.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the touched-file vs downstream-file graph-depth heuristic is sufficient for this advisory layer until richer impact distance data exists.
- - Confirm ranked impacted-file payload belongs only in orchestration scope output for now, not the adapter capability domain contract.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/impact_ranking_service.py` — added proposal-only impacted-file ranking helper
- - `src/grain/services/orchestration_service.py` — attached ranked impacted-file metadata to scope-signal payloads
- - `tests/test_impact_ranking_service.py` — added focused impacted-file ranking coverage
- - `tests/test_orchestration_service.py` — asserted ranked impact payload presence
- 

## Reviewer Notes
- - Confirm the touched-file vs downstream-file graph-depth heuristic is sufficient for this advisory layer until richer impact distance data exists.
- - Confirm ranked impacted-file payload belongs only in orchestration scope output for now, not the adapter capability domain contract.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
