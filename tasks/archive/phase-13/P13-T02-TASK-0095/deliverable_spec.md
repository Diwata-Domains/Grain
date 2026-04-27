# Deliverable Spec: TASK-0095

## Required Output

### New Files
- `tasks/P13-T02-TASK-0095/task.md` — packet metadata and execution scope
- `tasks/P13-T02-TASK-0095/context.md` — packet context contract
- `tasks/P13-T02-TASK-0095/plan.md` — execute-stage implementation plan
- `tasks/P13-T02-TASK-0095/deliverable_spec.md` — deliverable contract
- `tasks/P13-T02-TASK-0095/results.md` — execution results and checklist
- `tasks/P13-T02-TASK-0095/handoff.md` — review handoff bundle
- `src/grain/domain/scan_result.py` — scanner output domain model
- `src/grain/services/codebase_scanner.py` — codebase scanner service
- `tests/test_codebase_scanner.py` — scanner service test coverage

### Modified Files
- `src/grain/domain/__init__.py` — export `ScanResult`
- `docs/working/backlog.md` — update P13-T02 task status sequencing
- `docs/working/current_focus.md` — update immediate goals after execute
- `docs/working/current_task.md` — active task pointer/status

## Acceptance Checklist
- [ ] `CodebaseScanner.scan()` returns `ScanResult`
- [ ] primary languages are detected from file extensions with deterministic ordering
- [ ] applicable adapters are detected (`code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`)
- [ ] key files are detected (`README*`, `package.json`, `pyproject.toml`, `Makefile`)
- [ ] CI config files are detected (`.github/workflows`, GitLab, CircleCI, Azure pipelines)
- [ ] documentation files are detected and returned as sorted relative paths
- [ ] scanner ignores common generated/dependency directories
- [ ] new scanner tests pass
- [ ] full test suite passes with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `OnboardDocGenerator` implementation (P13-T03)
- `workflow.onboard.existing.md` prompt work (P13-T04)
- Phase 13 integration suite (P13-T05)
