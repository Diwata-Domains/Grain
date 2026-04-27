# Task: Implement OpenAIProvider

## Metadata
- **ID:** TASK-0113
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T05 — Implement `OpenAIProvider`
- **Packet Path:** tasks/P16-T05-TASK-0113/
- **Dependencies:** TASK-0109, TASK-0110
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add an OpenAI-backed semantic provider with optional runtime import, API-key gating, and deterministic fallback behavior when configuration is incomplete. Wire the resolver to use this provider when `grain.embedding_provider` is set to `openai`.

## Why This Task Exists
Phase 16 needs a cloud-backed semantic provider alongside the local options. This task establishes the OpenAI client pattern while keeping the SDK optional and preserving BM25 fallback when the API key or package is unavailable.

## Scope
- add `OpenAIProvider` with embeddings API calls and vector-similarity ranking
- register OpenAI as a built-in resolver option
- add tests for provider scoring, missing API-key handling, and resolver integration

## Constraints
- preserve deterministic fallback to BM25 when OpenAI configuration is incomplete
- keep the OpenAI SDK optional; do not add it to core install requirements
- do not change context-service behavior in this task

## Escalation Conditions
- OpenAI client requirements force a broader config contract change
- cloud-provider integration would require mandatory credentials to proceed
