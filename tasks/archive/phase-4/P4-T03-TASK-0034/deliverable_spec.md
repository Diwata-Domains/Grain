# Deliverable Spec: TASK-0034

## Required Deliverables

- [x] `src/forge/domain/context.py` includes `select_working_docs`
- [x] `src/forge/services/context_service.py` includes `select_working_docs_for_packet`
- [x] `tests/test_working_doc_selection.py` covers default exclusion and opt-in inclusion
- [x] Existing canonical doc selection behavior remains unchanged
- [ ] No regressions in existing tests

## Acceptance Criteria

- [x] `select_working_docs(registry, tags)` returns `[]` when opt-in is disabled
- [x] `select_working_docs(registry, tags, include_working_docs=True)` returns only working-layer records whose `read_when` intersects `tags`
- [x] `select_working_docs_for_packet(...)` returns `(ok=False, [])` when manifest is missing or packet is absent
- [x] Working docs stay excluded by default in packet context assembly
