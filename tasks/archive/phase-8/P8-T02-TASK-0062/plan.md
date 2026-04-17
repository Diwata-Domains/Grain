# Plan: TASK-0062

## Approach

Implement a workflow evaluator service that reads `current_focus.md`, `current_task.md`, and `backlog.md`, then emits either one legal next action or an explicit stop reason with blocking reasons. Keep the evaluator pure/read-only and test it directly through service-level unit tests.

---

## Step 1 — Add Workflow Domain Types

Add a domain model for workflow evaluation output (`next_action`, `stop_reason`, `blocking_reasons`, `recommended_prompt`, `affected_artifacts`) so upcoming CLI commands can consume a stable structure.

---

## Step 2 — Implement Read-Only Evaluator Logic

Implement service logic that:
- validates required workflow docs exist and are parseable
- handles active-task stop gates (`blocked`, `review` with incomplete artifacts)
- resolves next action for no-active-task states (`task_execute`, `task_planning`)
- stops with explicit reasons for ambiguous/conflicting states and phase-boundary close conditions

---

## Step 3 — Add Focused Service Tests

Add unit tests for required-doc failure, blocked task stop, review artifact gate, review-to-close path, single-ready execute path, conflicting ready task stop, planning path, and phase-boundary stop.

---

## Verification

- `.venv/bin/pytest -q tests/test_workflow_state_service.py`
- `.venv/bin/forge task validate --id TASK-0062`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
