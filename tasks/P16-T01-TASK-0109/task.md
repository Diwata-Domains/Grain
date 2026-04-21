# Task: Define embedding domain model, resolver, and config surface

## Metadata
- **ID:** TASK-0109
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T01 — Define embedding domain model, resolver, and config surface
- **Packet Path:** tasks/P16-T01-TASK-0109/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the semantic-scoring contract layer for Phase 16. This task defines the embedding domain types, extends manifest config parsing to cover all planned providers and model fields, and adds a resolver service that applies provider-selection and BM25 fallback rules without requiring provider-specific integrations yet.

## Why This Task Exists
Phase 16 cannot proceed safely until the repo has a stable provider contract and config surface. BM25, Ollama, Local, and OpenAI all need to plug into the same resolver path, and the rest of the semantic layer depends on these types staying stable across later implementation tasks.

## Scope
- define `EmbeddingProvider`, `ScoredCandidate`, provider status, and resolution result domain types
- extend `GrainConfig` and manifest parsing for `embedding_provider` plus provider-specific model settings
- add an `EmbeddingProviderResolver` service with deterministic BM25 fallback behavior
- add tests covering config parsing, fallback resolution, and domain defaults

## Constraints
- keep the semantic layer advisory only; this task must not mutate context-selection behavior yet
- preserve deterministic local fallback behavior when the configured provider is unavailable or unsupported
- avoid adding new required dependencies in this slice

## Escalation Conditions
- provider-specific runtime requirements force canonical or workflow-contract changes
- resolver design requires non-deterministic fallback behavior to make progress
