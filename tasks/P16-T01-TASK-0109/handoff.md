# Handoff: TASK-0109

## Final State
`Define embedding domain model, resolver, and config surface` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0109
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 16 contract/config slice for semantic enrichment. The repo now has a dedicated embedding domain module, a provider resolver service, manifest support for `none`, `ollama`, `local`, and `openai`, and provider-specific model fields with defaults. The resolver currently falls back deterministically to a local BM25-style lexical scorer when a configured provider is unavailable or not yet registered, which keeps the semantic layer usable without introducing new required dependencies in this task.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Verify that adding the `grain:` block to `docs/runtime/docs_manifest.yaml` is acceptable for this repo's runtime-doc baseline.
- - Inspect whether the lexical fallback should remain internal to the resolver or move into a dedicated `BM25Provider` module in `P16-T02`.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/domain/embedding.py` — added semantic-scoring provider protocol and resolution/result types
- - `src/grain/services/embedding_resolver.py` — added provider resolution with deterministic BM25 fallback behavior
- - `src/grain/adapters/manifest.py` — extended `GrainConfig` and manifest parsing for semantic provider settings
- - `src/grain/domain/__init__.py` — exported embedding domain types
- - `src/grain/data/runtime/docs_manifest.yaml` — exposed semantic provider config in the bundled runtime template
- - `docs/runtime/docs_manifest.yaml` — exposed semantic provider config in this repo's runtime manifest
- - `tests/test_grain_config.py` — covered new config defaults and provider-model parsing
- - `tests/test_embedding_domain.py` — covered domain defaults and resolution metadata
- - `tests/test_embedding_resolver.py` — covered fallback resolution and deterministic lexical scoring
- 

## Reviewer Notes
- - Verify that adding the `grain:` block to `docs/runtime/docs_manifest.yaml` is acceptable for this repo's runtime-doc baseline.
- - Inspect whether the lexical fallback should remain internal to the resolver or move into a dedicated `BM25Provider` module in `P16-T02`.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
