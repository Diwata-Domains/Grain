# Deliverable Spec: TASK-0062

## Required Output

### New Files
- `prompts/workflow.onboard.new.md` — stable new-project onboarding prompt with question-first intake and explicit adapter-selection inputs

### Modified Files
- `prompts/workflow.init.md` — compatibility alias guidance to the new onboarding entrypoint
- `README.md` — onboarding instructions updated to reference the new prompt
- `prompts/README.md` — prompt index updated to include the new onboarding prompt and compatibility alias

## Acceptance Checklist
- [ ] New onboarding prompt exists and clearly enforces question-first, new-project-only flow
- [ ] Adapter selection inputs are explicit (primary required, secondary optional)
- [ ] Legacy `workflow.init` path preserved as compatibility guidance
- [ ] README onboarding instructions point to the new stable prompt entrypoint
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Existing-project onboarding implementation
- `forge init` scaffolding/CLI behavior changes (`P7-T03` onward)
- Provider-specific onboarding capture
