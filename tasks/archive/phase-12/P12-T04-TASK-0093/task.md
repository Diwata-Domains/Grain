# Task: Integrate accepted OrchestratorPlan ordering into workflow loop

## Metadata
- **ID:** TASK-0093
- **Status:** done
- **Phase:** Phase 12 — Automated Workflow Loop
- **Backlog:** P12-T04
- **Packet Path:** tasks/P12-T04-TASK-0093/
- **Dependencies:** TASK-0092
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Wire accepted OrchestratorPlan proposals into workflow loop task ordering and add `grain orchestrate accept --plan <id>` for explicit plan acceptance.

## Why This Task Exists
Phase 12 needs orchestration strategy outputs to guide loop execution order when applicable, while preserving backlog fallback behavior.

## Scope
- Add `orchestrate accept` command to mark proposal status as `accepted`.
- Add accepted-plan lookup in loop service for conflicting ready-task selection.
- Add tests for acceptance command and loop ordering behavior.

## Constraints
- Keep integration additive and fallback-safe when no accepted plan exists.
- Do not alter core workflow gate semantics.

## Escalation Conditions
- If accepted plans are malformed or missing usable task refs, loop must fall back to backlog behavior and report gate conditions.
