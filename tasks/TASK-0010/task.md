# Task: Implement manifest file loader

## Metadata
- **ID:** TASK-0010
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0001 (adapters/ module exists), TASK-0004 (filesystem adapter pattern established)

## Objective
Implement a loader that reads `docs/runtime/docs_manifest.yaml` from a repository-relative path and returns its parsed contents as a Python data structure. This is the foundation all Phase 2 validation and registry tasks depend on.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "docs manifest loader" as the first deliverable. Every downstream Phase 2 task — schema validation, document registry, existence checks — requires a way to read the manifest into memory. Without this, nothing in Phase 2 can proceed.

## Scope
- Implement a manifest loader in `src/ai_build_toolkit/adapters/`
- Read `docs/runtime/docs_manifest.yaml` using the resolved repository root
- Parse YAML and return raw parsed content
- Raise a typed error if the file is missing or unparseable

## Constraints
- Must use `resolve_repo_root()` from `adapters/filesystem.py` for path resolution or accept a `root: Path` argument
- Manifest path must match `data_contracts.md` Section 5: `docs/runtime/docs_manifest.yaml`
- Loader must live in `adapters/` — it is a filesystem read concern (`architecture.md` Section 6.4)
- Must raise `MissingPathError` if manifest is absent and `ConfigError` if YAML is malformed — both from `domain/errors.py`
- Must not perform schema validation — that is TASK-0011

## Escalation Conditions
- `PyYAML` or `ruamel.yaml` dependency introduces a conflict with existing dependencies
