# Handoff: TASK-0082

## Final State
Graph-aware orchestration adapter capability wiring is implemented, reviewed, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0082
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Status:** done

### Outcome
- **Review Readiness:** accepted
- **Recommended Next Status:** done
- **Short Summary:** Added graph-backed adapter capability implementation and wired orchestration scoring/scope analysis to consume impact signals with fallback behavior.

## What Was Built
- New graph-aware capability implementation:
  - `detect_scope` and `analyze_impact` use graph outputs when available
  - static profile-signal fallback when graph paths are unavailable
- Adapter profile loader now registers graph-aware capability objects by default.
- Orchestration service now includes impact-derived tokens in ranking and exposes impact payload fields in scope analysis output.
- Tests added for capability behavior and orchestration payload integration.

## What Review Should Check
- Capability methods remain deterministic, local-only, and non-mutating.
- Orchestration behavior degrades gracefully when graph-backed signals are sparse/unavailable.
- No CLI/runtime circular import regressions were introduced.

## What Was Not Done
- Full structural intelligence end-to-end integration suite (`P10-T05`).
- Phase 10 closure tasks.

## Known Issues or Follow-ups
- Impact scoring currently uses heuristic token overlap from graph-derived file/area strings; this is deterministic but may require tuning after P10-T05 integration data.

## Files Changed
- `src/grain/adapters/capabilities.py` — graph-aware capability implementation
- `src/grain/adapters/adapter_config.py` — capability registration on profile load
- `src/grain/services/orchestration_service.py` — impact-aware scoring/payload
- `src/grain/services/graph_service.py` — import decoupling for capability integration
- `tests/test_graph_adapter_capability.py` — capability tests
- `tests/test_orchestration_service.py` — orchestration payload assertion
- `docs/working/backlog.md` — `P10-T04` review, `P10-T05` ready
- `docs/working/current_focus.md` — immediate-goal updates
- `docs/working/current_task.md` — active task pointer
- `tasks/P10-T04-TASK-0082/task.md` — packet metadata/scope
- `tasks/P10-T04-TASK-0082/context.md` — packet context
- `tasks/P10-T04-TASK-0082/plan.md` — packet plan
- `tasks/P10-T04-TASK-0082/deliverable_spec.md` — packet deliverable contract
- `tasks/P10-T04-TASK-0082/results.md` — packet results
- `tasks/P10-T04-TASK-0082/handoff.md` — handoff

## Reviewer Notes
This completes graph wiring into adapter capability surfaces and unblocks `P10-T05` integration/rebuild validation.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Execute `P10-T05` next for full extraction→graph→context→orchestration integration and rebuild validation.
