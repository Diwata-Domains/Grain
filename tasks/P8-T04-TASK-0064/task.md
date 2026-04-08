# Task: Add forge task next

## Metadata
- **ID:** TASK-0064
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T04
- **Packet Path:** tasks/P8-T04-TASK-0064/
- **Dependencies:** TASK-0062, TASK-0063
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add `forge task next` to identify the next actionable task candidate from current workflow state, or explicitly report when planning is required first.

## Why This Task Exists
After `workflow next` (`P8-T03`), operators need a task-focused selection surface that can be consumed directly by execution loops without hidden selection logic.

## Scope
- Implement `task next` command on the existing `task` CLI group.
- Reuse workflow evaluator outputs to select one ready task deterministically.
- Add CLI tests for candidate selection, planning-required, and JSON output paths.

## Constraints
- Keep selection read-only; do not mutate backlog/current-task/task packets.
- Preserve explicit stop/planning signals rather than silently choosing from ambiguous states.

## Escalation Conditions
- If task selection requires non-deterministic tie-breaking, surface explicit stop reasons instead of hidden heuristics.
- If command contract needs canonical workflow changes, route through change proposal flow before altering behavior.
