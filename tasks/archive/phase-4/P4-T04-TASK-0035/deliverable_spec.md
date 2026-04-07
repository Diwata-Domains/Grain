# Deliverable Spec: TASK-0035

## Required Deliverables

- [ ] `ContextBundle` exists in `src/forge/domain/context.py`
- [ ] `tests/test_context_bundle.py` covers required fields and optional metadata
- [ ] Existing context selection behavior remains unchanged
- [ ] No regressions in existing tests

## Acceptance Criteria

- `ContextBundle` stores packet files, selected canonical docs, optional working docs, and export metadata
- `selected_working_docs` defaults to an empty list
- `export_metadata` defaults to an empty dict
- Existing canonical and working doc selection tests still pass
