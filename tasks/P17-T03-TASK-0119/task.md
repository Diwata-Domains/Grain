# Task: Integrate ranked scoring into context selection

## Metadata
- **ID:** TASK-0119
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T03 — Integrate ranked scoring into context selection
- **Packet Path:** tasks/P17-T03-TASK-0119/
- **Dependencies:** TASK-0118
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Replace the semantic-only adapter-source reranking in `context_service.py` with the new ranking service so context selection emits deterministic weighted breakdowns while preserving existing traces and source boundaries.

## Why This Task Exists
Phase 17 needs to prove the ranking layer affects real workflow output. Context selection is the first consumer, and it already has graph and semantic data available from Phase 10 and Phase 16.

## Scope
- integrate `ranking_service.py` into adapter-source reranking
- expose ranked score breakdowns in context bundle metadata
- preserve graph traces and stable source inclusion behavior

## Constraints
- do not invent new context sources or bypass graph-trace requirements
- ranking output must stay explainable and deterministic for review

## Escalation Conditions
- context-selection ranking requires a canonical change to source-authority semantics
- service integration breaks the Phase 16 semantic fallback contract
