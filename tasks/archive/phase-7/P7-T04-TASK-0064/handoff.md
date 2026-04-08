# Handoff: TASK-0064

## Final State
`forge init` now accepts `--primary-adapter` and `--secondary-adapter` options with profile-aware validation; packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0064
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added adapter-selection CLI options to `forge init` with validation against runtime adapter profiles and safe degradation when adapters are unknown or unavailable.

## What Was Built
- `--primary-adapter` and repeatable `--secondary-adapter` options on `forge init`
- `_apply_adapter_selection` service helper that validates declared IDs against source adapter profiles
- `InitResult` extended with `primary_adapter`, `secondary_adapters`, `adapter_warnings` fields
- `CommandResult` extended with `primary_adapter` and `secondary_adapters` fields; surfaced in text and JSON output
- 7 new adapter-selection tests

## What Review Should Check
- `test_valid_primary_adapter_is_accepted` passes using the actual `code_adapter` profile — confirms adapter loading from source repo works in test context
- Unknown adapter warning messages are informative and match the warning format expected for downstream consumers
- `CommandResult` JSON with new fields doesn't break any existing downstream JSON consumers
- Existing 8 init tests still pass without any adapter args

## What Was Not Done
- Starter task-packet bootstrap (`P7-T05`)
- Existing-project adoption flow (`P7-T07`)

## Known Issues or Follow-ups
- None

## Files Changed
- `src/forge/services/init_service.py` — InitResult fields, init_repo signature, _apply_adapter_selection
- `src/forge/cli/init.py` — CLI options, pass-through, CommandResult fields
- `src/forge/cli/output.py` — CommandResult fields, text output for adapters
- `tests/test_init_service.py` — 7 new adapter tests
- `docs/working/current_task.md` — updated to review

## Reviewer Notes
Validation uses the source Forge repo's adapter_profiles.md (same source as seed files), which is consistent and available in all environments. Exception handling in `_apply_adapter_selection` is intentionally broad to prevent init failures from profile loading issues.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
