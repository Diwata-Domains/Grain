# Task: Route executed tasks to review instead of execute

## Metadata
- **ID:** TASK-0135
- **Status:** done
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T01
- **Packet Path:** tasks/P20-T01-TASK-0135/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Update Grain's workflow evaluation so an active task with recorded execution output routes into review instead of continuing to surface `task_execute`.

## Why This Task Exists
Cross-project field usage showed that once `results.md` exists for an active in-progress task, Grain still reports `task_execute`. That breaks the intended Execute -> Review -> Close lifecycle and causes prompt selection and runner gating to drift from the actual packet state.

## Scope
- Change workflow evaluation to return an explicit review step when execution artifacts already exist for the active task.
- Update runner and prompt-facing behavior to gate on review and add regression coverage for the new state.

## Constraints
- Preserve the one-step guarded workflow model and keep machine-readable outputs stable.
- Do not skip directly to close; tasks in `review` status must still route to `task_close` with the existing review-artifact checks.

## Escalation Conditions
- If the current workflow contract has hidden dependencies on `task_execute` after `results.md` exists, stop and reconcile that contract before widening the state machine.
