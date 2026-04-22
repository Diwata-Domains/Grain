# Deliverable Spec: TASK-0132

## Required Output

### New Files
- `contrib/community_adapter_registry/README.md` — submission layout and contributor guidance
- `contrib/community_adapter_registry/templates/adapter_package.yaml` — package metadata template
- `contrib/community_adapter_registry/templates/adapter_profile.md` — adapter profile template
- `contrib/community_adapter_registry/templates/review_metadata.yaml` — review metadata template
- `contrib/community_adapter_registry/review_checklist.md` — maintainer review checklist
- `tests/test_phase19_registry_scaffold.py` — focused scaffold tests

### Modified Files
- none

## Acceptance Checklist
- [ ] community registry scaffold exists under `contrib/`
- [ ] package, profile, and review metadata templates are present
- [ ] contribution guidance explains submission layout and trust boundaries
- [ ] review checklist aligns with the explicit validation/install flow
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- CI automation
- remote install/fetch semantics
- promotion-policy enforcement
