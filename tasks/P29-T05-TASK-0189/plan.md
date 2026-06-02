# Plan: TASK-0189

## Approach

Close the hardening phase by fixing the parser edge that still caused redirection friction, then lock the hardened operator loop with focused smoke coverage and docs updates in the surfaces agents and humans actually read.

---

## Step 1 — Fix the parser edge

Ensure the phase backlog parser stops at the next top-level section instead of accidentally inheriting later `Status:` lines from non-phase sections.

---

## Step 2 — Expand smoke coverage

Add focused coverage for the parser edge and keep the new `workflow explain` command and existing workflow-next/state tests green together.

---

## Step 3 — Update hardened operator guidance

Update README and runtime guidance so blocked sessions are routed through `grain workflow explain` first and `grain workflow reconcile --dry-run` when the issue is drift.

---

## Verification

Run `PYTHONPATH=src /Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_workflow_explain_cmd.py tests/test_workflow_next_cmd.py tests/test_workflow_state_service.py tests/test_command_groups.py tests/test_release_surface.py`.
