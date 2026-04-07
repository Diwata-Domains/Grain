# Task: Create Packet Template Files

## Metadata
- **ID:** TASK-0020
- **Status:** done
- **Phase:** Phase 3 — Task Packet System
- **Backlog:** P3-T02
- **Dependencies:** none

## Objective
Create the six individual packet file templates under `templates/tasks/`: `task.md`, `context.md`, `plan.md`, `deliverable_spec.md`, `results.md`, and `handoff.md`. These are the scaffold sources used by `abt task create` (P3-T04) when initializing a new packet directory.

## Why This Task Exists
`abt task create` needs to render each packet file from a template. The template loader (`templates/loader.py`) reads from `templates/<name>`. The individual per-file templates must exist before directory creation and CLI creation commands can be implemented.

## Source Documents
- `docs/canonical/data_contracts.md` — Section 8 (required packet files), Section 9 (metadata contract)
- `docs/canonical/workflow_spec.md` — Section 6 (file responsibilities)

## Constraints
- Templates are plain markdown — no rendering engine (Q9 resolved)
- Each template must contain the minimum structure for its file role
- `task.md` template must include the required metadata block (ID, Status, Phase, Dependencies)
- Templates live in `templates/tasks/` — do not modify `templates/tasks/task_packet.md`
- Do not create service or CLI code in this task

## Escalation Conditions
- None anticipated
