# Task: Implement forge model escalate

## Metadata
- **ID:** TASK-0043
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T12
- **Packet Path:** tasks/P4-T12-TASK-0043/
- **Dependencies:** TASK-0040 (P4-T09, done)

## Objective
Implement `forge model escalate` so the CLI returns the escalation target model class for a given current class, following the escalation rules defined in `docs/runtime/agent_profiles.md`. Cover `open_model → frontier_model` and `* → reviewer_model` paths.

## Why This Task Exists
Phase 4 requires explicit model escalation support. `forge model escalate` is the CLI surface for surfacing escalation decisions, making the routing contract visible rather than implicit.

## Scope
- Add `get_escalation_target` to `src/forge/domain/routing.py`.
- Add `escalate_model_for_class` service function to `src/forge/services/model_service.py`.
- Implement `model escalate` command body in `src/forge/cli/model.py` with `--from-class` (required) and `--reason` (optional) options.
- Fix inline import of `select_model_for_stage_or_role` in `model_select` (move to module level).
- Add CLI tests in `tests/test_model_escalate_cmd.py`.

## Constraints
- Use parsed escalation rules from `ModelRoutingConfig` — do not hardcode class names in service or CLI.
- Return a non-zero exit with a clear error when no escalation path is defined for the given class.
- Do not alter canonical docs.

## Escalation Conditions
- If the escalation path contract in `agent_profiles.md` is ambiguous, stop and record rather than inventing hidden rules.

## Closure Requirements

Before the packet can move to review, the task artifacts must include:

- `results.md` with current task status, review readiness, recommended next status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, and blockers
- `handoff.md` with packet identity, phase, status, review readiness, recommended next status, summary, what was built, what review should check, known issues or follow-ups, files changed, reviewer notes, and closeout intake

Before the packet can move from review to done, the review artifacts must include:

- explicit `open_questions_to_log`
- explicit `proposal_candidates_to_log`
- explicit `followups_to_log`

Use `None` when a category has no items.

## Reviewer Focus
- Verify `get_escalation_target` walks class-specific rules before wildcard rules.
- Verify `--from-class` with an unknown class returns a clear non-zero error.
- Verify JSON shape includes `from_class`, `target_class`, `reason`.
