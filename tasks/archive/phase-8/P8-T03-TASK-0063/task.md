# Task: Add forge workflow next

## Metadata
- **ID:** TASK-0063
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T03
- **Packet Path:** tasks/P8-T03-TASK-0063/
- **Dependencies:** TASK-0062
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a `forge workflow next` CLI command that reports one next legal workflow action or an explicit stop reason in both text and JSON formats, backed by the read-only workflow state evaluator.

## Why This Task Exists
Phase 8 requires machine-readable workflow guidance surfaces. `P8-T03` is the first CLI command that exposes evaluator decisions from `P8-T02` to operators and agents.

## Scope
- Add a new `workflow` CLI group with a `next` subcommand.
- Wire the command to `evaluate_workflow_state` and emit structured text/JSON output.
- Add command tests for normal next-action and stop-reason paths.

## Constraints
- Keep the command read-only; it must not mutate task/phase/backlog state.
- Preserve one-step runner contract semantics (explicit stop reasons, deterministic next action).

## Escalation Conditions
- If evaluator output cannot be mapped to stable machine-readable fields, stop and log a blocking issue.
- If command behavior would require canonical workflow changes, route via change proposal instead of silent behavior drift.
