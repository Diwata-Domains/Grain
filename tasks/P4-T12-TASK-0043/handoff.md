# Handoff: TASK-0043

## Final State
`forge model escalate` is implemented, tested, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0043
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** `forge model escalate` is implemented and closed. Self-loop bug fixed — wildcard loop now guards `target_class != current_class`.

## What Was Built
- `get_escalation_target(config, current_class, reason)` in `routing.py` — class-specific rules first, wildcard fallback
- `escalate_model_for_class(root, current_class, reason)` in `model_service.py` — loads config and returns target or error
- `forge model escalate --from-class <class> [--reason <text>]` CLI command in `model.py`
- Text output: `model escalate: ok`, `from_class`, `target_class`, optional `reason`
- JSON output: `{ok, command, repo, from_class, target_class, reason}`
- 6 CLI tests covering class-specific path, wildcard path, reason forwarding, JSON shape, no-path error, missing profile
- Inline import of `select_model_for_stage_or_role` moved to module level

## What Review Should Check
- `get_escalation_target` walks class-specific before wildcard (order is load order from parsed rules)
- `--from-class` with no applicable rule (no wildcard) returns non-zero exit with error message
- JSON shape is stable: `from_class`, `target_class`, `reason` always present
- `model_select` no longer contains an inline import

## What Was Not Done
- `forge context` or `forge task` changes
- Changes to canonical docs

## Known Issues or Follow-ups
- Self-loop bug resolved: added `rule.target_class != current_class` guard to wildcard loop in `routing.py`; `test_model_escalate_reviewer_model_exits_nonzero` added. 339/339 passing.

## Files Changed
- `src/forge/domain/routing.py` — `get_escalation_target` function
- `src/forge/services/model_service.py` — `escalate_model_for_class` function
- `src/forge/cli/model.py` — `model_escalate` implementation; inline import fix
- `tests/test_model_escalate_cmd.py` — new CLI test file (6 tests)

## Reviewer Notes
Full suite is green at 338/338. The wildcard-catches-all behavior is by design and tests confirm it explicitly.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Consider adding error message assertions to `test_model_escalate_unknown_class_exits_nonzero` and `test_model_escalate_missing_profile_exits_nonzero`.
