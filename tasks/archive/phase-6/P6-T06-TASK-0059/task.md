# Task: Surface adapter review and validation hints in context output

## Metadata
- **ID:** TASK-0059
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T06
- **Packet Path:** tasks/P6-T06-TASK-0059/
- **Dependencies:** TASK-0058
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
When an active adapter is declared, surface adapter `review_focus_hints` and `test_or_validation_hints` in context outputs so operators can see adapter-specific guidance during `context build` and `context export`.

## Why This Task Exists
Phase 6 requires adapter hints to be visible in context artifacts before full adapter-system validation can be completed in `P6-T07`.

## Scope
- Add adapter hint fields to context bundle metadata output.
- Surface adapter hint summaries in CLI text outputs and include adapter context in JSON export output.
- Render adapter hint sections in markdown context exports when an adapter is active.
- Add focused tests for build/export behavior with active adapter hints.

## Constraints
- Adapter hints are advisory only and must not enforce validation rules.
- No-adapter behavior must remain adapter-neutral and backward compatible.

## Escalation Conditions
- If hint-surfacing requires changes to canonical contracts, stop and record a change proposal before editing canonical docs.
- If context export shape changes break existing automation, stop and log the compatibility blocker.
