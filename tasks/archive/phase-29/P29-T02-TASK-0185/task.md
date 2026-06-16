# Task: Add workflow misuse blockers for common off-rails states

## Metadata
- **ID:** TASK-0185
- **Status:** done
- **Phase:** Phase 29 — Workflow Compliance Hardening
- **Backlog:** P29-T02
- **Packet Path:** tasks/P29-T02-TASK-0185/
- **Dependencies:** TASK-0184
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Detect and surface the most common off-rails workflow states earlier so agents and operators stop sooner when `current_task.md`, backlog state, and active packet state have drifted apart.

## Why This Task Exists
Guidance alone does not prevent stale workflow state from accumulating during long sessions. The next hardening step is to block the most common drift patterns before agents continue executing against the wrong task state.

## Scope
- Detect backlog-active work when `current_task.md` is unset.
- Detect clearly invalid active packet/backlog status mismatches.
- Keep the signals read-only and surface them through `workflow next`.

## Constraints
- Do not add hidden state or background processes.
- Keep the enforcement narrow enough to avoid blocking legitimate status progressions that the backlog may lag slightly on.

## Escalation Conditions
- Stop if misuse detection requires rewriting the workflow lifecycle rather than surfacing earlier drift blockers.
