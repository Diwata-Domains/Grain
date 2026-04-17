# Task: Add `forge workflow run`

## Metadata
- **ID:** TASK-0068
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T08
- **Packet Path:** tasks/P8-T08-TASK-0068/
- **Dependencies:** P8-T03 (TASK-0063), P8-T04 (TASK-0064), P8-T05 (TASK-0065), P8-T06 (TASK-0066), P8-T07 (TASK-0067)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Add a guarded one-step runner CLI command `forge workflow run` that evaluates the current workflow state, executes one mechanical step if the state allows it (activating a ready task into `current_task.md`), or stops with an explicit gate reason when human review, planning, execution by an agent, or verification is required. The command must return machine-readable JSON output and be usable in automation scripts.

## Why This Task Exists

Phase 8 establishes a workflow automation runner foundation. After `workflow next`, `task next`, `phase next`, `task prepare`, and `prompt show` provide read-only state inspection, `workflow run` is the one-step state-advancing command that closes the loop. It operationalizes the stop-condition contract defined in Q16.

## Scope
- New `workflow_run_service.py` with runner logic
- `workflow run` command added to `src/forge/cli/workflow.py`
- Gate conditions: task_in_progress (execution in flight), task_close (human review required), task_planning (planning required), blocked, phase_boundary, conflicting, eval failure
- Mechanical action: activate ready task → write `current_task.md` to `in_progress`
- Text and JSON output formats
- Tests covering: action taken, all gate conditions, JSON output

## Constraints
- Read-only service pattern must be preserved in `workflow_service.py`
- State mutation is limited to writing `docs/working/current_task.md`
- Follow existing command output style: `forge.cli.output.CommandResult`, `print_result`
- Do not modify canonical docs directly
- One step per invocation — must stop after taking one action or reaching one gate

## Escalation Conditions
- If activation logic requires touching task packet files beyond `current_task.md`, stop and escalate
- If the runner discovers a canonical contract gap around `task_execute` vs in-flight detection, stop and log as open question

## Closure Requirements

Before moving to review:
- `results.md` with status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, blockers
- `handoff.md` with packet identity, status, review readiness, summary, what to check, known issues, files changed

## Reviewer Focus
- Verify that gate conditions match Q16 stop-condition contract
- Verify that `current_task.md` is written correctly when a task is activated
- Verify JSON output shape is stable and machine-readable
- Confirm no state mutation occurs on gate paths
