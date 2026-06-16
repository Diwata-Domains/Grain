# Deliverable Spec: TASK-0174

## Required Output

### New Files
- no new product areas required; this slice should stay inside integration tests and packet/phase closeout artifacts

### Modified Files
- `tests/test_document_adapters_integration.py` — add one integrated crawler adapter smoke flow
- `tasks/P26-T05-TASK-0174/*` — complete the packet review artifacts for the phase closeout slice
- `docs/working/workflow_metrics.md` and `docs/working/current_focus.md` — phase closeout bookkeeping
- `docs/working/backlog.md` if needed — final task state normalization before phase close

## Acceptance Checklist
- [ ] one integrated smoke path covers the current crawler adapter slice end-to-end
- [ ] Phase 26 closeout docs are ready for `grain phase close`
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new crawler features
- recipe-layer work
