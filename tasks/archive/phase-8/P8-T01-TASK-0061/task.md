# Task: Lock minimal workflow automation slice and stop-condition rules

## Metadata
- **ID:** TASK-0061
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T01
- **Packet Path:** tasks/P8-T01-TASK-0061/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Resolve and record the minimal workflow-automation runner slice boundaries for Phase 8: next-legal-step definition, stop conditions, review/verification gates, and required machine-readable command outputs.

## Why This Task Exists
Phase 8 must begin with a narrow planning contract before implementation tasks can proceed safely. Without this boundary, runner implementation risks overreach and workflow drift.

## Scope
- Update `docs/working/v2_plan.md` with explicit minimal-slice rules and stop-condition behavior.
- Align `docs/working/backlog.md` readiness/status transitions for P8 tasks that depend on `P8-T01`.
- Update `docs/working/current_focus.md` and `docs/working/open_questions.md` so phase guidance and decisions match the new boundary.

## Constraints
- Keep this task planning-only; do not implement runner code in this packet.
- Preserve CLI-first and machine-readable automation direction.
- Do not modify canonical docs directly.

## Escalation Conditions
- If minimal-slice boundaries require canonical workflow changes, log a change proposal instead of editing canonical docs.
- If a required stop-condition decision cannot be made from current planning docs, record a blocking open question.

## Model Selection Rationale
`frontier_model` is appropriate because this packet sets cross-task runner boundaries that govern subsequent CLI/service implementation work.
