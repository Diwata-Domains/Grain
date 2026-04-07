# Plan: TASK-0004

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Requires a design decision about what constitutes the repository root marker and where resolution logic lives relative to module boundaries. Affects all downstream commands. `reviewer_model` should verify the resolver placement matches `architecture.md` Section 6.4 and the marker choice is inspectable and filesystem-friendly.

## Steps

1. Define the v1 repository root marker — a lightweight, inspectable indicator (e.g. presence of `docs/runtime/PROJECT_RULES.md` or a `pyproject.toml` at root). Document the choice in the implementation.
2. Create `src/ai_build_toolkit/adapters/filesystem.py`
3. Implement `find_repo_root(start: Path) -> Path` — walks upward from `start` until the marker is found; raises a clear error if not found
4. Implement `resolve_repo_root(repo_option: str | None) -> Path` — uses `--repo` if provided, otherwise calls `find_repo_root(Path.cwd())`
5. Wire `--repo` as a global option on the `main` Click group in `src/ai_build_toolkit/cli/__init__.py` (store on Click context, do not call resolver yet — commands will invoke it when needed)
6. Write unit tests covering:
   - auto-detection finds the correct root
   - explicit `--repo` path is used as-is
   - missing marker raises a clear error

## Patch Strategy
- New file: `src/ai_build_toolkit/adapters/filesystem.py`
- Update: `src/ai_build_toolkit/cli/__init__.py` — add `--repo` option to `main`
- New file: `tests/test_filesystem_adapter.py`
- No changes to `services/`, `domain/`, or `validators/`
