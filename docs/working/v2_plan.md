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
3. global installation and distribution paths
4. workflow automation runner foundation
5. existing project adoption flow
6. thin unified CLI surfaces for onboarding and prompt execution
7. Sentinel bootstrap work on top of the above
8. GUI/dashboard surface on top of stable workflow and verification primitives

Reason:
- adapters define how Forge generalizes beyond the current repo
- onboarding depends on adapter selection and stable doc generation targets
- global installation matters once onboarding is usable, because users should be able to invoke `forge` from any directory without relying on a repo-local virtualenv
- workflow automation should wrap a proven onboarding and packet model before interface layers expand
- existing-project adoption depends on the same onboarding patterns plus scan rules
- GUI work should sit on top of stable command/state primitives rather than forcing them into existence indirectly

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

### Workstream C — Workflow Automation Runner

Target outcome:
- a state-driven CLI layer that can tell agents and operators the next legal workflow step, prepare packet execution state, and stop cleanly at review or verification gates

Planning doc:
- `docs/working/v2_plan.md` §9

### Workstream D — Global Installation and Distribution

Target outcome:
- Forge can be installed as a global tool so users can invoke `forge` from any directory without depending on a repo-local virtualenv

Planning doc:
- `docs/working/future_roadmap.md` (`FR-004b`)

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

Phase 8 (Workflow Automation Runner Foundation) is now seeded and ready for planning.

- Phase 6 adapter work is complete
- Phase 7 new-project onboarding is complete (7/7 tasks, 419 tests passing)
- existing-project adoption remains deferred behind FR-013 entry criteria
- Phase 8 planning begins with `P8-T01` to lock the minimal runner slice and stop-condition rules

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

---

## 9. Operator Surface Guidance

Near-term surface order:

1. CLI/state primitives
2. workflow automation runner on top of file-backed state
3. machine-readable JSON output for automation-relevant commands
4. Sentinel bridge and verification-aware stop conditions
5. thin TUI only if operator friction remains high
6. GUI only after broader non-terminal demand is proven

Recommended CLI-first automation additions:

- `forge workflow next`
  - inspect repo state and report the next legal workflow step plus blockers
- `forge workflow run`
  - execute one legal workflow step or stop with an explicit gate reason
- `forge phase next`
  - surface whether phase planning/review/close is the next valid action
- `forge task next`
  - choose the next actionable task or report why planning is required first
- `forge task prepare`
  - ensure packet/context/prompt prerequisites are assembled for one task
- `forge prompt show`
  - display the recommended stable prompt entrypoint and required inputs for the current state
- `forge prompt run`
  - optional later wrapper for launching a stable prompt surface without changing prompt authority
- `forge verify ...` or `forge sentinel ...`
  - verification bridge commands for Sentinel submission, status, and result ingestion

Feedback and self-improvement guidance:

- Forge should accept structured workflow feedback about friction, ambiguity, token waste, manual rework, and runner gaps
- Sentinel should accept structured verification feedback about bugs, failures, screenshots, traces, repro steps, and optional human comments
- both systems may emit candidate follow-up work, but neither should bypass review or canonical change gates
- user feedback should be modeled as first-class artifacts rather than free-form notes only

Reconciliation strategy for working-doc state:

- keep a manual reconciliation checklist in review/close flow so dependent working docs are updated at the point of change
- add an explicit `forge workflow reconcile` command for humans and agents to detect or repair drift after the fact
- enforce the same consistency rules inside the workflow runner so it can warn or stop before drift spreads

Prompt-to-command rule:

- do not require a 1:1 CLI command for every prompt
- commands should own deterministic operations, state transitions, validation, exports, and tool integration
- prompts should remain the reasoning surface for planning, drafting, scoped execution, and judgment-heavy review
- when a prompt becomes repetitive, state-driven, and machine-parameterizable, it is a candidate for CLI automation

---

## 10. Phase 8 Minimal Slice Contract (P8-T01, 2026-04-07)

This section locks the smallest valid runner slice before implementation begins.

### 10.1 Scope In

- runner reads current repo/task/phase state and reports one next legal workflow action
- runner can execute at most one legal step per invocation
- runner stops at review and verification gates; it does not auto-bypass them
- runner outputs machine-readable JSON for automation-relevant commands

### 10.2 Scope Out

- multi-step autonomous execution loops
- hidden planning or backlog mutation without explicit command/action
- automatic canonical edits
- TUI/GUI-specific behavior
- Sentinel bridge execution behavior (tracked separately)

### 10.3 Next-Legal-Step Definition (v1 slice)

For the first runner slice, next legal step resolution is constrained to:

1. `task planning` when no ready task exists and backlog action is required
2. `task execute` when one ready task is available and no active review gate blocks execution
3. `task review` when current task status is `review`
4. `task close` only after review artifacts are complete
5. `phase review/close` only when no executable task remains in the active phase

### 10.4 Stop Conditions

Runner must stop (with explicit reason) when:

- active task is `blocked`
- review artifacts are missing/incomplete for a `review` task
- phase boundary is reached and phase-level review/close is required
- required docs or packet files are missing/invalid
- multiple conflicting next actions exist and cannot be resolved deterministically

### 10.5 Machine-Readable Output Boundary

The following command surfaces are required to emit stable JSON for automation:

- `forge workflow next`
- `forge workflow run`
- `forge phase next`
- `forge task next`
- `forge task prepare`
- `forge prompt show`

Each should include at minimum:
- `ok`
- `next_action` (or `stop_reason`)
- `blocking_reasons` (empty list when none)
- `recommended_prompt` (when applicable)
- `affected_artifacts`

### 10.6 Sequencing Effect

With this boundary locked:
- `P8-T02` is unblocked and ready to implement the workflow state evaluator service
- later P8 tasks must conform to the one-step and stop-condition contract above
