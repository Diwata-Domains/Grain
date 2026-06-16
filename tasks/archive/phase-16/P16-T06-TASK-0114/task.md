# Task: Integrate semantic scoring into context selection

## Metadata
- **ID:** TASK-0114
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T06 — Integrate semantic scoring into context selection
- **Packet Path:** tasks/P16-T06-TASK-0114/
- **Dependencies:** TASK-0110, TASK-0111, TASK-0112, TASK-0113
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Wire semantic scoring into `context_service.py` so graph-derived adapter candidates are reranked against the task objective while preserving deterministic source traces, existing source boundaries, and BM25 fallback behavior.

## Why This Task Exists
Phase 16 is supposed to enrich the existing graph-assisted context pipeline, not replace it. This task is the first place the embedding-provider layer affects real workflow output, so it needs to prove that semantic scoring remains advisory and traceable.

## Scope
- resolve the active embedding provider inside context selection
- rank traced adapter candidates against the task objective and keep non-traced candidates stable
- expose semantic-ranking details in bundle metadata and cover the behavior with focused tests

## Constraints
- do not invent new context sources or bypass graph filtering
- keep selection output deterministic and preserve selection traces for every graph-derived file

## Escalation Conditions
- semantic ranking requires a canonical change to context-selection authority rules
- provider integration breaks default BM25 fallback or makes optional providers mandatory
