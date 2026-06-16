# Deliverable Spec: TASK-0164

## Required Output

### New Files
- no new product areas required; this task should stay inside the existing docs and smoke/release test surfaces

### Modified Files
- `README.md` — clarify the desktop/MCP and Obsidian operator story
- `docs/runtime/AGENTS.md` and `docs/runtime/CLAUDE.md` — keep runtime guidance aligned with the desktop and Obsidian boundaries
- `tests/test_release_surface.py` and any focused smoke tests needed — lock the shipped guidance into regression coverage
- `tasks/P24-T05-TASK-0164/*` — complete the packet review artifacts for the Phase 24 closeout slice

## Acceptance Checklist
- [ ] operator docs clearly explain direct CLI vs local MCP wrapper usage
- [ ] operator docs clearly explain the dedicated `obsidian_adapter` path for vault work
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new MCP tools
- new Obsidian mutation behavior
- deeper vault graph semantics
