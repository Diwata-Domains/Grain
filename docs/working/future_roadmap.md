# Future Roadmap

## 1. Purpose

Tracks deferred features, future capabilities, and post-v1 ideas that should not disrupt current execution.

Items here are intentionally **not part of the current phase or immediate backlog**.

They may become:

* future phases
* v2/v3 capabilities
* optional extensions

Grain is a **development orchestration system**.
Future work should expand its capabilities **without destabilizing the core build loop**.

---

## 2. Status Definitions

* `idea` — early concept, not yet evaluated
* `candidate` — worth building, but not scheduled
* `deferred` — explicitly postponed
* `planned` — intended for a future phase/version
* `promoted` — moved into active planning or implementation work elsewhere in working docs
* `graduated` — delivered or fully absorbed into active product/workflow state; no longer a future capability
* `revisit_later` — unclear value or timing

### Lifecycle Convention

Use roadmap statuses this way:

- keep `idea`, `candidate`, `planned`, `deferred`, and `revisit_later` for genuinely future-facing items
- use `promoted` when the item has moved into:
  - `docs/working/implementation_plan.md`
  - `docs/working/backlog.md`
  - `docs/working/current_focus.md`
- use `graduated` only when the roadmap item is effectively delivered and no longer belongs in future planning

Do not use the roadmap as a second active backlog.
If an item is actively being executed, the working docs own the operational state and the roadmap should only preserve the high-level trace.

---

## 3. Future Capabilities

### FR-001 — Adapter System Formalization

* **Status:** graduated — delivered through Phase 6 (closed)
* **Suggested Target:** v2
* **Why it matters:**

  * the Forge workflow (build loop, task packets, model routing, context assembly) is fully language and domain agnostic — adapters are the translation layer that makes it work across any project type
  * without adapters, Forge is implicitly a Python/backend tool; with adapters it works across every domain the user operates in
  * target project types include: Rust, Python, TypeScript/JavaScript, React, Tauri, Storybook, Markdown documentation systems, and Excel/spreadsheet workflows
  * content-management systems and markdown-first knowledge bases should fit the same docs-oriented adapter path
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
    * later content-management variants — editorial systems, docs sites, knowledge bases, publishing pipelines
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
  * promoted into active work through Phase 6 and follow-on v2 planning
  * **Delivered:** `code_adapter` and `frontend_adapter` profiles live in `docs/runtime/adapter_profiles.md`; `AdapterProfile` domain model in `src/forge/domain/adapters.py`; adapter-aware `forge init` with `--primary-adapter` and `--secondary-adapter` flags; full canonical contract formalized across `architecture.md §4.13`, `data_contracts.md §17`, `workflow_spec.md §13`, `cli_spec.md §6.7`; `docs_adapter` and `spreadsheet_adapter` remain planned-not-yet-implemented; extended by FR-014 (adapter capability surface)

---

### FR-002 — Spreadsheet Adapter (Excel Integration)

* **Status:** promoted — slotted as Phase 14 (v0.1.0 scope, alongside docs_adapter and PDF support)
* **Suggested Target:** v0.1.0
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

* **Status:** graduated — substantially delivered through Phase 8
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
  * **Delivered:** `forge task next`, `forge phase next`, `forge workflow next`, `forge workflow run`, `forge prompt show`, `forge task prepare` all delivered in Phase 8; `forge run <prompt>` concept was superseded by `forge workflow run` which is more precise and gate-aware; context assembly automation covered by `forge context build/show/export`

---

### FR-004b — Grain Distribution and Installation Paths

* **Status:** graduated — delivered through Phase 11 (closed 2026-04-11); Homebrew path (P11-T05) intentionally left outside the supported release story
* **Suggested Target:** v0.1.0
* **Why it matters:**

  * future users need a simple install path before Grain can be adopted broadly
  * local editable install is fine for current development, but not a sufficient distribution story for general use
* **Scope:**

  * PyPI publishing for `pip install grain`
  * `uv tool install grain` compatibility and documentation
  * optional Homebrew distribution only if a maintained tap/release pipeline is introduced later
  * clear versioned install and upgrade instructions
  * installation verification and troubleshooting docs
* **Dependencies:**

  * stable Phase 10 close (tree-sitter + knowledge graph — no further breaking CLI surface changes expected after this)
  * stable core CLI surface ✓
  * stable onboarding entrypoint ✓
  * stable packaging metadata and release process
