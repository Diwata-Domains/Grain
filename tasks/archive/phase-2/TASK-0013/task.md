# Task: Implement document existence validation

## Metadata
- **ID:** TASK-0013
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0012 (document registry model)

## Objective
Implement a validator that takes a `DocumentRegistry` and a repository root path and checks that each registered document's declared path actually exists on the filesystem. Returns a list of error strings (empty = all present).

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "document existence validator" as a major deliverable. The registry knows what paths are declared; this validator checks that those paths are real. It is a required input to `abt docs validate` (P2-T06).

## Scope
- Implement `validate_doc_existence(registry: DocumentRegistry, root: Path) -> list[str]` in `src/ai_build_toolkit/validators/doc_existence_validator.py`
- Check each record's `path` relative to `root`
- Return an error string for each missing path, including the record `id` and expected path
- Records whose path points to a directory are valid if the directory exists

## Constraints
- Lives in `validators/` — not `domain/` or `adapters/`
- Accepts a `DocumentRegistry` instance — does not parse the manifest itself
- Returns error strings, does not raise
- Must not validate schema or authority — only existence

## Escalation Conditions
- A record's `path` is an empty string (treat as missing)
