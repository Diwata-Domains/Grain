# Handoff: TASK-0131

## Final State
`Implement grain adapter install` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0131
- **Phase:** Phase 19 — Community Adapter Registry
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Added the first Phase 19 install surface. `grain adapter install` now accepts either an explicit package directory or a registry handle resolved against a local reviewed-registry checkout, validates the selected package before mutation, rejects duplicate adapter IDs, and appends the installed adapter profile into `docs/runtime/adapter_profiles.md`. The command stays local-only and inspectable, with no remote fetch or hidden registry state.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm Phase 19 should keep registry-handle resolution scoped to local reviewed-registry checkouts until remote fetch semantics are designed explicitly.
- - Confirm appending installed community adapters into `docs/runtime/adapter_profiles.md` is the right local-install target for this phase.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- `pytest` could not be run from the repo-local environment until the stale `.venv` entrypoint is repaired or the test runner is installed into the active tool environment.

## Files Changed
- - `src/grain/services/adapter_install_service.py` — implemented explicit local-only install behavior for validated adapter packages and local registry handles
- - `src/grain/cli/adapter.py` — added `grain adapter install`
- - `tests/test_adapter_install_service.py` — added focused service coverage for source installs, handle installs, duplicates, and handle failures
- - `tests/test_adapter_cmd.py` — added CLI install coverage
- - `tasks/P19-T03-TASK-0131/task.md` — populated packet metadata and scope
- - `tasks/P19-T03-TASK-0131/context.md` — recorded the governing docs and excluded remote-registry scope
- - `tasks/P19-T03-TASK-0131/plan.md` — captured the install strategy
- - `tasks/P19-T03-TASK-0131/deliverable_spec.md` — defined acceptance criteria and non-goals
- 

## Reviewer Notes
- - Confirm Phase 19 should keep registry-handle resolution scoped to local reviewed-registry checkouts until remote fetch semantics are designed explicitly.
- - Confirm appending installed community adapters into `docs/runtime/adapter_profiles.md` is the right local-install target for this phase.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
