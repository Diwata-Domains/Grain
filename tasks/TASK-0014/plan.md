# Plan: TASK-0014

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Requires encoding rules from two canonical sources (data_contracts.md and PROJECT_RULES.md) and reasoning about which checks belong here vs. in manifest_validator.py.

## Steps

1. Create `src/ai_build_toolkit/validators/authority_validator.py`:
   - Define `ALLOWED_AUTHORITY_VALUES` from `data_contracts.md` Section 6.2
   - Implement `validate_authority(registry: DocumentRegistry, manifest: dict) -> list[str]`:
     - For every record: check `authority` is in `ALLOWED_AUTHORITY_VALUES`
     - For canonical layer records: check `editable_by_agents is False`
     - Check `manifest.get("rules", {}).get("authority_order")` is a non-empty list

2. Write tests in `tests/test_authority_validator.py`:
   - Valid registry and manifest returns empty list
   - Invalid `authority` value returns error with record id
   - Canonical record with `editable_by_agents: True` returns error
   - Non-canonical record with `editable_by_agents: True` does not trigger error
   - Missing `authority_order` in rules returns error
   - Empty `authority_order` list returns error
   - Multiple violations return one error per violation

## Patch Strategy
- New file: `src/ai_build_toolkit/validators/authority_validator.py`
- New file: `tests/test_authority_validator.py`
- No other files touched
