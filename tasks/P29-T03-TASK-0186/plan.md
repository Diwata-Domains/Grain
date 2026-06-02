# Plan: TASK-0186

## Approach

Hydrate the auto-created packet immediately after `workflow run` creates it, then sync packet and backlog status to `in_progress` so the activation path stops producing placeholder packets and obvious state drift.

---

## Step 1 — Hydrate created packet templates

When `workflow run` auto-creates a packet, replace the key template placeholders in `task.md`, `context.md`, `plan.md`, and `deliverable_spec.md` with deterministic bootstrap content instead of leaving raw scaffolding on disk.

---

## Step 2 — Sync activation state

As part of activation, move the packet `task.md` status and the matching backlog entry to `in_progress` so the active-task state on disk agrees with the runner’s activation decision.

---

## Step 3 — Lock the behavior with focused tests

Add focused workflow-run and runner-integration coverage for hydrated packet creation, status sync, and the updated review gate expectations.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_workflow_run_cmd.py tests/test_runner_integration.py tests/test_workflow_state_service.py`.
