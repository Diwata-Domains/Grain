# Deliverable Spec: P2-T07-TASK-0016

## Definition of Done

1. `show_doc(root, doc_id)` added to `services/docs_service.py`
2. `abt docs show <doc_id>` exits 0 and prints metadata for a known doc
3. `abt docs show <unknown>` exits 2 with a clear error message
4. Missing manifest returns non-zero with error
5. `--format json` produces valid JSON output
6. CLI layer stays thin — no lookup logic in `docs.py`
7. All tests passing, no regressions

## Out of Scope
- `abt docs index` (P2-T08, blocked on Q5)
- Validator test fixtures (P2-T09)
