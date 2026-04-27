# Handoff: TASK-0138

## Final State
`Add a recognized terminal project-complete workflow state` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0138
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 terminal-state fix. Grain now recognizes a terminal `complete` state in `current_focus.md`, returns a dedicated `project_complete` stop reason from workflow evaluation, and reports no phase action from `phase next` when the project is intentionally complete. This replaces the previous parse-error behavior while keeping the evaluator read-only and deterministic.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm that `Phase: complete` is the right terminal marker spelling for docs and future prompts.
- - Confirm no downstream command should continue offering task-level work once the project is marked complete.
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `src/grain/services/workflow_service.py` — added terminal `complete` phase parsing and `project_complete` stop handling
- - `src/grain/services/workflow_run_service.py` — mapped `project_complete` through the workflow-run gate contract
- - `src/grain/cli/phase.py` — reports no phase action when the project is marked complete
- - `tests/test_workflow_state_service.py` — added project-complete evaluator coverage
- - `tests/test_phase_next_cmd.py` — added phase-next coverage for project-complete state
- 

## Reviewer Notes
- - Confirm that `Phase: complete` is the right terminal marker spelling for docs and future prompts.
- - Confirm no downstream command should continue offering task-level work once the project is marked complete.
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
