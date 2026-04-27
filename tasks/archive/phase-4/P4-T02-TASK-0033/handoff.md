# Handoff: P4-T02-TASK-0033

## Final State
Canonical doc selection logic is implemented, reviewed, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0033
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added pure canonical-doc selection by `read_when` tag intersection plus a manifest-aware service wrapper.

## What Was Built
- `select_canonical_docs(registry, context_tags)` in `src/forge/domain/context.py`
- `select_canonical_docs_for_packet(root, task_id, context_tags)` in `src/forge/services/context_service.py`
- canonical-selection tests in `tests/test_canonical_doc_selection.py`

## What Review Should Check
- empty tag sets return an empty selection
- only canonical-layer records are returned
- missing manifest or missing packet surfaces as `ok=False` rather than a crash

## What Was Not Done
- no working-doc inclusion
- no CLI behavior
- no implicit default-tag policy in this pure selection function

## Known Issues or Follow-ups
- None

## Files Changed
- `src/forge/domain/context.py`
- `src/forge/services/context_service.py`
- `tests/test_canonical_doc_selection.py`
- `tasks/P4-T02-TASK-0033/results.md`
- `tasks/P4-T02-TASK-0033/handoff.md`

## Reviewer Notes
This task remains correct after the later Phase 4 context decisions because the default-tag behavior is applied by callers, not by the pure selector itself.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
