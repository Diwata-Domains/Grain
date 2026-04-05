# Plan: TASK-0015

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Requires composing five previously separate components into a coherent service+CLI layer while respecting the thin-CLI / fat-service boundary from architecture.md.

## Steps

1. Create `src/ai_build_toolkit/services/docs_service.py`:
   - `validate_docs(root: Path) -> CommandResult`
   - Calls `load_manifest(root)` — on `MissingPathError`/`ConfigError`, return failed `CommandResult` immediately
   - Calls `validate_manifest_schema(manifest)` — collect errors
   - Calls `build_registry(manifest)`
   - Calls `validate_doc_existence(registry, root)` — collect errors
   - Calls `validate_authority(registry, manifest)` — collect errors
   - Returns `CommandResult(ok=len(errors)==0, command="docs validate", errors=all_errors)`

2. Update `src/ai_build_toolkit/cli/docs.py` — `docs_validate` command:
   - Accept `--repo` and `--format` from `ctx.obj`
   - Call `resolve_repo_root(repo_option)`
   - Call `docs_service.validate_docs(root)`
   - Call `print_result(result, fmt)`
   - If `not result.ok`: raise `ValidationError("docs validation failed")` so cli() exits with code 3

3. Write tests in `tests/test_docs_validate_cmd.py`:
   - Valid repo passes with exit 0
   - Missing manifest exits with non-zero and error message
   - Schema error reported in output
   - Missing doc file reported in output
   - `--format json` produces JSON output

## Patch Strategy
- New file: `src/ai_build_toolkit/services/docs_service.py`
- Update: `src/ai_build_toolkit/cli/docs.py`
- New file: `tests/test_docs_validate_cmd.py`
