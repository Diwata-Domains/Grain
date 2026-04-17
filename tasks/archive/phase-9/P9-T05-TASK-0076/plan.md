# Plan: TASK-0076

## Approach

Add a dedicated `adapter` command group with read-only profile inspection commands (`list`, `show`) backed by adapter runtime config loader. Keep output deterministic in both text and JSON formats and cover behavior with command-level tests.

---

## Step 1 — Add Adapter CLI Group

Create `src/grain/cli/adapter.py` and implement:
- `adapter list`
- `adapter show --id`
Register the group in root CLI.

---

## Step 2 — Add Output Contracts

Ensure text output is operator-readable and JSON output includes structured fields for automation (`profiles`, `adapter`, `source_path`).

---

## Step 3 — Add Command Tests

Add command tests for:
- list text/json
- show text/json
- unknown adapter id exit behavior
- command group/subcommand help coverage updates

---

## Verification

- `.venv/bin/pytest -q tests/test_adapter_cmd.py tests/test_command_groups.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0076`
- `.venv/bin/pytest -q`
