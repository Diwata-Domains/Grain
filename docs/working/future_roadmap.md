# Future Roadmap

## 1. Purpose

Tracks deferred features, future capabilities, and post-v1 ideas that should not disrupt current execution.

Items here are intentionally **not part of the current phase or immediate backlog**.

They may become:

* future phases
* v2/v3 capabilities
* optional extensions

Forge is a **development orchestration system**.
Future work should expand its capabilities **without destabilizing the core build loop**.

---

## 2. Status Definitions

* `idea` — early concept, not yet evaluated
* `candidate` — worth building, but not scheduled
* `deferred` — explicitly postponed
* `planned` — intended for a future phase/version
* `revisit_later` — unclear value or timing

---

## 3. Future Capabilities

### FR-001 — Adapter System Formalization

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * the Forge workflow (build loop, task packets, model routing, context assembly) is fully language and domain agnostic — adapters are the translation layer that makes it work across any project type
  * without adapters, Forge is implicitly a Python/backend tool; with adapters it works across every domain the user operates in
  * target project types include: Rust, Python, TypeScript/JavaScript, React, Tauri, Storybook, Markdown documentation systems, and Excel/spreadsheet workflows
  * Sentinel must operate across these same domains
* **Scope:**

  * formal adapter interface — defines what an adapter must provide: execution hints, test runner config, validation approach, relevant file patterns, build tool awareness
  * `adapter_profiles` in `docs/runtime/` — one profile per adapter type, loaded by context assembly and model routing
  * execution-target-aware task packets — adapter field in task metadata signals which adapter governs execution and validation for that task
  * initial adapter set:
    * `code_adapter` — Python, Rust, general backend
    * `frontend_adapter` — TypeScript, JavaScript, React, Storybook, Tauri (component-scoped tasks, build tool awareness, browser test runners)
    * `docs_adapter` — Markdown documentation systems, cross-reference validation
    * `spreadsheet_adapter` — Excel/spreadsheet workflows, formula validation, workbook operation specs
  * adapter selection during onboarding (FR-012, FR-013) — agent asks project type and sets adapter profile at project init time
* **Why not now:**

  * Forge core workflow must stabilize first — adapters should wrap a stable core, not a moving one
* **Dependencies:**

  * stable task packet format
  * stable execution loop
  * stable context assembly (Phase 4 complete)
* **Notes:**

  * the workflow itself never changes per adapter — only execution hints, validation rules, and file patterns change
  * adapter design must not require changes to canonical packet or workflow contracts
  * a project may have multiple adapters active (e.g. a Tauri project has both `frontend_adapter` and `code_adapter`)

---

### FR-002 — Spreadsheet Adapter (Excel Integration)

* **Status:** candidate
* **Suggested Target:** v2
* **Why it matters:**

  * enables structured spreadsheet/model workflows
  * expands Forge beyond code into data systems
* **Scope:**

  * workbook operation specification
  * formula validation patterns
  * integration with Excel AI tools
* **Why not now:**

  * execution model differs significantly from file-based workflows
* **Dependencies:**

  * adapter system formalization (FR-001)
* **Notes:**

  * v1: instruction-only
  * v2+: optional execution automation

---

### FR-003 — Image Adapter (Asset Generation Pipeline)

* **Status:** candidate
* **Suggested Target:** v2
* **Why it matters:**

  * supports structured image generation workflows
  * enables asset pipelines for frontend/content systems
* **Scope:**

  * prompt generation system
  * asset naming and organization
  * optional API-based generation
* **Why not now:**

  * requires clear execution abstraction first
* **Dependencies:**

  * adapter system (FR-001)
* **Notes:**

  * validation will remain heuristic, not deterministic

---

### FR-004 — Forge CLI (Unified Command Layer)

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * improves usability beyond raw prompt execution
  * standardizes interaction with Forge
* **Scope:**

  * `forge run <prompt>`
  * `forge task next`
  * `forge phase review`
  * context assembly automation
* **Why not now:**

  * prompts and workflow still evolving
* **Dependencies:**

  * stable prompt library
* **Notes:**

  * should remain thin wrapper, not heavy abstraction

---

### FR-005 — Sentinel (Verification Platform)

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * introduces automated validation and bug detection
  * closes the loop between building and verification
* **Scope:**

  * issue reporting SDK
  * test orchestration engine
  * adversarial bug hunter
  * artifact capture (logs, repro steps, screenshots)
  * ticket + fix pipeline
  * human approval workflow
