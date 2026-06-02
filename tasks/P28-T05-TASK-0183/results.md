# Results: TASK-0183

## Summary
Updated the public/operator-facing Assay verification guidance to match the live Grain bridge. The README now shows the `grain verify submit/status/ingest` loop, runtime project rules describe the packet-local verification boundary and close constraints, the canonical CLI spec no longer claims verify is a deferred Sentinel stub, and the shipped close prompt now warns against closing while verification is pending.

## Files Changed
- `README.md` — documented the live Assay verification loop
- `docs/runtime/PROJECT_RULES.md` — added packet-local verification operator rules
- `src/grain/data/runtime/PROJECT_RULES.md` — aligned the shipped runtime copy
- `docs/canonical/cli_spec.md` — replaced stale deferred Sentinel wording with the live Assay bridge description
- `prompts/tasks.close.md` — added verification-close guidance
- `src/grain/data/prompts/tasks.close.md` — aligned the shipped prompt asset
- `tests/test_release_surface.py` — added verification guidance assertions

## Verification
- `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_verify_submit_cmd.py tests/test_command_groups.py tests/test_closure_validation.py tests/test_workflow_state_service.py tests/test_task_close_cmd.py tests/test_release_surface.py`
- `102 passed in 11.96s`

## User Review
- **State:** approved
- **Summary:** The Assay verification loop is now documented in the same packet-local terms that the live CLI and workflow gates actually enforce.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Phase 28 is ready for review and close.

### Residual Risks
- The docs still describe a local payload handoff model; if Grain later adds remote Assay transport, these surfaces will need another pass.

## Verification Review
- **State:** passed
- **Summary:** Focused verification, gate, and release-surface tests passed after the docs and prompt updates landed.

### Findings
- None

## Closure Decision
- **Decision:** closed
- **Reason:** Closed after the live Assay verification bridge was documented and locked into release-surface coverage.

### Closure Blockers
- None
