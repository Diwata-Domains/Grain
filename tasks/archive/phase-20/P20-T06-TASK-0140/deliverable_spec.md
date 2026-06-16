# Deliverable Spec: TASK-0140

## Required Output

### New Files
- `tests/test_release_surface.py` additions — guardrail coverage for shipped prompt and runtime assets

### Modified Files
- `prompts/task.execute.md` and `src/grain/data/prompts/task.execute.md` — packet-first execution guardrails
- `prompts/tasks.next_and_implement.md` and `src/grain/data/prompts/tasks.next_and_implement.md` — explicit packet-on-disk requirements before implementation
- `src/grain/services/agents_md_service.py` — generated AGENTS block now warns against coding without an active packet
- `src/grain/data/runtime/context_loading.md` and `docs/runtime/context_loading.md` — implementation guidance now stops when no packet exists
- `docs/runtime/CLAUDE.md` — local agent instructions reinforce active-packet-first behavior
- `tests/test_agents_md_cmd.py` — AGENTS generation coverage for the new guardrail wording

## Acceptance Checklist
- [x] Stable execution prompts explicitly require packet creation or activation before code changes
- [x] Generated agent instructions warn against implementing from chat context without a packet on disk
- [x] Bundled runtime guidance tells agents to stop if no active packet exists yet
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changing workflow command behavior or state-machine semantics
- Introducing new prompt entrypoints or hidden workflow steps
