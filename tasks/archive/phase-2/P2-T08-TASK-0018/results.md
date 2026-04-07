# Results: P2-T08-TASK-0018

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/docs_service.py` — added `generate_index(root, dry_run)`
- `src/ai_build_toolkit/cli/docs.py` — wired `docs_index` command with `--dry-run`
- `tests/test_docs_index_cmd.py` — new file, 7 tests
- `docs/runtime/docs_index.md` — regenerated from manifest (live repo)

## Summary
Implemented `generate_index()` service that loads the manifest, builds the
registry, and formats a structured markdown index grouped by layer with a
table per layer (id, path, authority, editable_by_agents, purpose). Authority
order pulled from `rules.authority_order`. `--dry-run` returns the line count
in warnings without writing. `abt docs index` run against the live repo
successfully refreshed `docs/runtime/docs_index.md`.

## Test Results
7/7 new tests passing. 154/154 total passing (no regressions).

## Deliverable Checklist
- [x] `generate_index(root, dry_run)` in `docs_service.py`
- [x] `abt docs index` writes `docs_index.md` and exits 0
- [x] Written file contains all doc IDs grouped by layer
- [x] `--dry-run` does not write, exits 0
- [x] Missing manifest returns non-zero
- [x] `--format json` works
- [x] CLI stays thin
- [x] All tests passing
- [x] Live repo `docs_index.md` refreshed

## Blockers
None. Phase 2 is now fully complete — all 9 tasks done.
