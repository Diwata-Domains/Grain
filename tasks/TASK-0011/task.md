# Task: Implement manifest schema validation

## Metadata
- **ID:** TASK-0011
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0010 (manifest loader must exist)

## Objective
Implement a validator that takes a parsed manifest dict and checks that all required top-level sections and required fields are present and correctly typed. This is the schema gate that all downstream Phase 2 work depends on.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "manifest schema validator" as a major deliverable. The loader (TASK-0010) returns raw parsed content. This task adds the first validation layer: structural conformance against the schema defined in `data_contracts.md` Sections 5 and 6.

## Scope
- Implement `validate_manifest_schema(manifest: dict) -> list[str]` in `src/ai_build_toolkit/validators/manifest_validator.py`
- Validate required top-level sections: `version`, `project`, `canonical`, `working`, `runtime`, `tasks`, `rules`
- Validate required fields on each doc entry in `canonical`, `working`, `runtime`
- Validate required sub-keys in `tasks` and `rules` sections
- Return a list of error strings (empty = valid); do not raise exceptions
- Write tests in `tests/test_manifest_validator.py`

## Constraints
- Validator lives in `validators/`, not `adapters/` or `services/`
- Must not load files — accepts an already-parsed dict
- Must not raise exceptions — return error strings
- Schema rules must derive strictly from `data_contracts.md` Sections 5 and 6
- Do not validate file existence (that is TASK-0012 / P2-T04)
