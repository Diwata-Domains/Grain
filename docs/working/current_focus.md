# Current Focus

## Current Phase
Phase 4 — Context Assembly and Model Routing

## Phase 4 Status
- P4-T01 through P4-T08 are done
- Next implementation target: P4-T09

## Phase 3 Status
Complete. 13/13 tasks done. 272/272 tests passing at close.

## Immediate Goals
1. implement model selection logic (P4-T09)
2. implement `forge model show` (P4-T10)
3. implement `forge model select` (P4-T11)
4. implement `forge model escalate` (P4-T12)
5. add context and routing tests (P4-T13)

## Active Constraints
- stay within CLI-first v1 scope
- use local filesystem only
- context bundle must be exportable for use with external coding agents
- no-tag context invocation defaults to the `running_tasks` tag set
- context command JSON surfaces are intentionally distinct by command and now canonically documented
- model selection must support open_model, frontier_model, reviewer_model classes
- no database or background-service dependencies
- requires Phase 2 document registry (done) and Phase 3 task packet system (done)

## Do Not Work On Right Now
- review automation (Phase 5)
- handoff artifact generation (Phase 5)
- golden-path integration tests (Phase 5)

## Definition of Progress for Phase 4
Phase 4 is complete when:
- a packet context bundle can be assembled via `forge context build`
- context sources can be inspected via `forge context show`
- context can be exported via `forge context export`
- model class can be resolved and displayed via `forge model show` / `forge model select`
- model escalation is supported via `forge model escalate`
- context and routing tests cover selection boundaries
- all Phase 4 task packets are either `done` or explicitly deferred
