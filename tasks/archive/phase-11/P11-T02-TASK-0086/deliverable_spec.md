# Deliverable Spec: TASK-0086

## Required Output

### New Files
- `.github/workflows/publish-pypi.yml` — CI-compatible build and publish workflow for TestPyPI/PyPI
- `scripts/bump_version.py` — semver bump utility for `pyproject.toml`
- `tests/test_bump_version_script.py` — bump utility tests
- `tasks/P11-T02-TASK-0086/task.md` — packet metadata/scope
- `tasks/P11-T02-TASK-0086/context.md` — packet context contract
- `tasks/P11-T02-TASK-0086/plan.md` — implementation plan
- `tasks/P11-T02-TASK-0086/deliverable_spec.md` — deliverable contract
- `tasks/P11-T02-TASK-0086/results.md` — execution results
- `tasks/P11-T02-TASK-0086/handoff.md` — review handoff

### Modified Files
- `pyproject.toml` — release optional dependencies and packaging alignment
- `docs/working/backlog.md` — set `P11-T02` to review and advance next task state
- `docs/working/current_focus.md` — immediate-goal update after P11-T02
- `docs/working/current_task.md` — active packet pointer

## Acceptance Checklist
- [ ] CI workflow supports build + twine check + publish path for TestPyPI and PyPI
- [ ] Version bump process is explicitly defined and automated via script
- [ ] Build/publish tooling dependencies declared for release use
- [ ] Workflow file parses successfully
- [ ] Wheel build validation passes locally
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Live publish execution
- Post-publish install validation from PyPI (handled in later tasks)
