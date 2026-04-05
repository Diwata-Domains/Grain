# Plan: TASK-0041

## Approach

Implement `model show` directly in the CLI layer using the existing model-profile adapter and domain models, then add focused command tests for text and JSON output contracts and missing-config behavior. Keep scope tight to display-only behavior.

---

## Step 1 — Implement `model show` command output

Load model profiles from runtime config, render readable text output listing class capabilities, and provide JSON output that serializes profiles and escalation rules for automation consumers.

---

## Step 2 — Add CLI command tests

Add tests for successful text output, JSON shape/content, and missing profile file failure path.

---

## Step 3 — Validate and finalize task artifacts

Run targeted model tests and the full suite, then update task packet artifacts for reviewer handoff.

---

## Verification

Run `.venv/bin/pytest tests/test_model_show_cmd.py tests/test_model_service.py tests/test_model_config_loader.py` and `.venv/bin/pytest`.
