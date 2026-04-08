# Plan: TASK-0064

## Approach

1. Extend `InitResult` with `primary_adapter`, `secondary_adapters`, `adapter_warnings` fields.
2. Update `init_repo()` signature to accept `primary_adapter` and `secondary_adapters`.
3. Add `_apply_adapter_selection()` helper that loads source adapter profiles, validates IDs, records valid ones, and warns on unknown ones. Degrades safely if profile loading fails.
4. Extend `CommandResult` with `primary_adapter` and `secondary_adapters` fields; surface in text and JSON output.
5. Add `--primary-adapter` and `--secondary-adapter` options to `init_cmd`; pass through to service and result.
6. Add 7 new tests covering: no-adapter neutral, valid primary, valid secondary, unknown primary warns, unknown secondary warns, mixed valid/invalid secondaries, dry-run with adapters.

## File Changes
- `src/forge/services/init_service.py` — InitResult fields, init_repo signature, _apply_adapter_selection
- `src/forge/cli/init.py` — CLI options, pass-through to service, CommandResult fields
- `src/forge/cli/output.py` — CommandResult fields, text print for adapters
- `tests/test_init_service.py` — 7 new adapter tests

## Risks
- None. All changes are additive. Existing tests are unaffected when no adapter args are passed.
