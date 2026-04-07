# Handoff: P4-T07-TASK-0038

## Final State
`forge context export` is implemented, reviewed, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0038
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Implemented markdown and JSON export for packet-scoped context bundles using the existing context assembly path.

## What Was Built
- markdown export rendering and writing via `src/forge/adapters/export.py`
- `forge context export` in `src/forge/cli/context.py`
- source metadata generation in `src/forge/services/context_service.py`
- command tests covering default export path, custom output, JSON metadata mode, working-doc inclusion, and unknown task handling

## What Review Should Check
- no-tag invocation behavior was still unresolved at close time and affected all three context commands
- JSON output shape divergence across context commands was extended by this task and had to be carried into CP-006

## What Was Not Done
- no new context-selection policy was introduced
- no canonical serialization contract was defined in this task

## Known Issues or Follow-ups
- `context export` without `--output` writes `context_export.md` into the packet directory by default
- the `"not found"` error-path string match remains duplicated in all three context commands

## Files Changed
- `src/forge/adapters/export.py` — added markdown export rendering and writing
- `src/forge/services/context_service.py` — added `build_source_metadata(...)`
- `src/forge/cli/context.py` — implemented `forge context export`
- `tests/test_context_export_cmd.py` — added command tests
- `tasks/P4-T07-TASK-0038/results.md` — persisted review intake

## Reviewer Notes
Closeout should extend CP-006 to cover `context export`. Q11 was already tracked and did not require a new open-question entry.

## Closeout Intake

### Open Questions To Log
- None new. Q11 already existed in `docs/working/open_questions.md` at close time.

### Proposal Candidates To Log
- CP-006 — Unify context command JSON doc record shapes. Update the existing proposal to cover `context build`, `context show`, and `context export`.

### Follow-Ups To Log
- Resolve Q11 before Phase 5 begins.
- Canonicalize context command JSON surfaces before Phase 5 tooling depends on them.
- Document the default export path behavior.
