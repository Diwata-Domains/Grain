# Task: Tree-sitter structural entity extraction (Layer 1)

## Metadata
- **ID:** TASK-0079
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T01
- **Packet Path:** tasks/P10-T01-TASK-0079/
- **Dependencies:** TASK-0078
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement deterministic structural entity extraction for Phase 10 Layer 1, covering code/frontend/docs/devops source shapes and emitting normalized structural entity records.

## Why This Task Exists
Phase 10 requires a local structural extraction layer before graph building and graph-assisted context selection can be implemented.

## Scope
- Add a new structural intelligence service module under `src/grain/services/`.
- Implement extraction for:
  - code/frontend: functions, classes, imports, call sites
  - docs: heading/link cross-reference signals
  - devops: dependency declaration signals
- Provide normalized extraction output records and batch extraction helper.
- Add service tests covering each adapter-relevant source category.
- Add tree-sitter runtime dependency declaration in project metadata for Phase 10 workstream.

## Constraints
- Deterministic and local-only extraction; no LLM usage and no remote calls.
- Output remains proposal/intelligence data only and must not mutate workflow state.

## Escalation Conditions
- If extraction requirements require canonical contract changes before implementation, stop and log a proposal candidate.
- If dependency/runtime constraints prevent deterministic local extraction, stop and log the blocker explicitly.
