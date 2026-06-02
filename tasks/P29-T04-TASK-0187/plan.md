# Plan: TASK-0187

## Approach

Add a thin `workflow explain` surface over the existing evaluator, map common workflow gates to concrete operator guidance, and lock the behavior with focused command coverage.

---

## Step 1 — Add a read-only diagnostic service

Build a small service that consumes `evaluate_workflow_state(...)` and translates stop reasons / next actions into operator-facing summaries, recommended actions, and suggested commands.

---

## Step 2 — Wire the workflow CLI surface

Add `grain workflow explain` as a thin CLI wrapper that supports both text and JSON output without duplicating workflow logic.

---

## Step 3 — Verify with focused command coverage

Add tests for actionable, blocked, and JSON diagnostic cases, plus command-group coverage for the new subcommand.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_workflow_explain_cmd.py tests/test_command_groups.py tests/test_workflow_next_cmd.py tests/test_workflow_state_service.py`.
