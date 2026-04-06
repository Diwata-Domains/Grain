# Deliverable Spec: TASK-0049

## Required Deliverables
- A working `forge review summary` command.
- Structured text output that shows packet state, validation findings, and next actions.
- JSON output that serializes the same information predictably.
- Tests covering success, blockers, and missing packets.

## Acceptance Criteria
- The command must succeed for existing packets even if validation findings are present.
- Missing packets must fail cleanly.
- Output must stay packet-scoped and read-only.
