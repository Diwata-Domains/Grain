# Results: TASK-0064

## Packet State
- **Current Task Status:** done
- **Review Readiness:** [reviewer fills]
- **Recommended Next Status:** [reviewer fills]

## Files Changed
- `src/forge/services/init_service.py` — Added `primary_adapter`, `secondary_adapters`, `adapter_warnings` to InitResult; updated `init_repo` signature; added `_apply_adapter_selection` helper with profile-aware validation
- `src/forge/cli/init.py` — Added `--primary-adapter` and `--secondary-adapter` options; pass-through to service; surface in CommandResult
- `src/forge/cli/output.py` — Added `primary_adapter` and `secondary_adapters` fields to CommandResult; print adapter lines in text output
- `tests/test_init_service.py` — 7 new adapter-selection tests added

## Summary
Added `--primary-adapter` and repeatable `--secondary-adapter` options to `forge init`. The service validates declared adapter IDs against the source Forge repo's `adapter_profiles.md` using the existing `load_adapter_profiles` loader. Valid adapters are recorded in `InitResult` and surfaced in `CommandResult` output (text and JSON). Unknown adapters produce warnings without failing. No adapter declared = adapter-neutral, all existing behavior unchanged. Dry-run respects adapter validation without writing.

## Test Results
7/7 new tests passing. 409/409 total passing.

## Efficiency

### Execute
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Files Read (estimated):** 18
- **Notes:** Single pass. All changes were additive; no rework required.

### Review
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Notes:** No issues found. All acceptance criteria confirmed. Broad exception catch is intentional per spec.

### Close
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Notes:** Clean closure — no working-doc updates required; all OQ/proposal/follow-up fields None.

## Review Notes
- Validation uses `_SOURCE_REPO_ROOT` (the installed Forge repo), not the target init directory. This is intentional and consistent with seed file sourcing.
- `_apply_adapter_selection` catches all exceptions from profile loading and degrades to a warning. Reviewer should confirm this is the right behavior for edge cases (e.g. corrupt profiles.md).
- `CommandResult` now has `primary_adapter` and `secondary_adapters` — these appear in all command JSON output even when empty strings/empty lists; this is harmless but reviewer should confirm no downstream JSON consumers are affected.

## Review Intake
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **Review Decision:** ready
- **Definition of Done Met:** yes
- **Recommended Next Status:** done

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Deliverable Checklist
- [x] `--primary-adapter` option added and functional
- [x] `--secondary-adapter` repeatable option added and functional
- [x] Unknown adapters warn without failing
- [x] No adapter = adapter-neutral (no behavior change)
- [x] Dry-run with adapters works correctly
- [x] JSON output includes adapter fields
- [x] All tests passing (409/409)

## Blockers
None.
