# Deliverable Spec: TASK-0173

## Required Output

### New Files
- no new product areas required; this slice should stay inside shipped docs and release-surface tests

### Modified Files
- `README.md` — explain the crawler workflow and review boundary
- `docs/runtime/AGENTS.md` and `docs/runtime/CLAUDE.md` — add crawler review and safety guidance
- `tests/test_release_surface.py` — add regression assertions for the shipped crawler guidance
- `tasks/P26-T04-TASK-0173/*` — complete the packet review artifacts for the crawler safety-guidance slice

## Acceptance Checklist
- [ ] shipped docs clearly mention `crawler_adapter` and its review/safety boundary
- [ ] robots constraints, rate-limit/retry risk, selector brittleness, and extraction drift are explicit in the runtime guidance
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new crawler execution commands
- crawler recipe work
- phase-close smoke/docs work
