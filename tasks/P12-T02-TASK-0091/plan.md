# Plan: TASK-0091

## Approach

Build a workflow-loop service that repeatedly evaluates state, applies supervision rules, invokes configured stage commands with prompt paths, and stops with explicit reasons and per-step progress records.

---

## Step 1 — Add Workflow Loop Service

Create `workflow_loop_service.py` with loop control logic, step accounting, agent invocation, and stop-condition payload generation.

---

## Step 2 — Add CLI Surface

Add `grain workflow loop` command with `--steps` and supervision override support, plus text/JSON output for loop progress and stop state.

---

## Step 3 — Add Command Tests

Add command tests covering supervised gate, gated close-stop behavior, invocation/no-state-change behavior, and JSON output schema.

---

## Verification

- `python3 -m py_compile src/grain/cli/workflow.py src/grain/services/workflow_loop_service.py tests/test_workflow_loop_cmd.py`
- `.venv/bin/pytest -q tests/test_workflow_loop_cmd.py tests/test_workflow_run_cmd.py tests/test_workflow_next_cmd.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0091`
- `.venv/bin/pytest -q`
