# Task: Implement authority-order validation

## Metadata
- **ID:** TASK-0014
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0012 (document registry model)

## Objective
Implement a validator that checks authority-related constraints across a `DocumentRegistry` and the raw manifest. Validates that `authority` values are from the allowed set, that canonical documents are not marked `editable_by_agents: true`, and that `rules.authority_order` is a non-empty list.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "authority-order validation" as a major deliverable. `data_contracts.md` Section 6.2 defines allowed `authority` values and the `editable_by_agents` boolean contract. `PROJECT_RULES.md` Section 3 defines the authority hierarchy. This validator enforces those rules before CLI commands act on the registry.

## Scope
- Implement `validate_authority(registry: DocumentRegistry, manifest: dict) -> list[str]` in `src/ai_build_toolkit/validators/authority_validator.py`
- Check each record's `authority` value is in the allowed set from `data_contracts.md` Section 6.2
- Check that canonical layer records all have `editable_by_agents: False`
- Check that `manifest["rules"]["authority_order"]` is a non-empty list
- Return error strings for each violation; never raise

## Constraints
- Lives in `validators/` — not `domain/` or `adapters/`
- Accepts a `DocumentRegistry` and the raw manifest dict — does not load files
- Allowed `authority` values are fixed from `data_contracts.md` Section 6.2: `highest`, `high`, `highest_runtime`, `high_runtime`, `secondary`, `informational`, `advisory`
- Do not validate path existence — that is TASK-0013

## Escalation Conditions
- `data_contracts.md` allowed authority values are extended or renamed before this task completes
