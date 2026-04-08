# Task: Add adapter-selection options to onboarding initialization

## Metadata
- **ID:** TASK-0064
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T04
- **Packet Path:** tasks/P7-T04-TASK-0064/
- **Dependencies:** TASK-0063
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add `--primary-adapter` and repeatable `--secondary-adapter` options to `forge init`. Validate declared adapters against runtime adapter profiles when available, surface selected adapters in scaffold output, and degrade safely when no adapters are declared or when profile loading fails.

## Why This Task Exists
Phase 7 requires adapter-awareness from the first init so new projects start with domain context declared explicitly. P7-T03 established baseline seed file creation; this task wires adapter selection on top of it.

## Scope
- `--primary-adapter` (single string) and `--secondary-adapter` (repeatable) CLI options on `forge init`
- Validation against `adapter_profiles.md` loaded from the source Forge repo
- Unknown adapters produce warnings; valid ones are recorded in `InitResult` and surfaced in command output
- No adapter declared = adapter-neutral (all existing behavior unchanged)
- `CommandResult` extended with `primary_adapter` and `secondary_adapters` fields

## Constraints
- Additive-only change to existing `init` behavior — no regression to file creation or dry-run logic
- Adapter profiles are advisory; unresolvable profile source must not block init
- Do not modify canonical docs

## Escalation Conditions
- If adapter contract changes require a canonical update, stop and raise a change proposal

## Reviewer Focus
- Existing init tests still pass without adapter args
- Valid adapter IDs are accepted; invalid ones warn without failing
- Dry-run with adapters validates correctly without writing files
