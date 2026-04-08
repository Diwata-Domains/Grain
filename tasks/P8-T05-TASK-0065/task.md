# Task: Add forge phase next

## Metadata
- **ID:** TASK-0065
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T05
- **Packet Path:** tasks/P8-T05-TASK-0065/
- **Dependencies:** TASK-0062, TASK-0063, TASK-0064
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add `forge phase next` to surface whether phase-level planning/review-close/no-phase-action is currently appropriate using deterministic evaluator signals.

## Why This Task Exists
After `workflow next` and `task next`, Phase 8 needs a phase-level operator surface so automation and humans can distinguish task-level progression from phase-boundary planning/review actions.

## Scope
- Add new `phase` CLI group with `next` subcommand.
- Map evaluator outcomes into phase actions (`phase_planning`, `phase_review_close`, `no_phase_action`).
- Add command tests for all major phase-action paths and JSON output.

## Constraints
- Keep the command read-only; no workflow/task/phase mutation.
- Preserve one-step/explicit-stop contract semantics already locked in `P8-T01`.

## Escalation Conditions
- If phase action cannot be determined from evaluator state without heuristics, report explicit stop details instead of inferring behavior.
- If required semantics conflict with canonical workflow boundaries, route to change-proposal flow.
