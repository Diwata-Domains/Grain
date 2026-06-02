# Deliverable Spec: TASK-0183

## Required Output

### New Files
- None

### Modified Files
- `README.md` — document the live Assay verification loop
- `docs/runtime/PROJECT_RULES.md` — add packet-local verification operator rules
- `src/grain/data/runtime/PROJECT_RULES.md` — keep the shipped runtime copy aligned
- `docs/canonical/cli_spec.md` — replace stale deferred Sentinel wording with the live Assay bridge contract
- `prompts/tasks.close.md` — add verification-close guidance
- `src/grain/data/prompts/tasks.close.md` — keep the shipped prompt asset aligned
- `tests/test_release_surface.py` — lock the docs guidance into release-surface coverage

## Acceptance Checklist
- [x] README documents `grain verify submit`, `status`, and `ingest`
- [x] runtime rules document the packet-local verification loop and close constraints
- [x] canonical CLI spec reflects the live Assay bridge instead of deferred Sentinel stubs
- [x] close prompt guidance mentions pending/failed verification handling
- [x] focused release-surface and verification tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Assay runtime internals
- New verification commands beyond the Phase 28 bridge
