# Task: Harden machine-readable automation outputs and runner integration tests

## Metadata
- **ID:** TASK-0069
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T09
- **Packet Path:** tasks/P8-T09-TASK-0069/
- **Dependencies:** P8-T03 (TASK-0063), P8-T04 (TASK-0064), P8-T05 (TASK-0065), P8-T06 (TASK-0066), P8-T07 (TASK-0067), P8-T08 (TASK-0068)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Ensure the automation-relevant runner commands (`workflow next`, `task next`, `phase next`, `task prepare`, `prompt show`, `workflow run`) emit stable, predictable JSON and add integration test coverage that proves the commands work correctly in combination across realistic workflow scenarios.

## Why This Task Exists

Individual unit tests exist for each runner command. This task adds cross-command integration coverage proving the runner chain works as a whole: state changes from `workflow run` are immediately reflected in `workflow next`; commands agree on the same state; stop conditions surface consistently across all commands.

## Scope
- New integration test file `tests/test_runner_integration.py`
- Update `docs/working/current_focus.md` to reflect P8-T08 done and P8-T09 active
- Update `docs/working/backlog.md` P8-T09 status to `review`
- No source code changes (JSON shapes are already stable and consistent)

## Constraints
- Do not change existing JSON output shapes — breaking change risk
- Follow existing test helper patterns from `test_workflow_next_cmd.py` and `test_workflow_run_cmd.py`
- Patch-over-rewrite: only add tests and update working docs

## Escalation Conditions
- If a genuine JSON instability is discovered that requires a breaking fix, stop and propose it as a change proposal

## Closure Requirements

Before the packet can move to review:
- `results.md` with status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, blockers
- `handoff.md` with packet identity, status, review readiness, summary, what to check, known issues, files changed

## Reviewer Focus
- Verify integration tests cover state transitions, cross-command agreement, and JSON invariants
- Confirm no source code changes beyond working docs and tests
- Check that all new tests pass with no regressions