* **Notes:**

  * start with PyPI first
  * keep installation simple and boring before adding platform-specific channels

---

### FR-004c — Workflow Automation Runner

* **Status:** graduated — delivered through Phase 12
* **Suggested Target:** v2
* **Why it matters:**

  * the Forge task loop should eventually be automatable without hiding state or bypassing review
  * users should be able to automate the legal next workflow step instead of manually launching every prompt
* **Scope:**

  * state-driven next-step runner
  * automatic choice between task planning, execute, review, close, and phase review/close based on repo state
  * stop conditions at task gates, review gates, and phase boundaries
  * explicit reporting when human input, review, or canonical decisions are required
  * optional prompt-launch integration for supported agent CLIs
* **Why not now:**

  * adapter and onboarding work should stabilize first
  * automation should wrap a proven workflow, not compensate for an unstable one
* **Dependencies:**

  * stable prompt entrypoints
  * stable task packet and working-doc contracts
  * stable phase planning and task planning surfaces
* **Notes:**

  * automate the next valid step, not hidden planning
  * keep all workflow state in files already used by Forge
  * phase boundaries should be valid stop points for the automation runner
  * should land before TUI/GUI work so later interfaces wrap stable command/state primitives
  * automation-relevant commands should expose machine-readable JSON for agent and operator use

---

### FR-005 — Sentinel (Verification Platform)

* **Status:** planned
* **Suggested Target:** v2
* **Why it matters:**

  * Sentinel is the companion verification system to Forge — where Forge asks "how do we build it?", Sentinel asks "does it work?"
  * introduces automated validation, bug detection, and reproducibility into the build loop
  * closes the loop between building and verification by feeding structured issues back into Forge as work inputs
  * Sentinel is a **paid product** — primary monetization vehicle for the Forge+Sentinel system
* **Scope:**

  * automated testing and validation orchestration
  * bug and issue ingestion pipeline
  * reproducible artifact generation
  * screenshot and artifact capture (logs, repro steps, visual state)
  * frontend capture flow for user-triggered bug reports with screenshots, relevant app state, and optional human comment
  * sandbox/container execution for isolated verification
  * structured issue output fed back into Forge as `candidate_task` proposal objects
  * structured verification artifact model covering screenshots, logs, traces, captured state, repro steps, and human annotations
  * human approval workflow for issue → work conversion
  * observability and workflow intelligence layer
* **Why not now:**

  * Forge must be stable enough to build Sentinel with it
  * onboarding flow (FR-012) must exist for Sentinel to be bootstrapped cleanly
* **Dependencies:**

  * stable Forge workflow (Phase 5 complete)
  * task packet system
  * adapter groundwork (FR-001)
  * FR-012 — New Project Onboarding Flow (Sentinel is a new project bootstrapped through this flow)
* **Notes:**

  * Sentinel feeds verified issues back into Forge as structured proposal objects — not raw bug reports
  * user feedback during product use should be captured as structured verification or feedback artifacts, not loose comments only
  * building Sentinel with Forge is the intended v1 real-world validation
  * Sentinel monetization is based on verification, reproducibility, and observability — not on limiting Forge core

---

### FR-005b — Forge Pro (Intelligence and Advanced Project Management Layer)

* **Status:** candidate
* **Suggested Target:** v3
* **Why it matters:**

  * Forge Core is open and generous by design — Pro capabilities should derive value from intelligence and coordination, not from limiting the core
  * advisory intelligence, multi-project visibility, and advanced project management are natural paid extensions
* **Scope:**

  * advisory intelligence layer — candidate task generation, roadmap suggestions, efficiency analysis, determinism/ambiguity insights
  * self-improvement proposal flow for workflow friction, prompt drift, repeated manual fixes, and automation opportunities discovered while using Forge
  * multi-project coordination and cross-project backlog visibility
  * advanced workflow metrics and observability dashboards
  * team-level workflow features
* **Why not now:**

  * Forge Core and Sentinel take priority
  * advisory intelligence requires stable telemetry layer first
* **Dependencies:**

  * stable Forge Core (Phase 5 complete)
  * FR-005 Sentinel (observability patterns established)
  * Telemetry/Observability Layer (FR-011)
* **Notes:**

  * Forge Core must remain fully functional without Pro
  * Pro should never gate basic execution, packet management, or core adapter functionality
  * Forge self-improvement should stay proposal-driven; verification evidence still belongs primarily to Sentinel

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

