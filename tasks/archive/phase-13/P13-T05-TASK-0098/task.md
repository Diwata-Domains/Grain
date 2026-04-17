# Task: Phase 13 integration tests

## Metadata
- **ID:** TASK-0098
- **Status:** done
- **Phase:** Phase 13 — Existing Project Adoption
- **Backlog:** P13-T05
- **Packet Path:** tasks/P13-T05-TASK-0098/
- **Dependencies:** TASK-0094, TASK-0095, TASK-0096
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** docs_adapter, frontend_adapter

## Objective
Add a focused Phase 13 integration test suite validating the existing-project adoption flow across onboard scaffold behavior, scanner detection signals, and draft document generation behavior.

## Why This Task Exists
Phase 13 needs integration-level confidence that onboarding, scanning, and draft generation work together on synthetic existing repositories and preserve additive-only safety.

## Scope
- Add `tests/test_phase13_integration.py` with at least 15 tests
- Cover onboard CLI behavior on synthetic existing repos
- Cover `CodebaseScanner` detection behavior on fixture trees
- Cover `OnboardDocGenerator` output shape and draft markers
- Include an end-to-end additive flow assertion across onboard -> scan -> generate

## Constraints
- Tests must remain local and deterministic
- No canonical doc changes
- Keep scope to Phase 13 behavior only

## Escalation Conditions
- If Phase 13 integration expectations conflict with current command/service contracts, stop and record in `docs/working/change_proposals.md`
