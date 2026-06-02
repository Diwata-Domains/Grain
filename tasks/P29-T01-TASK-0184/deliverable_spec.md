# Deliverable Spec: TASK-0184

## Required Output

### New Files
- None

### Modified Files
- `docs/runtime/AGENTS.md` — stronger Grain/Assay loop discipline guidance
- `docs/runtime/CLAUDE.md` — stronger anti-drift startup and execution rules
- `docs/runtime/PROJECT_RULES.md` — explicit stop-and-return rules for packet and verification drift
- `src/grain/data/runtime/PROJECT_RULES.md` — shipped runtime copy aligned
- `prompts/task.execute.md` — stronger packet-first / stop-and-return wording
- `src/grain/data/prompts/task.execute.md` — shipped prompt copy aligned
- `prompts/tasks.next_and_implement.md` — stronger anti-drift execution-loop wording
- `src/grain/data/prompts/tasks.next_and_implement.md` — shipped prompt copy aligned
- `prompts/tasks.close.md` — stronger verification-loop and anti-drift wording
- `src/grain/data/prompts/tasks.close.md` — shipped prompt copy aligned
- `tests/test_release_surface.py` — release-surface assertions for the new hardening guidance

## Acceptance Checklist
- [x] runtime guidance explicitly tells agents to stop and return to Grain when packet/workflow drift is detected
- [x] execution prompts explicitly forbid continuing from chat memory or bypassing the Grain/Assay loop
- [x] close prompt explicitly reinforces the verification/closure boundary
- [x] release-surface tests cover the new hardening guidance
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New CLI commands
- New workflow-state mutation logic
- Reconcile/runner fixes
