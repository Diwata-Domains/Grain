# Task: Implement adapter domain model

## Metadata
- **ID:** TASK-0055
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T02
- **Packet Path:** tasks/P6-T02-TASK-0055/
- **Dependencies:** TASK-0054

## Objective
Create the adapter domain model for runtime adapter profiles by introducing an `AdapterProfile` dataclass with the required contract fields and optional hint sections used by later loader and context tasks.

## Why This Task Exists
Phase 6 needs a stable domain object before implementing profile parsing and context integration. This packet provides the smallest reusable model that matches the contract introduced in `adapter_profiles.md`.

## Scope
- Add `src/forge/domain/adapters.py` with `AdapterProfile`.
- Include required fields (`adapter_id`, `domain_type`, `applies_to`) and optional hint section fields.
- Add focused unit tests for required fields and safe default behavior.

## Constraints
- Keep this packet domain-only; do not implement parsing/loading logic.
- Do not change packet parser, context service, or routing behavior.
- Preserve adapter-neutral behavior for existing workflows.

## Escalation Conditions
- If the adapter profile runtime contract is ambiguous or conflicts with higher-authority docs, stop and record a blocker.
- If field shape cannot be represented cleanly in a dataclass, stop and document the conflict for planning.
