# Current Focus

## Current Phase
Phase 7 — New-Project Onboarding Flow (seeded, execution-ready)

## V1 Status
Complete. All 5 phases closed. 53 tasks done. 379 tests passing at v1 close.

## Phase 6 Status
CLOSED. All 7 tasks done. 399/399 tests passing. Adapter contract proven with `code_adapter`. Phase closed 2026-04-06.

## Immediate Goals
1. review `P7-T01` and confirm Phase 7 planning decisions are locked
2. execute `P7-T02` (prompt entrypoint) and `P7-T03` (`forge init` scaffolding) in sequence
3. keep onboarding narrow: prove `code_adapter` flow first, then generalize

## Active Constraints
- use local filesystem only
- preserve the stable v1 workflow as the core
- do not start blocked/deferred Phase 7 items before dependency and readiness rules are met
- scope onboarding narrowly: prove with one adapter before generalizing
- keep provider handling model-agnostic in the first onboarding slice

## Do Not Work On Right Now
- existing-project adoption flow implementation (Phase 7 — represented as blocked `P7-T07` until new-project flow is stable)
- Sentinel (v2 — FR-005)
- advisory/intelligence layer (v2)
- telemetry automation (v2 — FR-011)
- frontend_adapter onboarding expansion (defer until code_adapter onboarding path is proven)
