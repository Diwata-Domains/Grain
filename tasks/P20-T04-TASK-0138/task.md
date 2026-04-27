# Task: Add a recognized terminal project-complete workflow state

## Metadata
- **ID:** TASK-0138
- **Status:** done
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T04
- **Packet Path:** tasks/P20-T04-TASK-0138/
- **Dependencies:** TASK-0135, TASK-0137
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a recognized terminal project-complete state so `workflow next` and related phase surfaces stop cleanly when a repo is intentionally complete instead of failing phase parsing.

## Why This Task Exists
Field usage showed that marking a project complete in `current_focus.md` currently causes `required_docs_invalid` because the phase parser only understands numbered phases. Grain needs a deterministic terminal no-op state for completed projects.

## Scope
- Extend current phase parsing to recognize a terminal `complete` state.
- Surface that state through workflow evaluation and phase-next output as a clean no-op rather than a parse error.

## Constraints
- Keep the workflow evaluator read-only and deterministic.
- Do not add a new task-level action for a complete project; this should be an explicit stop condition.

## Escalation Conditions
- If terminal-state support requires widening multiple command contracts beyond evaluation and phase-next, stop and narrow the change rather than broadening Phase 20 scope.
