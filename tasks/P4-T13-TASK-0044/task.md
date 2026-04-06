# Task: Add context and routing tests

## Metadata
- **ID:** TASK-0044
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T13
- **Packet Path:** tasks/P4-T13-TASK-0044/
- **Dependencies:** TASK-0038, TASK-0043

## Objective
Add focused tests that cover context bundle assembly boundaries, export metadata/output shape, and model routing selection/escalation behavior for the Phase 4 context and routing subsystem.

## Why This Task Exists
Phase 4 is complete only when context assembly and routing behavior are covered by tests. This task provides the final verification surface for `forge context build`/`forge context export` support and model-class resolution boundaries.

## Scope
- Add `tests/test_context_build.py` for bundle assembly and source selection coverage.
- Add `tests/test_context_export.py` for markdown export output coverage.
- Add `tests/test_model_routing.py` for model selection and escalation coverage.
- Keep coverage aligned with the existing domain/service implementation without changing CLI behavior.

## Constraints
- Preserve provider-agnostic model-class routing.
- Keep context selection local-file based and aligned with existing packet/document contracts.
- Do not expand into Phase 5 review or handoff features.

## Escalation Conditions
- If the existing routing or context contracts are inconsistent with the testable behavior, stop and record the conflict instead of inventing new rules.
- If a test requirement would force a canonical or workflow change, escalate through the proposal flow rather than editing canonical docs directly.
