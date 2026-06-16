# Deliverable Spec: TASK-0121

## Required Output

### New Files
- `src/grain/services/task_advice_service.py` — proposal-only task-advice ranking helper
- `tests/test_task_advice_service.py` — focused ranked task-advice coverage

### Modified Files
- `src/grain/services/orchestration_service.py` — attach ranked task advice to scope payloads
- `tests/test_orchestration_service.py` — assert task-advice payload presence
- `docs/working/open_questions.md` — record Q17 resolution
- `docs/working/backlog.md` — re-scope P17-T04/P17-T06 after Q17 resolution
- packet files under `tasks/P17-T04-TASK-0121/` — task execution records

## Acceptance Checklist
- [ ] ranked task advice scores only the currently eligible phase task pool
- [ ] advisory task suggestions are exposed on a proposal-only surface
- [ ] `workflow next` and `task next` remain unchanged
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- changes to authoritative workflow or task-selection commands
