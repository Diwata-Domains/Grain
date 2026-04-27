# Handoff: TASK-0139

## Final State
`Make upgrade safer for customized repo doc layouts` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0139
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 upgrade-safety fix. `grain upgrade` now distinguishes stale managed files that contain local user additions, skips overwriting those files by default in non-interactive mode, and reports them as customized/skipped so operators can review them explicitly with `--interactive` or inspect them with `--diff`. This preserves normal update behavior for uncustomized managed files while reducing destructive-looking upgrade guidance for customized repos.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the default skip behavior is the right non-interactive contract for customized managed files.
- - Confirm `grain upgrade --interactive` remains the preferred explicit path for applying bundled changes into customized repos.
- 

## What Was Not Done
- [follow-up, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `src/grain/services/upgrade_service.py` — added customized-file detection and default skip behavior for locally modified managed files
- - `src/grain/cli/upgrade.py` — surfaced `skipped_customized` in text and JSON output and redirected operators to interactive or diff review
- - `tests/test_upgrade_cmd.py` — added coverage for default skip behavior, explicit apply behavior, and CLI reporting
- 

## Reviewer Notes
- - Confirm the default skip behavior is the right non-interactive contract for customized managed files.
- - Confirm `grain upgrade --interactive` remains the preferred explicit path for applying bundled changes into customized repos.
- 

## Closeout Intake

### Open Questions To Log
- [question, or "None"]

### Proposal Candidates To Log
- [proposal, or "None"]

### Follow-Ups To Log
- [follow-up, or "None"]
