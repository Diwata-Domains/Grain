# Task: Make task IDs globally monotonic across archived packets

## Metadata
- **ID:** TASK-0136
- **Status:** done
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T02
- **Packet Path:** tasks/P20-T02-TASK-0136/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Update `next_task_id()` so packet ID allocation remains globally monotonic after phase archiving by including archived packet directories when scanning for the highest assigned `TASK-####`.

## Why This Task Exists
Field usage showed that Grain can reuse bare task IDs after archiving because archived packets under `tasks/archive/` are currently ignored. That breaks the expectation that `TASK-####` identifiers remain globally monotonic across the life of the repo.

## Scope
- Update the ID allocator to include archived packet directories when computing the next task ID.
- Add regression tests covering archived packets and archive container directories.

## Constraints
- Keep task ID allocation deterministic and filesystem-local.
- Do not change packet naming conventions or phase archive layout as part of this task.

## Escalation Conditions
- If archive directory traversal introduces a performance or compatibility issue in normal packet creation flows, stop and reassess the scanning approach before broadening the change.
