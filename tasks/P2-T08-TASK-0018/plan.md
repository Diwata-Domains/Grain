# Plan: P2-T08-TASK-0018

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Requires deciding what to preserve vs. replace in `docs_index.md`, formatting structured markdown output, and wiring dry-run correctly.

## Steps

1. Add `generate_index(root: Path, dry_run: bool = False) -> CommandResult` to `services/docs_service.py`:
   - Load manifest (catch `AbtError`, return failed result)
   - Build registry
   - Format markdown output:
     - Header with generation notice and source path
     - Authority hierarchy from `manifest["rules"]["authority_order"]`
     - Three sections (Canonical, Working, Runtime), each with a table: id | path | authority | editable_by_agents | purpose
   - If `dry_run`: return result with output in `warnings`, do not write
   - If not `dry_run`: write to `root / "docs/runtime/docs_index.md"`
   - Return `CommandResult(ok=True, command="docs index", files_updated=[...] or files_skipped=[...])`

2. Wire `docs_index` in `cli/docs.py`:
   - Add `@click.option("--dry-run", is_flag=True)`
   - Call `resolve_repo_root(repo)`
   - Call `docs_service.generate_index(root, dry_run=dry_run)`
   - Call `print_result(result, fmt)`

3. Write tests in `tests/test_docs_index_cmd.py`:
   - Normal run writes `docs_index.md` and exits 0
   - `--dry-run` does not write file, exits 0
   - Missing manifest exits non-zero
   - Written file contains all registered doc ids
   - `--format json` produces valid JSON

## Patch Strategy
- Update: `src/ai_build_toolkit/services/docs_service.py`
- Update: `src/ai_build_toolkit/cli/docs.py`
- New file: `tests/test_docs_index_cmd.py`
- `docs/runtime/docs_index.md` will be overwritten on first real run
