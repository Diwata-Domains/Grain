# Results: P2-T07-TASK-0016

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/docs_service.py` — added `show_doc(root, doc_id)`
- `src/ai_build_toolkit/cli/docs.py` — wired `docs_show` command
- `tests/test_docs_show_cmd.py` — new file, 5 tests

## Summary
Implemented `show_doc()` returning a `(CommandResult, DocumentRecord | None)` tuple.
The CLI formats metadata fields directly in text mode (not via `print_result`) to
avoid the "warning" prefix. JSON mode adds a `doc` key to the serialised result.
`click.UsageError` (not domain `UsageError`) is raised for not-found so exit code 2
works correctly via both `CliRunner` and the `cli()` entrypoint.

## Test Results
5/5 new tests passing. 147/147 total passing (no regressions).

## Deliverable Checklist
- [x] `show_doc(root, doc_id)` added to `docs_service.py`
- [x] `abt docs show <doc_id>` exits 0 and prints all metadata fields
- [x] `abt docs show <unknown>` exits 2 with clear error
- [x] Missing manifest returns non-zero with error
- [x] `--format json` includes `doc` object with all fields
- [x] CLI layer stays thin
- [x] All tests passing

## Blockers
None.

## Handoff Notes
P2-T08 (`abt docs index`) is blocked on Q5 resolution. P2-T09 (validator test
fixtures) is the last remaining Phase 2 task and is now unblocked. Phase 2
core deliverables are complete: manifest loading, schema validation, registry,
existence validation, authority validation, `abt docs validate`, `abt docs show`.
