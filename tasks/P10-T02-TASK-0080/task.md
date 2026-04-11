# Task: Knowledge graph builder (Layer 3)

## Metadata
- **ID:** TASK-0080
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T02
- **Packet Path:** tasks/P10-T02-TASK-0080/
- **Dependencies:** TASK-0079
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement a JSON knowledge graph builder service that converts structural extraction outputs into typed graph nodes and confidence-labeled edges, and persists inspectable artifacts on disk.

## Why This Task Exists
Phase 10 Layer 3 depends on a rebuildable graph artifact that links files, entities, task packets, docs, and adapters before graph-assisted context selection can be introduced.

## Scope
- Add `graph_service.py` with graph build and persist operations.
- Build graph nodes for files, entities, task packets, canonical docs, runtime docs, and adapters.
- Build graph edges with confidence labels (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`) and typed relations.
- Persist graph artifacts as JSON under working proposals.
- Add tests for graph creation, persistence, payload shape, and input validation.

## Constraints
- Graph artifacts must be deterministic and inspectable.
- Outputs are advisory/proposal artifacts only; no workflow state mutation.

## Escalation Conditions
- If graph schema requirements exceed current Phase 10 plan scope, stop and surface a proposal candidate.
- If graph engine dependency is unavailable at runtime, degrade safely without breaking deterministic artifact output.
