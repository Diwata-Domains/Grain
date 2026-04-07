# V2 Plan

## 1. Purpose

This document captures v2 transition and sequencing after v1 closure.

It exists to:
- define the post-v1 transition boundary
- sequence the first v2 workstreams
- prevent premature v2 implementation drift while planning proceeds

This document does not authorize broad or unsized v2 implementation by itself.
It defines the planning and promotion boundary for post-v1 work.

---

## 2. Planning Boundary

Allowed now:
- v2 scope definition
- adapter contract planning
- onboarding flow planning
- identifying dependencies and open questions
- drafting working-layer planning docs

Not allowed without explicit promotion into scoped work:
- broad unsized v2 implementation
- implementing multiple v2 workstreams in parallel without sequencing
- implementing onboarding flows before the adapter contract is proven
- changing canonical docs for v2 unless a concrete change proposal is approved

---

## 3. Readiness Gates Before V2 Implementation

The first promoted v2 slice should not begin until all of the following are true:

1. Phase 5 is formally closed
2. v1 review, handoff, and close workflow is stable enough to use on new work
3. prompt entrypoints and packet contracts are stable enough to reuse across projects
4. current v1 open questions and applied proposals do not leave core workflow ambiguity
5. v2 planning docs are specific enough to break into task-sized backlog items

---

## 4. V2 Priority Order

Recommended order:

1. adapter system formalization
2. new project onboarding flow
3. existing project adoption flow
4. thin unified CLI surfaces for onboarding and prompt execution
5. Sentinel bootstrap work on top of the above

Reason:
- adapters define how Forge generalizes beyond the current repo
- onboarding depends on adapter selection and stable doc generation targets
- existing-project adoption depends on the same onboarding patterns plus scan rules

---

## 5. First V2 Workstreams

### Workstream A — Adapter System

Target outcome:
- a stable adapter contract that changes execution hints and validation behavior without changing the core workflow contract

Planning doc:
- `docs/working/v2_adapters.md`

### Workstream B — Onboarding Flows

Target outcome:
- clear, agent-driven flows for:
  - new project bootstrap
  - existing project adoption

Planning doc:
- `docs/working/v2_onboarding.md`

---

## 6. Promotion Rule

The first v2 implementation backlog should be created only after:
- Phase 5 close review is complete
- this plan is updated with a concrete v2 sequence
- the adapter and onboarding planning docs have no blocking ambiguities

When promoted:
- move scoped work into `docs/working/backlog.md`
- assign a v2 phase or transition phase label
- keep packets narrow

---

## 7. Current Recommendation

Phase 7 (New-Project Onboarding Flow) is now seeded and active.

- Phase 6 adapter work is complete and provides the dependency base
- `P7-T01` is the first executable onboarding task
- existing-project adoption remains out of the active execution loop until the new-project flow is proven

Active tracking: `docs/working/current_focus.md`

---

## 8. Planning Workflow

Use this planning cadence:

1. `prompts/phase.plan.next.md`
   - define the next phase or transition slice
2. `prompts/phase.tasks.seed.md`
   - generate the initial task slice for a newly defined phase
3. `prompts/phase.replan.md`
   - revise current or next phase only when reality changed materially
4. `prompts/task.plan.next.md`
   - continuously select the next task or split a too-broad backlog item
5. `prompts/task.execute.md`
   - packetize and implement one task
6. `prompts/task.review.md`
   - review one task
7. `prompts/task.close.md`
   - close one reviewed task

Task generation and task splitting belong in the planning layer before packet generation.
Review and close may expose the need for a split, but they should not own backlog planning.
