# Task: Implement forge model select

## Metadata
- **ID:** TASK-0042
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T11
- **Packet Path:** tasks/P4-T11-TASK-0042/
- **Dependencies:** TASK-0040 (P4-T09, done)

## Objective
Implement `forge model select` so the CLI resolves and displays the model class for a given workflow stage or task role, using the routing domain and service layer from P4-T09.

## Why This Task Exists
Phase 4 requires user-facing model routing resolution. `forge model select` is the CLI surface over `select_model_for_stage_or_role` from `model_service.py` and `select_model_class` from `routing.py`.

## Scope
- Implement `model select` command body in `src/forge/cli/model.py`.
- Support `--stage TEXT` and `--role TEXT` options (at least one required).
- Support `--format text|json` via global flag.
- Add CLI tests in `tests/test_model_select_cmd.py`.

## Constraints
- Use `select_model_for_stage_or_role` from `src/forge/services/model_service.py` — do not inline routing logic in the CLI.
- Follow existing CLI output patterns from `model show`.
- Do not implement `forge model escalate` in this task.

## Escalation Conditions
- If routing behavior requires contract changes, stop and propose.
- If neither `--stage` nor `--role` is provided, emit a UsageError.

## Closure Requirements

Before the packet can move to review, the task artifacts must include:

- `results.md` with current task status, review readiness, recommended next status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, and blockers
- `handoff.md` with packet identity, phase, status, review readiness, recommended next status, summary, what was built, what review should check, known issues or follow-ups, files changed, reviewer notes, and closeout intake

Before the packet can move from review to done, the review artifacts must include:

- explicit `open_questions_to_log`
- explicit `proposal_candidates_to_log`
- explicit `followups_to_log`

Use `None` when a category has no items. Do not rely on unlabeled narrative prose for closeout automation.

## Reviewer Focus
- Verify `--stage` and `--role` are passed through to `select_model_for_stage_or_role` correctly.
- Verify JSON shape matches documented CLI contract.
- Verify UsageError when neither option provided.
