# Task: Add workflow loop guardrails and documentation

## Metadata
- **ID:** TASK-0092
- **Status:** done
- **Phase:** Phase 12 — Automated Workflow Loop
- **Backlog:** P12-T03
- **Packet Path:** tasks/P12-T03-TASK-0092/
- **Dependencies:** TASK-0091
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add workflow loop guardrails (`--dry-run`, default step safety cap, clearer progress logging) and update docs to clarify supervision-level behavior and autonomous risk.

## Why This Task Exists
Phase 12 requires safety-focused controls and explicit operator guidance before broader loop adoption.

## Scope
- Add `--dry-run` command behavior for loop preview.
- Add default max-step guardrail and progress/log detail fields.
- Update runtime and README documentation for supervision-level clarity.
- Add loop tests for dry-run and updated payload/output fields.

## Constraints
- Keep behavior changes scoped to loop command/service and docs.
- Do not implement orchestrator integration in this task.

## Escalation Conditions
- If guardrail behavior conflicts with canonical workflow gate semantics, preserve gate semantics and record follow-up.
