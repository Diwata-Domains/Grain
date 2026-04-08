# Plan: TASK-0056

## Approach

Implement a markdown parser for adapter profiles that mirrors the existing model profile loader style: load runtime markdown from a fixed path, parse profile sections into domain objects, and raise explicit config errors when required contract elements are missing.

## Model Selection
- `open_model` is appropriate because this is narrow, mechanical parser work with low ambiguity.

---

## Step 1 — Build loader module

Create `src/forge/adapters/adapter_config.py` with `load_adapter_profiles()` and `parse_adapter_profiles_markdown()` using `MissingPathError` and `ConfigError` for failure paths.

---

## Step 2 — Implement contract validation

Validate required fields (`adapter_id`, `domain_type`, `applies_to`) and required hint presence (`context_priority_rules` or `test_or_validation_hints`) while parsing profile sections.

---

## Step 3 — Add tests and verify

Add focused tests for successful parse/load and key failure modes (missing required field, missing hint section, missing runtime file), then run focused and full test suites.

---

## Verification

Run:
- `./.venv/bin/pytest -q tests/test_adapter_config_loader.py`
- `./.venv/bin/pytest -q`