* **Status:** planned
* **Suggested Target:** v3
* **Why it matters:**

  * improves visibility of workflow state
  * broadens the eventual surface beyond terminal-native operators
  * remains useful even if CLI + prompts are sufficient for power users
* **Scope:**

  * phase view
  * backlog viewer
  * open questions panel
  * metrics dashboard
  * verification and review visibility on top of Forge + Sentinel state
* **Why not now:**

  * CLI + agent workflow is sufficient for v1
  * workflow runner and Sentinel bridge primitives should exist first
* **Dependencies:**

  * stable workflow + metrics
  * FR-004c (Workflow Automation Runner)
  * FR-005 / FR-006 verification surface maturity
* **Notes:**

  * must not replace file-based system
  * GUI is an expected future surface, but not a substitute for the command/state model

---

### FR-007b — Forge TUI

* **Status:** promoted — active v0.3.0 planning in Phase 21/22
* **Suggested Target:** v0.3.0
* **Why it matters:**

  * gives users a faster operator surface for navigating phases, backlog, packets, open questions, and proposals without leaving the terminal
  * makes Forge easier to use in daily practice while preserving the CLI-first and file-backed workflow model
* **Scope:**

  * current phase and next-task view
  * backlog list by phase and status
  * task packet inspection
  * open questions and change proposals panels
  * workflow metrics view
  * thin action launcher for common flows such as task execute, review, close, and phase review
* **Why not now:**

  * adapter and onboarding work should stabilize first
  * the workflow model is more important than the interface layer at the current stage
  * the workflow automation runner should exist first so the TUI shells stable primitives instead of inventing its own
* **Dependencies:**

  * stable Forge core
  * FR-004c (Workflow Automation Runner)
  * stable task and phase prompt surfaces
  * stable file-backed workflow contracts
* **Notes:**

  * the TUI should read and write the same files Forge already uses
  * it should not introduce hidden state or an alternate workflow model
  * first version should be a thin terminal operator shell, not embedded agent orchestration
  * promoted into active planning through `docs/working/backlog.md` Phase 21 and seeded Phase 22

---

### FR-016 — Writable Office Artifact Editing

* **Status:** promoted — active v0.3.0 planning in Phase 21/23
* **Suggested Target:** v0.3.0
* **Why it matters:**

  * Grain can already read spreadsheets and document artifacts, but practical operator value requires safe write/update support
  * non-code artifacts need reviewable edits just as much as code does
* **Scope:**

  * `.docx` read/update/export flow
  * spreadsheet read/update/export flow
  * review-safe change summaries or diffs
  * artifact-specific validators
  * write safety modes such as `propose`, `apply`, and `export-as-new-file`
* **Dependencies:**

  * stable docs and spreadsheet extraction
  * stable review and packet workflow
* **Notes:**

  * promoted into active planning through `docs/working/backlog.md` Phase 21 and seeded Phase 23

---

### FR-017 — Desktop Tooling and MCP Surface

* **Status:** promoted — active v0.3.0 planning in Phase 21/24
* **Suggested Target:** v0.3.0
* **Why it matters:**

  * Grain should be callable from the environments the operator actually uses, not only from a shell prompt
  * Claude/Desktop-style MCP paths and Codex CLI-native paths imply different integration surfaces
* **Scope:**

  * thin MCP wrapper for Claude/Desktop-style environments
  * CLI-first Codex guidance and helper flows
  * shared tool contract for desktop-driven Grain usage
* **Dependencies:**

  * stable CLI surfaces
  * stable review-safe artifact actions
* **Notes:**

  * promoted into active planning through `docs/working/backlog.md` Phase 21 and seeded Phase 24

---

### FR-018 — Obsidian Adapter and Vault Semantics

* **Status:** promoted — active v0.3.0 planning in Phase 21/24
* **Suggested Target:** v0.3.0
* **Why it matters:**

  * generic markdown handling is not the same as understanding an Obsidian vault
  * wiki-links, frontmatter, attachments, canvases, and `.obsidian/` config can affect both context selection and safe edits
* **Scope:**

  * decide between extending `docs_adapter` versus introducing `obsidian_adapter`
  * support vault-aware context loading and validations
  * support safe note and link maintenance workflows
* **Dependencies:**

  * stable markdown/docs flows
  * stable review-safe artifact update patterns
* **Notes:**

  * promoted into active planning through `docs/working/backlog.md` Phase 21 and seeded Phase 24

---

### FR-019 — Database Adapter

