# Task: Add stable new-project onboarding prompt entrypoint

## Metadata
- **ID:** TASK-0062
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T02
- **Packet Path:** tasks/P7-T02-TASK-0062/
- **Dependencies:** TASK-0061
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create a stable new-project onboarding prompt entrypoint with a question-first flow and explicit adapter-selection inputs, then convert `prompts/workflow.init.md` into compatibility guidance and align `README.md` onboarding instructions to the new entrypoint.

## Why This Task Exists
Phase 7 requires a clear, stable onboarding prompt surface before `forge init` scaffolding expansion. Without a dedicated entrypoint, onboarding guidance remains ambiguous and harder to apply consistently for new projects.

## Scope
- Add `prompts/workflow.onboard.new.md` as the stable new-project onboarding prompt.
- Update `prompts/workflow.init.md` to act as a compatibility alias that points to the new entrypoint.
- Update onboarding references in `README.md` to prefer the new prompt while preserving compatibility notes.

## Constraints
- Do not edit canonical docs directly.
- Keep onboarding scoped to new-project flow; existing-project adoption remains deferred.
- Keep provider handling model-agnostic in this first onboarding slice.

## Escalation Conditions
- If onboarding requirements conflict with locked Phase 7 decisions in `docs/working/v2_onboarding.md`, stop and log the conflict before proceeding.
- If this task requires canonical workflow/contract changes, log a change proposal instead of editing canonical docs.

## Model Selection Rationale
`frontier_model` is appropriate because this task coordinates onboarding behavior across multiple prompt/docs surfaces and must preserve Phase 7 scope boundaries without drift.
