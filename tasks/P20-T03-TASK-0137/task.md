# Task: Treat completed current task state as non-active workflow state

## Metadata
- **ID:** TASK-0137
- **Status:** review
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T03
- **Packet Path:** tasks/P20-T03-TASK-0137/
- **Dependencies:** TASK-0135
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Harden workflow evaluation so a `done` packet referenced by `current_task.md` is treated as non-active state immediately instead of requiring a separate reconcile pass before the workflow can progress.

## Why This Task Exists
After closing a task, Grain could keep routing against the completed packet until `workflow reconcile --fix` reset `current_task.md`. That makes the evaluator overly dependent on manual cleanup instead of recognizing terminal task state itself.

## Scope
- Update workflow evaluation to ignore a stale `current_task.md` pointer when the referenced packet is already `done`.
- Add regression coverage proving the evaluator can continue to the next ready task without a separate reconcile step.

## Constraints
- Preserve existing blocked / needs-fix / review semantics for genuinely active tasks.
- Keep the evaluator read-only; do not mutate `current_task.md` inside `workflow next`.

## Escalation Conditions
- If resolving stale done pointers requires mutating repo state inside evaluation, stop and reassess rather than weakening the read-only contract.
