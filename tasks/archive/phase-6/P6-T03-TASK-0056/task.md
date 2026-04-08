# Task: Implement adapter profile loader

## Metadata
- **ID:** TASK-0056
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T03
- **Packet Path:** tasks/P6-T03-TASK-0056/
- **Dependencies:** TASK-0055

## Objective
Parse `docs/runtime/adapter_profiles.md` into structured `AdapterProfile` objects via a dedicated adapter config loader module that follows the same runtime-markdown loading pattern as model profile loading.

## Why This Task Exists
Phase 6 needs a concrete adapter loader before packet metadata and context assembly can consume adapter hints. This task turns the adapter profile runtime contract into executable parsing behavior.

## Scope
- Add `src/forge/adapters/adapter_config.py` with load and parse functions.
- Parse adapter profile sections into `AdapterProfile` domain objects.
- Validate required fields and required hint presence from the runtime contract.
- Add focused loader tests.

## Constraints
- Keep scope limited to loader/parsing behavior.
- Do not change packet parsing or context assembly behavior in this packet.
- Keep adapter behavior model-agnostic and config-driven.

## Escalation Conditions
- If runtime adapter profile contract is ambiguous or unparsable without changing canonical docs, stop and log a proposal candidate.
- If loader behavior would require changing packet lifecycle or authority rules, stop and record conflict.
