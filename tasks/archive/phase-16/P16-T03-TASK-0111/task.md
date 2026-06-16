# Task: Implement OllamaProvider

## Metadata
- **ID:** TASK-0111
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T03 — Implement `OllamaProvider`
- **Packet Path:** tasks/P16-T03-TASK-0111/
- **Dependencies:** TASK-0109, TASK-0110
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add an Ollama-backed semantic provider that fetches embeddings from a local server and ranks candidates by vector similarity. Wire the resolver to use this provider when `grain.embedding_provider` is set to `ollama`, while falling back cleanly to BM25 when the local server is unavailable.

## Why This Task Exists
Phase 16 requires one local-first semantic provider beyond BM25. Ollama is the first networked provider in the sequence and establishes the pattern for provider availability checks and resolver fallback on runtime unavailability.

## Scope
- add `OllamaProvider` with local HTTP embedding requests and cosine-similarity ranking
- register Ollama as a built-in resolver provider
- add tests for provider scoring, unavailable-server status, and resolver integration

## Constraints
- preserve deterministic fallback to BM25 when Ollama is unreachable
- keep the implementation local-first and dependency-light
- do not change context-service behavior in this task

## Escalation Conditions
- Ollama API incompatibility requires changing the provider contract
- local-server reachability checks would force non-local defaults or hidden network assumptions
