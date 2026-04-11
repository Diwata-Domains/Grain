# Task: Graph-assisted context selection (Layer 4)

## Metadata
- **ID:** TASK-0081
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T03
- **Packet Path:** tasks/P10-T03-TASK-0081/
- **Dependencies:** TASK-0080
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Replace adapter glob-only context selection in `context_service.py` with graph-assisted traversal so included adapter sources are structurally connected to packet-local files and traceable.

## Why This Task Exists
Phase 10 Layer 4 requires graph-driven context inclusion to reduce non-relevant file loading and make every inclusion explainable by a structural path.

## Scope
- Update context selection flow to use graph traversal from packet-local files to adapter candidate files.
- Keep packet-local files preferred, then include only graph-connected adapter files.
- Record graph selection traces for each included adapter source path.
- Preserve deterministic local behavior and adapter hint metadata outputs.
- Add/update tests for graph-assisted adapter source selection and traceability.

## Constraints
- No hidden inclusions: every graph-selected file must include a trace path.
- Keep output machine-readable and deterministic.
- No workflow/canonical mutation behavior added.

## Escalation Conditions
- If traversal requirements need graph schema changes outside current Layer 4 scope, stop and log proposal candidate.
- If graph build is unavailable, degrade safely without introducing implicit or unverifiable inclusions.
