# Deliverable Spec: TASK-0070

## Required Output

### New Files
- `tasks/P8-T10-TASK-0070/task.md` — task definition
- `tasks/P8-T10-TASK-0070/context.md` — context selection
- `tasks/P8-T10-TASK-0070/plan.md` — execution plan
- `tasks/P8-T10-TASK-0070/deliverable_spec.md` — this file
- `tasks/P8-T10-TASK-0070/results.md` — execution results
- `tasks/P8-T10-TASK-0070/handoff.md` — reviewer handoff

### Modified Files
- `docs/canonical/cli_spec.md` — new §6.9 `forge verify` command group added; §12 updated to include verify commands
- `docs/working/v2_plan.md` — new §11 Sentinel Bridge Contract added
- `docs/working/backlog.md` — P8-T10 status: ready → in_progress
- `docs/working/current_task.md` — set to TASK-0070, in_progress

## Acceptance Checklist
- [ ] cli_spec.md §6.9 exists with three forge verify subcommands (submit, status, ingest)
- [ ] Each verify subcommand has: purpose, responsibilities, must not, recommended options, deferral note
- [ ] cli_spec.md §12 command coverage list includes forge verify submit/status/ingest with a deferred note
- [ ] No existing cli_spec.md sections were altered (only §6.9 and §12 additions)
- [ ] v2_plan.md §11 exists with: command surface reference, result payload schema, verification gate stop condition, bridge contract terms
- [ ] Payload schema includes at minimum: verification_id, task_id, issue_type, severity, outcome, artifact_refs, summary
- [ ] Verification gate stop condition is consistent with v2_plan.md §10.4 stop conditions
- [ ] No other canonical docs modified
- [ ] review bundle complete in results.md and handoff.md

## Not Required
- Forge verify command implementation (src/ changes)
- Sentinel implementation of any kind
- Changes to workflow_spec.md, architecture.md, product_scope.md, or data_contracts.md
- Test coverage (no executable code added)
