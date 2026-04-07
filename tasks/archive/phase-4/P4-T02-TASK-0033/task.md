# Task: Implement Canonical Doc Selection Logic

## Metadata
- **ID:** TASK-0033
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T02
- **Packet Path:** tasks/P4-T02-TASK-0033/
- **Dependencies:** TASK-0032 (P4-T01, done)

## Objective
Implement a pure domain function that selects relevant canonical docs from the document registry by matching each doc's `read_when` list against a caller-supplied set of context tags. Add a service wrapper that loads the manifest, builds the registry, and returns the matching canonical `DocumentRecord`s for a given packet and tag set.

## Why This Task Exists
Phase 4 requires context assembly that includes only the relevant subset of canonical docs — not all of them. The `read_when` metadata in `docs_manifest.yaml` already encodes when each doc is relevant. This task exposes that selection as a first-class operation.

## Scope
- `select_canonical_docs(registry, context_tags) -> list[DocumentRecord]` in `domain/context.py`
- `select_canonical_docs_for_packet(root, task_id, context_tags) -> tuple[CommandResult, list[DocumentRecord]]` in `services/context_service.py`
- Tests in `tests/test_canonical_doc_selection.py`
- No CLI in this task (P4-T05/T06 handles that)
- No working-doc inclusion (P4-T03 handles that)

## Constraints
- Empty `context_tags` → empty selection (architecture: do not load all canonical docs by default)
- Only canonical-layer records are returned (not working or runtime docs)
- Manifest may not be present in all test repos — degrade gracefully with ok=False
- Selection is pure filter: `read_when` intersection with `context_tags`

## Escalation Conditions
- If `read_when` semantics need to expand beyond simple intersection — stop and record
