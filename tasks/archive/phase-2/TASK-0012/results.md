# Results: TASK-0012

## Status
done

## Files Changed
- `src/ai_build_toolkit/domain/documents.py` — new file, `DocumentRecord`, `DocumentRegistry`, `build_registry()`
- `tests/test_document_registry.py` — new file, 13 tests

## Summary
Implemented the document registry domain model. `DocumentRecord` is a dataclass
with all seven fields from `architecture.md` Section 7.1. `DocumentRegistry`
wraps a list of records and exposes `all()`, `by_id()`, and `by_layer()`.
`build_registry()` parses the three manifest layers into records, setting the
`layer` field from the section name. Gracefully handles absent/non-list
sections and empty manifests without raising.

## Test Results
13/13 new tests passing. 111/111 total tests passing (no regressions).

## Deliverable Checklist
- [x] `domain/documents.py` exists with no filesystem access
- [x] `DocumentRecord` has all 7 required fields
- [x] `DocumentRegistry.all()`, `by_id()`, `by_layer()` implemented
- [x] `build_registry()` populates from canonical, working, runtime sections
- [x] `layer` field reflects source section on every record
- [x] `by_id` returns None for unknown IDs
- [x] Empty/missing sections handled without raising
- [x] All tests passing

## Blockers
None.

## Handoff Notes
P2-T04 (document existence validation) and P2-T07 (`abt docs show`) can both
proceed now — they depend on `DocumentRegistry`. P2-T04 needs `by_layer()` or
`all()` to iterate records and check paths. P2-T07 needs `by_id()` to look up
a single document for display.
