# Task: Task-level observability metadata and CLI surfaces

## Metadata
- **ID:** TASK-0175
- **Status:** done
- **Phase:** Phase 27 — Recipe Layer and Operator Ergonomics
- **Backlog:** P27-T01
- **Packet Path:** tasks/P27-T01-TASK-0175/
- **Dependencies:** none
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add a lightweight, packet-local observability surface that records executor identity, model class, stage timestamps, and the last workflow action without introducing hidden state or background services.

## Why This Task Exists
Phase 27 starts with observability because the TUI and later token-budget panels need a stable file-backed source for execution metadata before they can explain current task state.

## Scope
- Add a packet-local `observability.json` service for read/update flows.
- Expose the metadata through `grain task observe` and `grain workflow next`.
- Auto-record runner activation and task-close workflow actions.

## Constraints
- Keep observability packet-local and file-backed only.
- Do not introduce agent supervision, background processes, or hidden runtime state.

## Escalation Conditions
- Stop if the design requires a central event log or non-packet storage.