* **Status:** candidate
* **Suggested Target:** post-v0.3.0 unless pulled forward by repeated use
* **Why it matters:**

  * database work is a first-class part of full-stack development and has different review and validation needs than generic data files
  * schema changes, migrations, seed flows, query artifacts, and ORM boundaries should not be overloaded into `data_adapter`
* **Scope:**

  * schema and migration artifact awareness
  * query-file and ORM-surface context hints
  * database-specific review and validation guidance
  * optional future support for safe migration planning and diff summaries
* **Notes:**

  * keep this as a dedicated adapter family (`database_adapter` / `db_adapter`) rather than a `data_adapter` extension

---

### FR-020 — Scraping and Crawler Adapter

* **Status:** candidate
* **Suggested Target:** post-v0.3.0 unless pulled forward by repeated use
* **Why it matters:**

  * scraping and crawling workflows have their own operational constraints, selectors, extraction schemas, and output-review patterns
  * these workflows benefit from explicit boundaries around robots/rate-limit policy, crawl config, and extracted-output validation
* **Scope:**

  * crawl-config and selector awareness
  * extraction-schema and output-validation guidance
  * review focus around politeness constraints, retries, and data-shape stability
* **Notes:**

  * prefer a dedicated `crawler_adapter` or `scraping_adapter` rather than hiding this inside `data_adapter`

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
  * one of Forge's core product claims is that structured workflow should increase useful work completed before model usage limits or context ceilings are hit
  * future work may include model-routing decisions based partly on token or cost budgets
  * **tree-sitter pattern (2026-04-07):** structural extraction via tree-sitter (import/call graph parsing, local, zero LLM tokens) is the preferred direction for adapter context selection improvements across multiple adapters. Instead of loading all files matching broad glob patterns, parse the dependency graph of what the task actually touches and load only those files. Applicable adapters: `code_adapter` (Python, Rust, Go, Java), `frontend_adapter` (TypeScript, JavaScript, TSX, CSS), `docs_adapter` (Markdown link/cross-reference graphs), `devops_adapter` (Bash, Dockerfile, HCL, YAML). Not applicable to `spreadsheet_adapter` (formula dependencies require different tooling). Observed reference: Graphify project (MIT) demonstrates this pattern at scale with 19-language tree-sitter support. Implementation deferred until adapter context selection is the proven bottleneck.

---

### FR-012 — New Project Onboarding Flow

* **Status:** graduated — delivered through Phase 7 (closed)
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
  * promoted into active work through Phase 7 planning and backlog seeding
  * **Delivered:** `prompts/workflow.onboard.new.md` with conversational agent-driven flow; `forge init` extended with `--primary-adapter`, `--secondary-adapter`, `--bootstrap` flags; `workflow.init.md` kept as compatibility alias; adapter-aware starter packet creation; `docs/working/v2_onboarding.md` as the living onboarding design doc

---

### FR-013 — Existing Project Adoption (Repo Scan and Onboard)

* **Status:** promoted — slotted as Phase 13 (v0.1.0 scope, after Phase 12 close)
* **Suggested Target:** v0.1.0
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
  * `P7-T07` entry-criteria boundary recorded on 2026-04-07:
    * new-project onboarding slice must be complete and reviewed (`P7-T02` through `P7-T06`)
    * onboarding prompt/init surfaces must remain stable without unresolved drift
    * onboarding integration coverage must remain passing
    * first adoption packet must stay planning/scaffold-first (no deep scan tuning or provider-specific branching)
  * promotion trigger: move FR-013 from `planned` to `promoted` only when the above criteria are satisfied and a concrete starter packet is queued in backlog/current focus

---

### FR-014 — Orchestration Service and Adapter Capability Surface

* **Status:** candidate — seeded in backlog as Phase 9 (`backlog.md §12`)
* **Suggested Target:** v2 (post-Phase 8)
* **Why it matters:**

  * Forge currently sequences tasks within a single domain with no cross-domain coordination — as projects grow to span backend, frontend, DevOps, and docs work, the planning overhead becomes manual and error-prone
  * an orchestration service turns cross-domain planning into a structured, inspectable, proposal-driven activity rather than freeform operator reasoning
  * the adapter capability surface gives adapters a formal way to contribute scope, impact, and follow-up signals that the orchestrator can use — making adapters active participants in planning, not just passive hint containers
