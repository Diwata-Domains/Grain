# Plan: TASK-0077

## Approach

Expose orchestration service outputs through a new `orchestrate` CLI command group. Keep all behavior read-only except writing inspectable plan artifacts to `docs/working/proposals/`. Reuse existing task/phase planning builders and add adapter filter support so scope and plan commands can be constrained when requested.

---

## Step 1 — Add Scope Analysis Surface

Add a service function for adapter/domain signal analysis and adapter filter validation so `orchestrate scope` can return deterministic text/json outputs.

---

## Step 2 — Add Orchestrate CLI Group

Create `src/grain/cli/orchestrate.py` with:
- `orchestrate scope --scope <text> [--adapter <id> ...]`
- `orchestrate plan --scope <text> [--adapter <id> ...]`

`plan` should write `OrchestratorPlan` JSON to `docs/working/proposals/OP-*.json`.

---

## Step 3 — Register Command and Add Tests

Register the group in root CLI and add coverage for:
- scope text/json
- adapter-filter failure path
- plan artifact creation
- plan JSON payload contract
- command-group help updates

---

## Verification

- `.venv/bin/pytest -q tests/test_orchestrate_cmd.py tests/test_orchestration_service.py tests/test_command_groups.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0077`
- `.venv/bin/pytest -q`
