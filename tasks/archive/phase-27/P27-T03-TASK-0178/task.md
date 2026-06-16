# Task: TUI observability and context-cost panels

## Metadata
- **ID:** TASK-0178
- **Status:** done
- **Phase:** Phase 27 — Recipe Layer and Operator Ergonomics
- **Backlog:** P27-T03
- **Packet Path:** tasks/P27-T03-TASK-0178/
- **Dependencies:** TASK-0175, TASK-0177
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Extend the Textual shell so operators can inspect task observability metadata, context-cost summaries, and recent packet-result changes without leaving the TUI.

## Why This Task Exists
Phase 27 ends by wiring the new observability and token-budget data into the TUI, proving the shell remains a thin interface over existing packet and service state.

## Scope
- Add an observability panel to the TUI.
- Extend the context panel with token-budget and trim-hint data.
- Show recent packet result summary text in the packet inspector.

## Constraints
- Reuse existing packet-local files and context metadata.
- Do not add hidden UI-only state or alternate workflow logic.

## Escalation Conditions
- Stop if the TUI needs to compute data that is not already available from Grain services or packet files.
