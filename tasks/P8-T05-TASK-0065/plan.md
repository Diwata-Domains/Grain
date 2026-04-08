# Plan: TASK-0065

## Approach

Implement `phase next` as a projection of workflow evaluator state: when no executable tasks remain, emit `phase_review_close`; when task planning is required, emit `phase_planning`; otherwise emit `no_phase_action`. Keep outputs machine-readable and non-mutating.

---

## Step 1 — Add Phase CLI Command Surface

Create a new `phase` CLI group with `next` subcommand and register it in root CLI.

---

## Step 2 — Map Evaluator Outcomes to Phase Actions

Reuse `evaluate_workflow_state` and map its `next_action`/`stop_reason` fields into phase-action outputs with explicit rationale and blockers.

---

## Step 3 — Add Phase Command Tests

Add tests for:
- no-phase-action when task execution remains available
- phase-planning when no ready task exists
- phase-review-close at phase boundary
- JSON output payload contract

---

## Verification

- `.venv/bin/pytest -q tests/test_workflow_state_service.py tests/test_workflow_next_cmd.py tests/test_task_next_cmd.py tests/test_phase_next_cmd.py`
- `.venv/bin/forge task validate --id TASK-0065`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
