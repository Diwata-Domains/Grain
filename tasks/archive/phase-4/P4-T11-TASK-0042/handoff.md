# Handoff: TASK-0042

## Final State
`forge model select` is implemented, tested, and closed.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0042
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** `forge model select` wires the existing model routing service into a functional CLI command with text/JSON output.

## What Was Built
- `forge model select --stage <stage>` and `--stage --role` option support
- Text output: `model select: ok`, `selected_class`, `reason`, `stage`, `role`
- JSON output: `{ok, command, repo, selected_class, reason, stage, role}`
- UsageError guard when neither option is provided
- 5 CLI tests covering all key paths

## What Review Should Check
- `--stage` and `--role` are forwarded unchanged to `select_model_for_stage_or_role`
- JSON shape is stable and complete per CLI spec §6.5
- UsageError fires when invoked with no options
- Missing `agent_profiles.md` causes non-zero exit and error output
- No routing logic is inlined in the CLI; service call is the only routing path

## What Was Not Done
- `forge model escalate` (P4-T12)
- Changes to `model_service.py` or `routing.py`

## Known Issues or Follow-ups
- None blocking for this packet.

## Files Changed
- `src/forge/cli/model.py` — implemented `model_select` command body
- `tests/test_model_select_cmd.py` — new CLI test file (5 tests)

## Reviewer Notes
Full test suite is green at 332/332. Implementation is a thin wiring layer; all logic lives in the service and domain layers from P4-T09.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- `model_escalate` silent stub remains; update when P4-T12 is implemented (pending CP-005).
- Consider adding an error-message assertion to `test_model_select_missing_profile_exits_nonzero`.
