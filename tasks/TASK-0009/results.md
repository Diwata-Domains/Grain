# Results: TASK-0009

## Status
done

## Files Changed
- `src/ai_build_toolkit/cli/__init__.py` — updated; added `--version` / `-V` option via `importlib.metadata`; fixed `cli()` wrapper to catch `click.UsageError` and exit 2 correctly
- `tests/test_smoke.py` — new; 7 subprocess-level smoke tests covering help, version, all groups listed, unknown command exit 2, and per-group help
- `docs/working/current_task.md` — updated to TASK-0009

## Outcome
All deliverable spec criteria met. 7/7 new tests passing, 63/63 total passing.

Phase 1 is complete. All P1-T01 through P1-T09 are done.

## Fix Applied
The `cli()` wrapper was not catching `click.UsageError` (raised by Click for unknown commands in `standalone_mode=False`). Added explicit handling to map it to exit code 2, consistent with `cli_spec.md` Section 5.

## Blockers
None.
