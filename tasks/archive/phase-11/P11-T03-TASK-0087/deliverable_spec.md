# Deliverable Spec: TASK-0087

## Required Output

### New Files
- `tasks/P11-T03-TASK-0087/task.md` — packet metadata/scope
- `tasks/P11-T03-TASK-0087/context.md` — packet context contract
- `tasks/P11-T03-TASK-0087/plan.md` — implementation plan
- `tasks/P11-T03-TASK-0087/deliverable_spec.md` — deliverable contract
- `tasks/P11-T03-TASK-0087/results.md` — execution results
- `tasks/P11-T03-TASK-0087/handoff.md` — review handoff

### Modified Files
- `README.md` — install method documentation and verification commands
- `docs/working/backlog.md` — move `P11-T03` to review and advance `P11-T04`
- `docs/working/current_focus.md` — update immediate goals after `P11-T03`
- `docs/working/current_task.md` — active packet pointer

## Acceptance Checklist
- [ ] `uv tool install` compatibility is validated in isolated environment
- [ ] Installed `grain` binary resolves and runs help command without project venv activation
- [ ] README install section documents recommended uv path and fallback editable install
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Homebrew install path
- full troubleshooting docs
