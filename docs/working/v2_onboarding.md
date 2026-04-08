# V2 Onboarding

## 1. Purpose

This document plans the v2 onboarding flows for Forge.

Onboarding exists so users do not need to hand-author the entire Forge doc system before they can use the workflow.

Two onboarding paths are expected:

1. new project onboarding
2. existing project adoption

---

## 2. Shared Onboarding Goals

Both flows should aim to produce:

- an initialized Forge directory structure
- a usable first draft of canonical docs
- working docs aligned to the project state
- a valid docs manifest and docs index
- starter agent/model profile data
- a first actionable backlog
- explicit open questions for unresolved decisions

The output should be useful, not perfect.

---

## 3. New Project Onboarding

Target:
- a guided agent flow for bootstrapping a brand-new project into Forge

Expected pattern:
- ask questions first
- generate docs second
- leave unresolved decisions in `open_questions.md`

Expected inputs:
- project name
- purpose
- users
- scope boundaries
- tech stack
- deployment target
- testing expectations
- project type for adapter selection

Expected outputs:
- starter canonical docs
- working docs
- manifest
- initial backlog
- initial open questions

---

## 4. Existing Project Adoption

Target:
- a guided agent flow for adding Forge to an already-existing repository

Expected pattern:
- scan repo first
- ask targeted follow-up questions second
- generate draft docs third

Constraints:
- additive only
- do not overwrite existing project files
- treat generated canonical docs as draft until reviewed

Expected additional outputs:
- adoption-specific open questions
- change proposal stubs when current project structure conflicts with Forge assumptions

---

## 5. Adapter Relationship

Onboarding should select or recommend adapters as part of the flow.

Reason:
- adapters determine what Forge should care about in execution and validation
- onboarding is the first point where project type is known clearly

Onboarding should not need the full adapter implementation to start planning, but it does depend on a stable adapter contract before full implementation.

---

## 6. Design Constraints

- onboarding should remain agent-first, not form-heavy
- generated docs should be editable and inspectable markdown
- onboarding should surface ambiguity instead of guessing through it
- outputs should fit the same authority model as any hand-built Forge repo
- onboarding should not hide major decisions inside prompt prose

---

## 7. Resolved Planning Decisions (P7-T01, 2026-04-07)

### Q1 — Prompt-only or thin CLI entrypoint?
Decision:
- use a hybrid surface for the minimal slice:
  - stable prompt entrypoint for question-first onboarding flow (`P7-T02`)
  - thin CLI support through `forge init` scaffolding/options (`P7-T03` onward)

Why:
- keeps onboarding agent-first while preserving predictable local CLI mechanics.

### Q2 — Existing-project scan depth versus token cost?
Decision:
- do not implement existing-project scan behavior in the first Phase 7 slice.
- keep adoption flow deferred behind `P7-T07` until new-project onboarding is stable.

Why:
- avoids mixing two onboarding modes before the new-project path is proven.

### Q3 — Canonical docs draft versus ready-to-use?
Decision:
- generate canonical docs from templates as starter drafts that are immediately usable for execution, but still expected to be reviewed/edited by the operator.
- unresolved project specifics must be captured in working docs/open questions rather than guessed.

Why:
- preserves momentum without implying canonical completeness from generated defaults.

### Q4 — Generate starter packet immediately or stop at backlog?
Decision:
- support an optional starter packet bootstrap step in onboarding (`P7-T05`), not mandatory by default.

Why:
- reduces time-to-first-task while preserving safe, additive initialization behavior.

### Q5 — Provider/CLI selection during onboarding?
Decision:
- keep provider routing generic in the minimal slice; do not add provider-specific onboarding capture yet.
- retain existing model-class abstraction and allow manual provider selection post-onboarding.

Why:
- keeps first slice model-agnostic and avoids premature provider-coupled branching.

---

## 8. Minimal Phase 7 Slice (Locked)

In scope now:
- new-project onboarding flow only
- prompt entrypoint + thin `forge init` onboarding support
- adapter selection focused on proving `code_adapter` path
- optional starter packet bootstrap

Out of scope for this slice:
- existing-project adoption execution path
- deep repo scan heuristics and token-optimized scan tuning
- provider-specific onboarding branches
- onboarding expansion for `frontend_adapter` before `code_adapter` path is proven

Exit criteria for this slice:
- `P7-T02` through `P7-T06` completed and reviewed
- integration path demonstrates end-to-end new-project onboarding with stable artifacts
- adoption flow remains deferred until the above is stable

---

## 9. Current Planning State

Phase 7 is closed.

Current state:
- new-project onboarding slice is complete (P7-T01 through P7-T07, 7/7 tasks done)
- 419 tests passing at Phase 7 close
- `P7-T07` boundary doc for existing-project adoption is recorded in §10 below
- full existing-project adoption implementation remains deferred until FR-013 entry criteria are satisfied
- active execution has moved to Phase 8 (Workflow Automation Runner Foundation)

---

## 10. Existing-Project Adoption Entry Criteria (P7-T07, 2026-04-07)

Existing-project adoption work may be promoted from deferred planning into active implementation only when all criteria below are true:

1. the new-project onboarding slice (`P7-T02` through `P7-T06`) is completed, reviewed, and considered stable in working docs
2. onboarding prompt surface remains stable (`workflow.onboard.new` + `workflow.init` compatibility path) without unresolved drift
3. init scaffolding, adapter capture, and optional bootstrap behavior are covered by integration tests and passing in CI/local runs
4. existing-project adoption scope is explicitly additive:
   - no overwriting existing project files
   - generated canonical docs remain draft until human review
5. first existing-project slice is planning/scaffold-only:
   - no deep scan heuristics tuning in the first packet
   - no provider-specific branching
   - no frontend-specific expansion before baseline `code_adapter` path is validated for adoption

Boundary rule:
- before the above criteria are met, `FR-013` remains planning-only and no execution packets should implement existing-project adoption behavior.

When criteria are met:
- promote a scoped existing-project adoption starter task from roadmap/backlog planning into active execution (next phase boundary).
