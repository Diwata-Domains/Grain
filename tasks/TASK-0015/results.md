# Results: TASK-0015

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/docs_service.py` — new file, `validate_docs(root)`
- `src/ai_build_toolkit/cli/docs.py` — `docs_validate` command wired; `docs_show` stub updated with `doc_id` argument
- `tests/test_docs_validate_cmd.py` — new file, 6 tests

## Summary
Implemented `validate_docs()` service that sequences all five Phase 2 components:
load_manifest → validate_manifest_schema → build_registry → validate_doc_existence
→ validate_authority. Schema errors short-circuit registry/existence/authority
steps since those require a well-formed manifest. `abt docs validate` prints
results via `print_result()`, then raises `ValidationError` on failure so
`cli()` exits with code 3. Exit code 3 verified via subprocess test.

## Test Results
6/6 new tests passing. 142/142 total passing (no regressions).

## Deliverable Checklist
- [x] `services/docs_service.py` with `validate_docs(root)` exists
- [x] All five Phase 2 components called in sequence
- [x] Schema errors short-circuit downstream validation
- [x] `CommandResult.ok = False` and errors populated on failure
- [x] `abt docs validate` exits 0 on valid repo
- [x] `abt docs validate` exits 3 on validation failure
- [x] `--format json` produces valid JSON
- [x] Missing manifest reported as error, not crash
- [x] CLI layer stays thin
- [x] All tests passing

## Blockers
None.

## Handoff Notes
P2-T07 (`abt docs show`) is now unblocked — `docs_show` stub already has the
`doc_id` argument. It needs `docs_service` extended with a `show_doc()` method
that calls `load_manifest` + `build_registry` + `by_id()`.
