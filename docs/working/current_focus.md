# Current Focus

## Current Phase
Phase 8 — Workflow Automation Runner Foundation (in progress)

## V1 Status
Complete. All 5 phases closed. 53 tasks done. 379 tests passing at v1 close.

## Phase 6 Status
CLOSED. All 7 tasks done. 399/399 tests passing. Adapter contract proven with `code_adapter`. Phase closed 2026-04-06.

## Phase 7 Status
COMPLETE. 6/6 active tasks done (P7-T01 through P7-T06). P7-T07 intentionally deferred/blocked. 454/454 tests passing at Phase 7 implementation complete (2026-04-08). Phase 7 delivered: onboarding prompt entrypoint, seed-file scaffolding, adapter-selection options, starter-packet bootstrap, and Phase 7 integration tests.

## Phase 8 Progress
P8-T01 through P8-T08 done. P8-T09 (harden outputs + integration tests) in progress. 494/494 tests passing.

## Immediate Goals
1. complete `P8-T09` (TASK-0069) — harden machine-readable automation outputs and add runner integration tests
2. after P8-T09: determine if phase review/close is next or if P8-T11 (working-doc reconciliation) should be promoted to ready first

## Active Constraints
- use local filesystem only
- preserve the stable v1 workflow as the core
- keep workflow automation narrow: define the smallest runner slice before expanding breadth
- preserve machine-readable CLI outputs for workflow actions
- do not start TUI/GUI implementation before CLI-first workflow automation and Sentinel bridge surfaces are defined

## Do Not Work On Right Now
- Sentinel (v2 — FR-005)
- P8-T10 (blocked — depends on Sentinel bootstrap expectations)
- advisory/intelligence layer (v2)
- telemetry automation (v2 — FR-011)
- autonomous workflow execution beyond one legal runner step
- TUI/GUI implementation before the workflow runner and verification-facing command surfaces exist
