# Task: Implement Context Bundle Model

## Metadata
- **ID:** TASK-0035
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T04
- **Dependencies:** TASK-0034 (P4-T03, done)

## Objective
Create the `ContextBundle` domain model that packages packet-local files, selected canonical docs, optional working docs, and export metadata into one structured object for later context build/export commands.

## Why This Task Exists
Phase 4 needs a stable context output object before CLI build/export commands can be implemented. The bundle model is the structured handoff between context selection and serialization.

## Scope
- `ContextBundle` dataclass in `domain/context.py`
- fields for packet files, selected canonical docs, optional working docs, and export metadata
- tests in `tests/test_context_bundle.py`
- no CLI behavior yet
- no export serializer yet

## Constraints
- Keep the model in the context domain module
- Preserve the minimal context-selection design from P4-T01 through P4-T03
- Do not introduce build/export logic in this task

## Escalation Conditions
- If the bundle shape requires additional required fields beyond packet files, canonical docs, optional working docs, and export metadata, stop and record the ambiguity
