# Task: Integrate grain suggest into grain workflow next

## Metadata
- **ID:** TASK-0216
- **Status:** done
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T05
- **Packet Path:** tasks/P32-T05-TASK-0216/
- **Dependencies:** TASK-0213
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
When `grain workflow next` evaluates the workspace and finds no obvious next task (e.g. stop reason `no_ready_tasks` / `backlog_empty`), run the suggest engine and surface the top candidate inline. Surface-only: nothing is written until `grain suggest accept <id>` is called.

## Why This Task Exists
Closes the proactive loop: the operator never hits a dead end. When the workflow has no legal next step, Grain proposes one instead of just stopping.

## Scope / Implementation Steps
1. In `src/grain/services/workflow_service.py`, when evaluation yields a no-ready-task stop reason, call `suggest_service.generate` (or a read-only `top_suggestion`) and attach the top candidate to the evaluation.
2. Text output: render an inline suggestion block. JSON output: add a `suggestion` field on the workflow-next payload.
3. Guarantee no side effects — surfacing must not persist proposals if that would surprise the runner (decide per suggest_spec; prefer read-only surface, persist only on `grain suggest`).

## Acceptance Criteria
- `grain workflow next` with no ready task surfaces the top suggestion in text and as a `suggestion` JSON field.
- Surfacing writes nothing that `accept` would later need to undo.
- Existing workflow-next stop reasons and outputs are unchanged when a ready task exists.
- No regression: full suite green.

## Tests
- `tests/test_workflow_next_suggestion.py` — suggestion surfaced on empty/no-ready state; absent when a ready task exists; JSON field present; no writes.

## Constraints
- Surface-only; the approval gate stays in `grain suggest accept`.
- Deterministic.

## Escalation Conditions
- Suggest engine errors must not break `grain workflow next` — degrade to the plain stop reason.
