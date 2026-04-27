# Plan: TASK-0039

## Approach

Implement a minimal markdown parser for `docs/runtime/agent_profiles.md` that maps known sections into typed routing models. Keep the parser tolerant to spacing and non-essential text, but strict about required model class sections. Validate behavior with focused unit tests and run the full test suite for regression safety.

---

## Step 1 — Add routing domain models

Create domain dataclasses representing model profiles, escalation rules, and full routing config so downstream model tasks have a stable typed interface.

---

## Step 2 — Implement model config loader

Add an adapter that loads `docs/runtime/agent_profiles.md`, parses model class sections and escalation rules, and raises typed config/path errors when invalid or missing.

---

## Step 3 — Add parser and loader tests

Cover success path parsing, missing file behavior, and incomplete profile config behavior. Ensure parsed escalation targets and preferred-model mappings are captured correctly.

---

## Verification

Run `.venv/bin/pytest tests/test_model_config_loader.py` and then `.venv/bin/pytest` to verify both task behavior and repo-wide regression safety.
