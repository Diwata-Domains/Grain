# Handoff: P4-T08-TASK-0039

## Final State
Model profile configuration loading is implemented, reviewed, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0039
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added runtime loading and parsing of `docs/runtime/agent_profiles.md` into structured routing configuration objects.

## What Was Built
- routing domain dataclasses in `src/forge/domain/routing.py`
- markdown loader/parser in `src/forge/adapters/model_config.py`
- parser and loader tests in `tests/test_model_config_loader.py`

## What Review Should Check
- parsed config includes `open_model`, `frontier_model`, and `reviewer_model`
- escalation rules capture `open_model -> frontier_model` and `* -> reviewer_model`
- loader and parser raise typed errors for missing file and incomplete profile content
- full test suite remains green

## What Was Not Done
- no CLI behavior for `forge model show`, `forge model select`, or `forge model escalate`
- no new runtime config format beyond `docs/runtime/agent_profiles.md`

## Known Issues or Follow-ups
- no blocking issues in this packet
- P4-T09+ should consume the routing domain objects directly in model services and CLI code

## Files Changed
- `src/forge/domain/routing.py`
- `src/forge/adapters/model_config.py`
- `tests/test_model_config_loader.py`
- `tasks/P4-T08-TASK-0039/task.md`
- `tasks/P4-T08-TASK-0039/context.md`
- `tasks/P4-T08-TASK-0039/plan.md`
- `tasks/P4-T08-TASK-0039/deliverable_spec.md`
- `tasks/P4-T08-TASK-0039/results.md`
- `tasks/P4-T08-TASK-0039/handoff.md`
- `docs/working/change_proposals.md`
- `docs/working/current_task.md`

## Reviewer Notes
Implementation is correct for v1. The only significant drift found was an architecture-doc mismatch around `ModelProfile` minimum fields, now logged as CP-008.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- CP-008 — Align `architecture.md §7.4` ModelProfile fields with the v1 implementation and runtime profile source.

### Follow-Ups To Log
- P4-T09+ should use `ModelRoutingConfig.by_class()` and `model_classes()` directly.
- Consider scoping `_ESCALATE_TO` parsing to known model classes if the escalation section grows.
