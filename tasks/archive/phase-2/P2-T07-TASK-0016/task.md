# Task: Implement `abt docs show`

## Metadata
- **ID:** TASK-0016
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Backlog:** P2-T07
- **Dependencies:** TASK-0012 (document registry), TASK-0015 (`abt docs validate` / docs_service exists)

## Objective
Implement the `abt docs show <doc-id>` command that looks up a single document by ID from the manifest registry and displays its metadata (id, path, layer, authority, purpose, editable_by_agents) to the user.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "`abt docs show` displays metadata for a known document" as a required CLI deliverable. The registry is built; this task exposes single-document lookup through the CLI.

## Scope
- Add `show_doc(root: Path, doc_id: str) -> CommandResult` to `services/docs_service.py`
- Implement the `docs show <doc_id>` command body in `cli/docs.py` (stub already present)
- `show_doc` loads manifest, builds registry, looks up `doc_id` via `by_id()`
- If not found: return failed `CommandResult` with a clear error, raise `UsageError`
- Text output: print each metadata field as a key/value line
- JSON output: serialise via `CommandResult` (use `warnings` field to carry metadata lines, or extend display logic)
- Write tests in `tests/test_docs_show_cmd.py`

## Constraints
- CLI stays thin — lookup logic in `docs_service`, not in `docs.py`
- Use `resolve_repo_root()` for path resolution
- `CommandResult` is the return type — do not invent a new result shape
- Raise `UsageError` (exit code 2) when doc_id is not found
- Do not re-run validation — `show_doc` is a read-only inspection command

## Escalation Conditions
- `CommandResult` cannot cleanly carry key/value metadata display without overloading `warnings`
