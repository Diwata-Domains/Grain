# Results: TASK-0014

## Status
done

## Files Changed
- `src/ai_build_toolkit/validators/authority_validator.py` — new file
- `tests/test_authority_validator.py` — new file, 17 tests

## Summary
Implemented authority-order validator. Checks three rules: (1) each record's
`authority` value is from the allowed set defined in data_contracts.md Section
6.2; (2) canonical-layer records have `editable_by_agents: False`; (3)
`rules.authority_order` in the manifest is a non-empty list. Working and
runtime records with `editable_by_agents: True` are correctly permitted.
Never raises — always returns a list.

## Test Results
17/17 new tests passing. 136/136 total passing (no regressions).

## Deliverable Checklist
- [x] `validators/authority_validator.py` exists
- [x] `validate_authority(registry, manifest)` implemented
- [x] Empty list for valid inputs
- [x] Invalid authority value detected with record id
- [x] Canonical + editable_by_agents=True detected
- [x] Non-canonical editable_by_agents=True does not error
- [x] Missing/empty authority_order detected
- [x] Never raises
- [x] All tests passing

## Blockers
None.

## Handoff Notes
P2-T06 (`abt docs validate`) can now be wired — both existence (TASK-0013)
and authority (TASK-0014) validators are complete. It will compose
load_manifest, validate_manifest_schema, build_registry,
validate_doc_existence, and validate_authority into a single CLI command.
