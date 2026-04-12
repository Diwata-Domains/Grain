# Deliverable Spec: TASK-0094

## Required Output

### New Files
- `tasks/P13-T01-TASK-0094/task.md` — packet metadata/scope ✓
- `tasks/P13-T01-TASK-0094/context.md` — packet context contract ✓
- `tasks/P13-T01-TASK-0094/plan.md` — implementation plan ✓
- `tasks/P13-T01-TASK-0094/deliverable_spec.md` — this file ✓
- `tasks/P13-T01-TASK-0094/results.md` — execution results (filled during execute)
- `tasks/P13-T01-TASK-0094/handoff.md` — review handoff (filled during execute)
- `src/grain/domain/onboard.py` — `ScaffoldManifest` dataclass
- `src/grain/services/onboard_service.py` — `OnboardService` with scaffold logic
- `src/grain/cli/onboard.py` — `grain onboard` CLI command
- `tests/test_onboard_cmd.py` — tests (≥ 8)

### Modified Files
- `src/grain/cli/__init__.py` — register onboard command
- `docs/working/backlog.md` — mark P13-T01 in_progress → done, sequence P13-T02
- `docs/working/current_task.md` — update active task pointer

## Acceptance Checklist
- [ ] `grain onboard --help` works
- [ ] `grain onboard [path]` creates canonical dirs and stubs additively
- [ ] Existing files are never overwritten — they appear in `skipped` list
- [ ] `--dry-run` produces correct manifest without touching filesystem
- [ ] `--format json` output matches `{"created": [...], "skipped": [...], "root": "..."}`
- [ ] All stub files include `# DRAFT` marker
- [ ] ≥ 8 new tests passing
- [ ] Full test suite passing with no regressions
- [ ] `results.md` and `handoff.md` filled

## Not Required
- Codebase scanning (P13-T02)
- Draft doc generation from scan (P13-T03)
- `workflow.onboard.existing.md` prompt (P13-T04)
- Phase 13 integration test suite (P13-T05)
