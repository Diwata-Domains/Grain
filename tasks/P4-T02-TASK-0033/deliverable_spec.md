# Deliverable Spec: TASK-0033

## Required Deliverables

- [ ] `select_canonical_docs(registry, context_tags)` in `domain/context.py`
- [ ] `select_canonical_docs_for_packet(root, task_id, context_tags)` in `services/context_service.py`
- [ ] `tests/test_canonical_doc_selection.py` with ≥7 tests, all passing
- [ ] No regressions in full test suite

## Acceptance Criteria

- `select_canonical_docs(registry, {"implementing_cli"})` returns only docs with `implementing_cli` in `read_when`
- `select_canonical_docs(registry, set())` returns empty list
- `select_canonical_docs(registry, {"nonexistent_tag"})` returns empty list
- Multiple matching docs returned when multiple tags match different docs
- Only canonical-layer records returned (not working, not runtime)
- `select_canonical_docs_for_packet` returns `ok=False` when manifest is absent
- `select_canonical_docs_for_packet` returns `ok=False` when packet is not found
