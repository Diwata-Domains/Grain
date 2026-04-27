# Handoff: TASK-0067

## Final State
`forge prompt show` implemented and registered; packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0067
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added forge prompt show — a read-only command that surfaces the recommended prompt entrypoint and metadata for the current workflow state in both text and JSON output.

## What Was Built
- `prompt_service.py` — evaluates workflow state, extracts recommended prompt, parses Metadata: block
- `prompt.py` — `forge prompt show` CLI command with text/JSON output
- `__init__.py` — registered `prompt_group`
- `prompts/README.md` — machine-readable surface documentation added
- `tests/test_prompt_show_cmd.py` — 11 tests

## What Review Should Check
- `forge prompt show` exits 0 for both active and stopped workflow states
- JSON `prompt` key contains all fields from the Phase 8 contract (§10.5)
- Metadata parsing correctly extracts model_class/scope/stage from prompt files
- `prompts/README.md` Machine-Readable Prompt Surface section is accurate

## What Was Not Done
- `forge workflow run` (P8-T08 — depends on P8-T07)
- Sentinel bridge (P8-T10 — blocked)
- Working-doc reconciliation (P8-T11)

## Known Issues or Follow-ups
- None

## Files Changed
- `src/forge/services/prompt_service.py` (new)
- `src/forge/cli/prompt.py` (new)
- `src/forge/cli/__init__.py` — prompt_group registered
- `prompts/README.md` — new section
- `tests/test_prompt_show_cmd.py` (new)
- `docs/working/current_task.md` — pointer updated

## Reviewer Notes
The pattern follows `phase.py` and `workflow.py` exactly. The only novel piece is `_parse_prompt_metadata` which reads the Metadata: block from prompt files. This keeps prompt metadata co-located with the prompt itself rather than in a separate config.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