* **Scope:**

  * orchestration service in `src/forge/services/` — task-level (split decisions, adapter selection, dependency detection), phase-level (phase shaping, dependency chains, replan proposals), project-level (multi-surface coordination)
  * adapter capability surface — optional adapter methods: `detect_scope`, `collect_context`, `analyze_impact`, `validate_changes`, `export_artifacts`, `suggest_followups`; graceful degradation when absent
  * `OrchestratorPlan` domain model — packet candidates, dependency links, cross-domain flags, split recommendations; status lifecycle (draft → under_review → accepted/rejected/deferred)
  * `forge orchestrate scope` and `forge orchestrate plan` CLI commands
  * `forge adapter list` and `forge adapter show` CLI commands
  * `docs/working/proposals/` convention for OrchestratorPlan artifacts on disk
* **Why not now:**

  * Phase 8 (Workflow Automation Runner) must close first
  * the orchestration service depends on stable context assembly and workflow state primitives that Phase 8 is building
  * tree-sitter structural analysis (FR-011) is a natural input to `detect_scope` and `analyze_impact` — both should be scoped together if possible
* **Dependencies:**

  * stable Phase 8 workflow runner primitives
  * stable adapter profiles and context assembly service
  * FA-T01 tree-sitter work (FR-011) — feeds `detect_scope` and `analyze_impact`
* **Notes:**

  * all orchestration outputs are proposals — they pass through Review/Gate; task packets are never created automatically
  * canonical doc design is complete (architecture.md §4.14, workflow_spec.md §15, product_scope.md §2.1, data_contracts.md §18, cli_spec.md §6.8)
  * implementation should start with the domain model (`OrchestratorPlan`) and `forge orchestrate` CLI stubs, then add the service

---

### FR-015 — Code Intelligence and Graph Layer

* **Status:** candidate — seeded in backlog as Phases 10–12 (`backlog.md §13–15`)
* **Suggested Target:** v3
* **Why it matters:**

  * static glob-pattern context selection (current approach) loads too broadly — it includes files that are not structurally connected to the task
  * as projects grow, imprecise context selection becomes the primary source of token waste, unnecessary retries, and stale-context drift
  * a graph-based intelligence system answers questions static patterns cannot: what files does this function actually call, which docs reference this module, which tasks have touched this code area
* **Scope:**

  * **Layer 1 — Deterministic Structural** (tree-sitter + markdown/yaml parsers): extract functions, classes, imports, calls, file relationships, task packet metadata, doc structure into normalized structural entities; no LLM usage here
  * **Layer 2 — Semantic Enrichment** (embeddings, controlled LLM summaries): similar task detection, doc-to-task matching, duplicate/overlap detection; outputs labeled as inferred, not authoritative
  * **Layer 3 — Graph Layer** (NetworkX, JSON on disk): knowledge graph with typed, confidence-labeled edges (EXTRACTED: defines/imports/calls/depends_on; INFERRED: references/related_to; AMBIGUOUS: ambiguous_link); nodes include files, modules, classes, functions, packets, docs, adapters, proposals; graph is rebuildable from source, inspectable, versionable
  * **Layer 4 — Graph-Assisted Context Selection**: replace glob-pattern context loading with graph traversal — prefer packet-local files, then include only structurally connected files via graph distance; enforce minimal context rule and traceable selection
  * **Layer 7 — Ranking/Decision Layer**: deterministic scoring across graph distance, semantic similarity, authority level, packet-local priority, telemetry signals; used for context selection, next-task suggestions, and impacted-file identification
  * optional: language-native analyzers (Python ast/mypy/ruff, TypeScript ts-morph), LSP integration, git-aware hotspot analysis
* **Why not now:**

  * requires stable Phase 8 workflow primitives and FA-T01 tree-sitter proof-of-concept first
  * embeddings (Layer 2) introduce external or local model infrastructure decisions that need proper evaluation — this is not a simple local-only addition
  * should be phased: Layer 1 + Layer 3 (structural graph) first, Layer 2 (semantic enrichment) second, Layer 7 (ranking) third
* **Dependencies:**

  * FR-014 (Orchestration Service) — `detect_scope` and `analyze_impact` feed from the graph layer
  * FA-T01 (Tree-sitter, FR-011) — Layer 1 implementation
  * stable Phase 8 context assembly service
* **Constraints** (must not violate):

  * graph must not replace task packets
  * advisory outputs must not mutate state directly
  * all inferred relationships must be labeled with confidence and source
  * all artifacts must be file-backed and inspectable
  * context must remain minimal and bounded — the graph enables precision, not expansion

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
