# Task: Resolve adapter contract open questions and create adapter_profiles.md

## Metadata
- **ID:** TASK-0054
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T01
- **Packet Path:** tasks/P6-T01-TASK-0054/
- **Dependencies:** none

## Objective
Resolve the open planning questions in `docs/working/v2_adapters.md` section 9 and create `docs/runtime/adapter_profiles.md` with the initial adapter contract plus `code_adapter` and `frontend_adapter` profiles.

## Why This Task Exists
Phase 6 starts by stabilizing adapter contract direction before any parser/domain/context code changes. A concrete runtime profile document is needed to ground later implementation tasks.

## Scope
- Create `docs/runtime/adapter_profiles.md` with contract and initial adapter profiles.
- Register `adapter_profiles` in `docs/runtime/docs_manifest.yaml`.
- Mark v2 adapter planning questions resolved in `docs/working/v2_adapters.md`.
- Refresh `docs/runtime/docs_index.md` from manifest updates.

## Constraints
- Keep changes at runtime/working doc level only.
- Do not implement adapter loader/domain/context behavior in this packet.
- Preserve adapter-neutral fallback behavior direction.

## Escalation Conditions
- If resolving planning questions requires canonical contract changes, stop and raise a change proposal.
- If profile schema cannot be expressed cleanly in runtime docs, stop and document blockers.
