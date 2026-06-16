# Handoff: TASK-0115

## Final State
`Add grain embedding show` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0115
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Added `grain embedding show` so the active semantic-provider state is inspectable from the CLI. The command reports configured and active providers, configured and active models, fallback activity, and provider availability/detail in both text and JSON output. The implementation uses a thin service boundary on top of `EmbeddingProviderResolver`, so it stays aligned with the same resolution rules used elsewhere in Phase 16.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the text output field names are the right long-term CLI surface for Phase 16 provider inspection.
- - Confirm provider availability should remain tied to the provider status contract rather than triggering separate reachability checks in the command.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/embedding_service.py` — added repo-level embedding-provider inspection helper
- - `src/grain/cli/embedding.py` — added `embedding show` text and JSON output
- - `src/grain/cli/__init__.py` — registered the embedding CLI group
- - `tests/test_embedding_show_cmd.py` — added command output coverage
- 

## Reviewer Notes
- - Confirm the text output field names are the right long-term CLI surface for Phase 16 provider inspection.
- - Confirm provider availability should remain tied to the provider status contract rather than triggering separate reachability checks in the command.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
