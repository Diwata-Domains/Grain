# Handoff: TASK-0065

## Final State
`forge init --bootstrap` now creates a starter task packet and initializes `current_task.md` as `ready`; packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0065
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added optional --bootstrap flag to forge init that scaffolds a starter P1-T01 task packet, optionally sets its Primary Adapter, and writes current_task.md with Status: ready.

## What Was Built
- `--bootstrap` flag on `forge init`
- `_run_bootstrap()` service helper (packet creation + current_task.md write)
- `_patch_task_adapter()` helper (sets Primary Adapter in starter task.md)
- `bootstrapped_task_id` on both `InitResult` and `CommandResult`
- Text output: `bootstrap TASK-####` line when bootstrap was run
- 6 new service tests + 2 new CLI tests

## What Review Should Check
- `current_task.md` content: Task ID matches created packet, Status is `ready`
- `--dry-run --bootstrap`: no files written, bootstrapped_task_id predicted as TASK-0001
- Adapter patching: task.md has `**Primary Adapter:** code_adapter` when adapter was validated
- No-bootstrap: all 409 pre-existing tests still pass (417 total now)

## What Was Not Done
- Phase-level integration tests (`P7-T06`)
- Existing-project adoption flow (`P7-T07`)

## Known Issues or Follow-ups
- `_patch_task_adapter` relies on the exact string `**Primary Adapter:** none` from the template; if the template changes, patching silently no-ops.

## Files Changed
- `src/forge/services/init_service.py` — bootstrap param, _run_bootstrap, _patch_task_adapter, InitResult.bootstrapped_task_id
- `src/forge/cli/init.py` — --bootstrap option, pass-through, CommandResult.bootstrapped_task_id
- `src/forge/cli/output.py` — bootstrapped_task_id field, text output
- `tests/test_init_service.py` — 6 new tests
- `tests/test_task_create_cmd.py` — 2 new CLI tests
- `docs/working/current_task.md` — updated to review

## Reviewer Notes
All bootstrap-related changes are isolated to the init path. The task service (`create_packet_directory`) is reused without modification.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