* **Why not now:**

  * Forge must be stable enough to build Sentinel with it
* **Dependencies:**

  * stable Forge workflow (Phase 5 complete)
  * task packet system
  * adapter groundwork (FR-001)
  * FR-012 — New Project Onboarding Flow (Sentinel is a new project and must be bootstrapped through it)
* **Notes:**

  * Sentinel will feed issues back into Forge as structured work
  * building Sentinel with Forge is the intended v1 real-world validation — if the onboarding flow works cleanly for Sentinel, it proves the system works on a fresh project

---

### FR-006 — Sentinel Integration Layer

* **Status:** candidate
* **Suggested Target:** v3
* **Why it matters:**

  * enables seamless flow from detection → execution
* **Scope:**

  * issue → backlog conversion
  * artifact → task context mapping
  * verification → review gating
* **Why not now:**

  * Sentinel itself must exist first
* **Dependencies:**

  * Sentinel (FR-005)
* **Notes:**

  * integration should remain lightweight

---

### FR-007 — Lightweight UI / Dashboard

* **Status:** idea
* **Suggested Target:** v3
* **Why it matters:**

  * improves visibility of workflow state
* **Scope:**

  * phase view
  * backlog viewer
  * open questions panel
  * metrics dashboard
* **Why not now:**

  * CLI + agent workflow is sufficient for v1
* **Dependencies:**

  * stable workflow + metrics
* **Notes:**

  * must not replace file-based system

---

### FR-008 — Multi-Project / Template System

* **Status:** candidate
* **Suggested Target:** v3
* **Why it matters:**

  * users running multiple concurrent projects (e.g. Rust backend, React frontend, Tauri app, Storybook, docs system) need Forge to be consistent and reusable across all of them without re-inventing the workflow each time
  * enables reuse of canonical doc patterns, adapter profiles, and prompt libraries across projects
* **Scope:**

  * project templates — starter canonical doc sets per project type (backend, frontend, docs, mixed)
  * shared adapter profile library — reuse adapter configs across projects without copying
  * cross-project backlog visibility — optional view across multiple active Forge-managed projects
  * standardized initialization flows that incorporate adapter selection from FR-001
* **Why not now:**

  * requires stable adapter system (FR-001) and onboarding flows (FR-012, FR-013) first
* **Dependencies:**

  * stable Forge core
  * FR-001 (Adapter System)
  * FR-012 (New Project Onboarding)
* **Notes:**

  * aligns with distributing Forge to others
  * multi-project visibility should remain optional and additive — each project stays self-contained by default

---

### FR-009 — Reusable Skill Layer

* **Status:** candidate
* **Suggested Target:** v3
* **Why it matters:**

  * enables portable agent capabilities across multiple Forge projects
  * separates repo-specific workflow prompts from reusable execution or review behaviors
* **Scope:**

  * skill packaging conventions
  * cross-project reviewer/executor capability extraction
  * guidance for when behavior should stay a prompt vs become a reusable skill
  * optional skill registry or distribution model
* **Why not now:**

  * Forge prompt and workflow contracts are still stabilizing
  * extracting skills too early would risk encoding unstable behavior as a reusable abstraction
* **Dependencies:**

  * stable prompt library
  * stable review and close workflow
  * repeated cross-project patterns worth extracting

---

### FR-010 — Contract Freshness Detection

* **Status:** candidate
* **Suggested Target:** v2
* **Why it matters:**

  * reduces stale-context drift when prompts or workflow docs change mid-conversation
  * avoids unnecessary broad rereads while still protecting workflow correctness
* **Scope:**

  * lightweight contract fingerprint or mtime checks
  * warning or hard-stop behavior before review or close when contract files changed
  * narrow tracked file set for prompt, runtime, and workflow-contract files
* **Why not now:**

  * restart-on-change rule is sufficient for v1
  * prompt and workflow contract surfaces are still stabilizing
* **Dependencies:**

  * stable prompt entrypoints
  * stable workflow-contract file set
* **Notes:**

  * prefer targeted file checks over full-repo rescans

---

### FR-011 — Token Efficiency and Cost Control

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * token usage is one of the main blockers in real AI-assisted development workflows
  * Forge should make context smaller, retries rarer, and prompt loops cheaper in a measurable way
* **Scope:**

  * exact token capture when runtimes expose usage
  * proxy efficiency metrics when exact counts are unavailable
  * stage-level token reporting for execute, review, and close
  * guardrails to reduce unnecessary context loading, artifact rewrites, and prompt retries
  * optional token-budget warnings or limits per task or phase
