# Task: Wire adapter hints into context assembly

## Metadata
- **ID:** TASK-0058
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T05
- **Packet Path:** tasks/P6-T05-TASK-0058/
- **Dependencies:** TASK-0057
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
When a packet declares a `primary_adapter`, bias context assembly toward that adapter's `relevant_file_patterns` and apply `context_priority_rules`, while preserving adapter-neutral behavior when no adapter is declared.

## Why This Task Exists
Phase 6 requires adapter-aware context selection before adapter review/validation hints can be surfaced in context output.

## Scope
- Read packet `primary_adapter` from task metadata during context bundle assembly.
- Load adapter profiles and resolve the declared primary adapter profile.
- Include adapter-biased source files in context bundle source ordering using `relevant_file_patterns`, `ignore_file_patterns`, and `context_priority_rules`.
- Keep no-adapter packet behavior unchanged.

## Constraints
- Adapter hints supplement existing context selection and must not replace canonical/working doc selection.
- Do not infer adapters when packet metadata does not declare one.
- Do not add review/test hint output in this packet (deferred to P6-T06).

## Escalation Conditions
- If adapter profile loading/parsing conflicts with context assembly contracts, stop and record blocker details.
- If adapter bias logic requires canonical contract changes, stop and file a change proposal.
