# Task: Add adapter metadata fields to task packet templates and parser

## Metadata
- **ID:** TASK-0057
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T04
- **Packet Path:** tasks/P6-T04-TASK-0057/
- **Dependencies:** TASK-0055, TASK-0056
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add optional adapter metadata fields to task packet templates and ensure packet metadata parsing reads these fields without breaking existing packets that do not declare adapters.

## Why This Task Exists
Phase 6 requires packet-level adapter declaration before adapter-aware context assembly can be wired in P6-T05 and P6-T06.

## Scope
- Add `primary_adapter` and `secondary_adapters` metadata fields to packet templates.
- Update packet metadata parsing to expose adapter fields from `task.md`.
- Add tests for parsing adapter fields and legacy packet compatibility.

## Constraints
- Keep adapter fields optional and adapter-neutral by default.
- Do not change canonical docs directly.
- Do not implement context assembly adapter behavior in this packet.

## Escalation Conditions
- If parser changes require canonical packet contract edits before safe implementation, stop and log a change proposal.
- If optional adapter fields cannot degrade safely for legacy packets, stop and record blocker details.
