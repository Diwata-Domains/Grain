# Plan: P2-T07-TASK-0016

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Straightforward read + lookup + display. No structural ambiguity; registry and CLI pattern are already established.

## Steps

1. Add `show_doc(root: Path, doc_id: str) -> CommandResult` to `services/docs_service.py`:
   - Load manifest (catch `AbtError`, return failed result)
   - Call `build_registry(manifest)`
   - Call `registry.by_id(doc_id)`
   - If None: return `CommandResult(ok=False, errors=[f"Doc '{doc_id}' not found in manifest"])`
   - If found: populate `warnings` with formatted key/value lines for display
     - `id: <value>`, `path: <value>`, `layer: <value>`, `authority: <value>`,
       `purpose: <value>`, `editable_by_agents: <value>`
   - Return `CommandResult(ok=True, command="docs show", ...)`

2. Wire `docs_show` in `cli/docs.py`:
   - Call `resolve_repo_root(repo)`
   - Call `docs_service.show_doc(root, doc_id)`
   - Call `print_result(result, fmt)`
   - If `not result.ok`: raise `UsageError(f"Doc '{doc_id}' not found")`

3. Write tests in `tests/test_docs_show_cmd.py`:
   - Known doc id returns exit 0 and shows metadata
   - Unknown doc id returns exit 2
   - Missing manifest returns non-zero
   - `--format json` returns valid JSON

## Patch Strategy
- Update: `src/ai_build_toolkit/services/docs_service.py`
- Update: `src/ai_build_toolkit/cli/docs.py`
- New file: `tests/test_docs_show_cmd.py`
