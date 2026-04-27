# Task: Implement LocalProvider

## Metadata
- **ID:** TASK-0112
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T04 — Implement `LocalProvider`
- **Packet Path:** tasks/P16-T04-TASK-0112/
- **Dependencies:** TASK-0109, TASK-0110
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a sentence-transformers-backed local semantic provider with lazy model loading and graceful degradation when the optional dependency is unavailable. Wire the resolver to use this provider when `grain.embedding_provider` is set to `local`.

## Why This Task Exists
Phase 16 needs a local-only embedding option that does not require a running server. This task establishes the local-model pattern and the optional-dependency fallback behavior for semantic provider resolution.

## Scope
- add `LocalProvider` with lazy model loading and vector-similarity ranking
- register LocalProvider as a built-in resolver option
- add tests for provider scoring, missing dependency handling, and resolver integration

## Constraints
- preserve deterministic fallback to BM25 when the local model dependency is unavailable
- keep the dependency optional; do not add it to core install requirements
- do not change context-service behavior in this task

## Escalation Conditions
- local-model loading requirements force new mandatory dependencies
- resolver support would require hidden downloads or non-local defaults