* **Why not now:**

  * v1 can start with manual or proxy tracking in task artifacts and workflow metrics
  * automated cost instrumentation should follow a stable prompt and packet workflow
* **Dependencies:**

  * stable task artifact contract
  * stable prompt library
  * reliable workflow metrics capture
* **Notes:**

  * token efficiency should be treated as a first-class workflow quality metric, not just a side effect
  * future work may include model-routing decisions based partly on token or cost budgets

---

### FR-012 — New Project Onboarding Flow

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * `workflow.init.md` is currently hardcoded for Forge — not reusable for other projects
  * `forge init` only scaffolds empty directories; no doc content is generated
  * anyone adopting Forge on a new project must manually write all canonical docs by hand
  * Sentinel will be bootstrapped through this flow as the first real-world validation
* **Scope:**

  * agent-driven `workflow.onboard.new.md` prompt — assumes the user has an agent CLI; the agent asks relevant follow-up questions (project name, purpose, constraints, tech stack, team size, deployment target, test strategy, etc.) and uses the answers to generate the full canonical doc set, working docs, manifest, and initial backlog
  * conversational flow: agent asks questions first, generates docs second — not a one-shot template fill
  * `forge init` remains the directory scaffolding step; the agent prompt handles all content generation
  * auto-generate initial `open_questions.md` from gaps the agent identifies during the conversation (unanswered questions, undecided constraints, unclear scope boundaries)
  * auto-generate starter `agent_profiles.md` and `docs_manifest.yaml` appropriate to the project type
* **Why not now:**

  * Forge's own doc contracts must stabilize before they can be generalized
* **Dependencies:**

  * stable Forge core (Phase 5 complete)
  * stable canonical doc structure
  * stable docs_manifest.yaml contract
* **Notes:**

  * primary surface is the agent prompt, not the CLI — assumes users have an agent CLI (e.g. Claude Code)
  * open questions generated at onboarding should be marked `decision_needed` by default
  * this is the required path for Sentinel bootstrap

---

### FR-013 — Existing Project Adoption (Repo Scan and Onboard)

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * most real projects already exist — Forge currently has no adoption path for them
  * target use cases include existing frontend codebases and other pre-built systems where Forge and Sentinel should be applied retroactively
  * without this, Forge is a greenfield-only tool
* **Scope:**

  * agent-driven `workflow.onboard.existing.md` prompt — assumes user has an agent CLI; agent scans the repo (architecture, structure, existing docs, tech stack, test suite, dependencies), asks targeted follow-up questions about unclear or missing context, then generates draft canonical docs
  * `forge onboard` CLI command — scaffolds the Forge directory structure into an existing repo without overwriting anything; agent prompt handles the content generation pass
  * auto-generates draft `product_scope.md`, `architecture.md`, and initial backlog from existing codebase signals
  * auto-generates `open_questions.md` entries for every gap, undocumented decision, or ambiguity found during the scan
  * auto-generates `change_proposals.md` stubs for any structural issues or canonical-level conflicts identified
  * all generated docs are marked `draft` — human review required before treating them as canonical
* **Why not now:**

  * requires stable canonical doc structure to know what to generate toward
  * scan quality depends on agent reasoning — needs stable prompt contracts first
* **Dependencies:**

  * FR-012 (New Project Onboarding Flow) — shares doc generation patterns and question flow
  * stable Forge core (Phase 5 complete)
  * FR-001 (Adapter System) — existing frontend or non-code projects may require adapter awareness during onboarding
* **Notes:**

  * scan must be additive — never overwrite files that already exist
  * the goal is a usable first draft in one pass, not a perfect canonical set
  * frontend codebases are a primary target use case alongside backend and full-stack projects

---

## 4. Promotion Rules

A roadmap item can move into active work when:

* it fits into an upcoming phase
* required dependencies are complete
* it no longer disrupts current execution
* it has a clear, scannable scope

When promoted:

* move it into `docs/working/backlog.md`
* assign it to a phase
* break it into task-sized units

---

## 5. Principles

* Do not let roadmap items disrupt current phases
* Do not prematurely break roadmap items into task packets
* Keep descriptions concise and decision-oriented
* Prefer deferring over forcing scope into the current phase
* Preserve Forge as a stable orchestration core
* Treat adapters and Sentinel as extensions, not core mutations
