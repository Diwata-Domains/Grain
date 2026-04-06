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

## 7. Open Planning Questions

1. Should new-project onboarding be prompt-only in v2, or also have a thin CLI entrypoint?
2. How should existing-project scans balance accuracy against token cost?
3. Which canonical docs should be generated as draft versus ready-to-use?
4. Should onboarding generate one starter backlog packet immediately, or stop at backlog creation?
5. How should onboarding handle provider/CLI selection — should it ask "which agent CLI do you use" (claude, codex, open model) and record that in agent_profiles.md, or leave it as a post-onboarding manual step?

---

## 8. Recommended Next Planning Step

When Phase 5 closes:
- define the question flow for new-project onboarding
- define the scan-and-question flow for existing-project adoption
- decide which outputs are generated directly versus scaffolded as draft
