# Task: Implement `abt docs validate`

## Metadata
- **ID:** TASK-0015
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0011 (schema validator), TASK-0013 (existence validator), TASK-0014 (authority validator)

## Objective
Wire all Phase 2 validators into a working `abt docs validate` CLI command backed by a `DocsService`. The command loads the manifest, runs schema, existence, and authority validation, and reports all errors to the user with a non-zero exit code when any validation fails.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "`abt docs validate` reports missing or malformed docs" as the primary CLI deliverable. All validators are now implemented; this task composes them into the command.

## Scope
- Create `src/ai_build_toolkit/services/docs_service.py` with `validate_docs(root: Path) -> CommandResult`
- Implement the `docs validate` command body in `src/ai_build_toolkit/cli/docs.py`
- Service calls: `load_manifest` → `validate_manifest_schema` → `build_registry` → `validate_doc_existence` → `validate_authority`
- All errors collected and returned in `CommandResult.errors`
- `CommandResult.ok = False` when any errors present
- Exit with code 3 (`ValidationError`) when validation fails, per `cli_spec.md` Section 5
- Support `--format text|json` via the global `--format` option

## Constraints
- CLI command stays thin — all logic in `DocsService` (`architecture.md` Section 4.1 / 4.2)
- `docs_validate` must use `resolve_repo_root()` from `adapters/filesystem.py` for path resolution
- `CommandResult` from `cli/output.py` is the return type — do not invent a new result shape
- Raise `ValidationError` (domain error) when errors are found so the `cli()` wrapper handles exit code 3
- Do not modify canonical docs or other validators

## Escalation Conditions
- `CommandResult` fields are insufficient to carry all validation output cleanly
