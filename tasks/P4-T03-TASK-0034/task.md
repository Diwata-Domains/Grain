# Task: Implement Optional Working-Doc Inclusion Logic

## Metadata
- **ID:** TASK-0034
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T03
- **Dependencies:** TASK-0033 (P4-T02, done)

## Objective
Add opt-in working-document selection to the context layer so packet context can include working docs only when explicitly requested for sequencing or blocker resolution. Default behavior must continue to exclude working docs.

## Why This Task Exists
Phase 4 context assembly must stay minimal by default, but some execution and review paths need working docs such as the backlog or current focus notes. This task adds the selection hook without loading the full working-doc set automatically.

## Scope
- `select_working_docs(registry, context_tags, include_working_docs=False) -> list[DocumentRecord]` in `domain/context.py`
- `select_working_docs_for_packet(root, task_id, context_tags, include_working_docs=False) -> tuple[CommandResult, list[DocumentRecord]]` in `services/context_service.py`
- Tests in `tests/test_working_doc_selection.py`
- Default behavior: no working docs returned unless explicitly opted in
- Selection remains tag-based using `read_when` metadata

## Constraints
- Use the existing manifest registry and `DocumentRecord` model
- Do not change canonical doc selection behavior
- Do not introduce bundle/export logic yet
- Keep working docs excluded unless the caller explicitly opts in

## Escalation Conditions
- If working-doc inclusion needs additional heuristics beyond explicit opt-in plus tag intersection, stop and record the ambiguity
