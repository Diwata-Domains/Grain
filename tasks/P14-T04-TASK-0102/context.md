# Context: TASK-0102

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — context assembly pipeline shape

### Runtime Config (load for this task)
- `docs/runtime/adapter_profiles.md` — all three adapter profiles (spreadsheet, docs, pdf) as defined by T01–T03

### Working (load if needed)
- `docs/working/backlog.md` — Phase 14 close sequencing

### Packet Files
- `tasks/P14-T04-TASK-0102/task.md`
- `tasks/P14-T04-TASK-0102/plan.md`
- `tasks/P14-T04-TASK-0102/deliverable_spec.md`

### Reference (scan for patterns, do not load fully)
- `src/grain/services/spreadsheet_extractor.py` — T01 result
- `src/grain/services/docs_extractor.py` — T02 result
- `src/grain/services/pdf_extractor.py` — T03 result
- `src/grain/services/context_service.py` — context assembly entry point
- `tests/test_context_build_cmd.py` — existing integration test patterns to follow

## Excluded Context
- Phase 13 onboard tests — not relevant
- Tree-sitter / graph internals — not relevant for document adapter integration

## Context Sufficiency Note
Read `test_context_build_cmd.py` for the exact test pattern (how to set up a task packet, call context build, and assert on output). Then write parallel tests for document file types.
