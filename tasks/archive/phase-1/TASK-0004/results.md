# Results: TASK-0004

## Status
done

## Files Changed
- `src/ai_build_toolkit/adapters/filesystem.py` — new; `find_repo_root()` and `resolve_repo_root()`
- `src/ai_build_toolkit/cli/__init__.py` — updated; added `--repo` global option stored on Click context
- `tests/test_filesystem_adapter.py` — new; 5 tests covering auto-detection, explicit override, subdirectory traversal, and missing-marker error

## Outcome
All deliverable spec criteria met. 5/5 new tests passing, 31/31 total passing.

Repository root marker: `docs/runtime/PROJECT_RULES.md` — present in every valid ai-build-toolkit repo, lightweight, inspectable.

## Blockers
None.
