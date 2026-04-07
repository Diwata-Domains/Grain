# Task: Add golden fixtures for manifests and packets

## Metadata
- **ID:** TASK-0051
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T07
- **Packet Path:** tasks/P5-T07-TASK-0051/
- **Dependencies:** TASK-0045, TASK-0046, TASK-0047, TASK-0048, TASK-0049, TASK-0050

## Objective
Create stable fixture files for representative repository manifests and review-ready packet artifacts, then use those fixtures in the Phase 5 integration and review tests.

## Why This Task Exists
Phase 5 needs durable fixture data so integration and review tests can rely on deterministic manifest and packet content instead of repeated inline blobs.

## Scope
- Add golden manifest and packet fixture files under `tests/fixtures/`.
- Update the Phase 5 integration and review tests to consume the shared fixtures.
- Keep the fixture set small, explicit, and reusable.

## Constraints
- Stay within CLI-first v1 scope.
- Use local filesystem only.
- Do not change runtime behavior or canonical docs.

## Escalation Conditions
- If the fixture shape does not match the existing CLI/test contracts, stop and record the mismatch rather than broadening the fixture to hide it.
- If the work requires new workflow semantics, escalate through the proposal flow instead of changing canonical docs directly.
