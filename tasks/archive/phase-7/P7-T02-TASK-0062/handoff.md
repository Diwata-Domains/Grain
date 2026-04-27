# Handoff: TASK-0062

## Final State
Stable new-project onboarding prompt entrypoint was added and the packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0062
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added `workflow.onboard.new` as the stable onboarding prompt and converted `workflow.init` into a compatibility alias.

## What Was Built
- Added `prompts/workflow.onboard.new.md` with question-first onboarding intake and explicit adapter-selection fields.
- Converted `prompts/workflow.init.md` into compatibility guidance that points to the new stable onboarding prompt.
- Updated `README.md` and `prompts/README.md` onboarding references to prefer the new prompt and preserve compatibility context.

## What Review Should Check
- New-project onboarding references consistently point to `prompts/workflow.onboard.new.md`.
- `prompts/workflow.init.md` clearly behaves as a compatibility alias and does not redefine onboarding contracts.
- New prompt keeps existing-project adoption out of scope and preserves model-agnostic/provider-generic wording.

## What Was Not Done
- Existing-project onboarding implementation flow
- `forge init` scaffolding/file-writing enhancements (`P7-T03`)
- Adapter-selection CLI option behavior (`P7-T04+`)

## Known Issues or Follow-ups
- Existing-project onboarding still relies on temporary compatibility guidance until dedicated flow work lands.

## Files Changed
- `prompts/workflow.onboard.new.md` — stable new-project onboarding prompt
- `prompts/workflow.init.md` — compatibility alias update
- `prompts/README.md` — prompt index updates
- `README.md` — onboarding guidance updates
- `docs/working/current_task.md` — active task status set to review
- `tasks/P7-T02-TASK-0062/task.md` — packet definition
- `tasks/P7-T02-TASK-0062/context.md` — task context
- `tasks/P7-T02-TASK-0062/plan.md` — execution plan
- `tasks/P7-T02-TASK-0062/deliverable_spec.md` — deliverable contract
- `tasks/P7-T02-TASK-0062/results.md` — execution results
- `tasks/P7-T02-TASK-0062/handoff.md` — handoff

## Reviewer Notes
This packet is prompt/docs surface work only; no code-path behavior changes were made in CLI/services.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Existing-project onboarding prompt/flow should replace temporary compatibility guidance when Phase 7 reaches `P7-T07`.
