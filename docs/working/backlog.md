# Backlog

## 1. Purpose

This document is the execution inventory for `Forge`.

It contains:
- concrete implementation tasks
- grouped by phase
- default task status
- short execution-oriented descriptions

Status values used here:
- `draft`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`

Default status for new backlog items in this file: `draft`

---

## 2. Phase 1 — Repository Foundation and Core CLI ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-1/`

---

## 3. Phase 2 — Documentation Registry and Validation ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-2/`

---

## 4. Phase 3 — Task Packet System ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-3/`

---

## 5. Phase 4 — Context Assembly and Model Routing ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-4/`

---

## 6. Phase 5 — Review, Handoff, and Hardening ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-5/`

---

## 8. Phase 6 — Adapter System Foundation (V2) ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-6/`

---

## 9. Phase 7 — New-Project Onboarding Flow ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-7/`

---

## 10. Phase 8 — Workflow Automation Runner Foundation ✓ CLOSED
11 tasks done

### P8 Planning Notes
- Scope: state-driven workflow guidance and automation primitives for agents and operators
- Depends on: stable new-project onboarding artifacts and prompt surfaces from Phase 7
- Planning doc: `docs/working/v2_plan.md`
- Keep the first slice CLI-first and machine-readable; do not start TUI/GUI work in this phase

### P8-T01 — Lock minimal workflow automation slice and stop-condition rules
- **Status:** done
- **Description:** Resolve the first runner slice boundaries: what counts as the next legal step, where the runner must stop, how review and verification gates are surfaced, and which commands must return machine-readable outputs for agents/operators.
- **Files:** `docs/working/v2_plan.md`, `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/open_questions.md`
- **Model:** frontier_model
- **Dependencies:** P7-T06
- **Ready:** yes

### P8-T02 — Implement workflow state evaluator service
- **Status:** done
- **Description:** Add a service/domain layer that inspects repo state and determines the next legal workflow action, blockers, and stop conditions without mutating state.
- **Files:** `src/forge/services/` (new workflow service), `src/forge/domain/` (runner/state types), `tests/` (new service tests)
- **Model:** frontier_model
- **Dependencies:** P8-T01
- **Ready:** yes

### P8-T03 — Add `forge workflow next`
- **Status:** done
- **Description:** Add a CLI command that reports the next legal workflow step, current blockers, and the minimal follow-up action in both text and JSON forms.
- **Files:** `src/forge/cli/` (new workflow group), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T04 — Add `forge task next`
- **Status:** done
- **Description:** Add a task-selection command that identifies the next actionable task packet candidate or reports that planning/splitting is required first.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/`, `docs/working/backlog.md` (if task selection rules need clarification), `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T05 — Add `forge phase next`
- **Status:** done
- **Description:** Add a phase-level command that reports whether phase planning, review, close, or no phase action is currently appropriate.
- **Files:** `src/forge/cli/` (workflow or phase surface), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T06 — Add `forge task prepare`
- **Status:** done
- **Description:** Add a command that ensures packet/context/prompt prerequisites are assembled for one task and reports missing inputs without making hidden decisions.
- **Files:** `src/forge/cli/task.py` or `src/forge/cli/context.py`, `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T07 — Add `forge prompt show`
- **Status:** done
- **Description:** Add a command that surfaces the recommended stable prompt entrypoint for the current state plus required inputs, without making prompts the source of truth.
- **Files:** `src/forge/cli/` (prompt or workflow surface), `src/forge/services/`, `prompts/README.md`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T01, P8-T02
- **Ready:** yes

### P8-T08 — Add `forge workflow run`
- **Status:** done
- **Description:** Add a guarded one-step runner that can execute one legal workflow action or stop with an explicit gate reason when human review, planning, or verification is required.
- **Files:** `src/forge/cli/` (workflow group), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T03, P8-T04, P8-T05, P8-T06, P8-T07
- **Ready:** yes

### P8-T09 — Harden machine-readable automation outputs and runner integration tests
- **Status:** done
- **Description:** Ensure automation-relevant commands emit stable JSON and add integration coverage across `workflow next`, `task next`, `phase next`, `task prepare`, and `workflow run`.
- **Files:** `src/forge/cli/output.py`, `tests/` (new runner integration coverage), `docs/working/current_focus.md`
- **Model:** open_model
- **Dependencies:** P8-T03 through P8-T08
- **Ready:** after P8-T08

### P8-T10 — Define Forge-side verification bridge contract for Sentinel handoff
- **Status:** done
- **Description:** Define the minimal Forge-side command contract so Sentinel can plug into the workflow runner when it exists. This is a contract-definition task, not implementation. Deliverable: (1) define `forge verify` command group in `cli_spec.md` as a deferred surface — commands for verification submission, status polling, and result ingestion; (2) define the minimal Sentinel result payload schema Forge expects to receive (structured issue type, artifact references, verification outcome); (3) define where verification results land in the workflow runner stop-condition logic (runner must stop and surface a verification gate when a result is pending); (4) record all of this in `v2_plan.md §11` as the Sentinel bridge contract. No Sentinel implementation required — this task produces the paper contract that FR-006 (Sentinel Integration Layer) will implement later.
- **Files:** `docs/canonical/cli_spec.md`, `docs/working/v2_plan.md`, `docs/working/open_questions.md`
- **Model:** frontier_model
- **Dependencies:** P8-T01
- **Ready:** yes — runner stop conditions defined in v2_plan.md §10; Forge/Sentinel distinction resolved in Q14; FR-005 scopes Sentinel's role; v2_plan.md §9 names the target command surface (`forge verify ...`)

### P8-T11 — Add working-doc reconciliation checks for state drift
- **Status:** done
- **Description:** Add a three-layer reconciliation approach for working-doc state so task/phase readiness, deferral notes, and current-focus guidance do not drift after task closeout or planning updates. The intended layers are: (1) manual close/review checklist expectations, (2) an explicit `forge workflow reconcile` command for detection and repair, and (3) runner-level validation that blocks or warns on inconsistent state before drift spreads.
- **Files:** `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/v2_plan.md`, `docs/working/open_questions.md`, `docs/working/workflow_metrics.md`
- **Model:** open_model
- **Dependencies:** P8-T01
- **Ready:** after P8-T01

---

## 12. Phase 9 — Orchestration Service Foundation ✓ CLOSED

> **Status:** CLOSED. All 7 tasks done. 561/561 tests passing. Phase closed 2026-04-11. FR-014.

### P9 Planning Notes
- Scope: implement the orchestration service (task and phase-level), adapter capability surface protocol, `OrchestratorPlan` domain model, and orchestrate/adapter CLI commands
- Depends on: stable Phase 8 workflow runner primitives and context assembly service
- Canonical design: complete — `architecture.md §4.14`, `workflow_spec.md §15`, `data_contracts.md §18`, `cli_spec.md §6.7–6.8`, `product_scope.md §2.1`
- Roadmap reference: FR-014

### P9-T01 — Define OrchestratorPlan domain model
- **Status:** done
- **Description:** Add `OrchestratorPlan` dataclass to `src/forge/domain/` with all required fields: `plan_id`, `scope_summary`, `active_adapters`, `packet_candidates`, `dependency_links`, `cross_domain_flags`, `split_recommendations`, `status`, `produced_by`. Add `PacketCandidate` and `CrossDomainDependency` supporting types.
- **Files:** `src/forge/domain/` (new orchestrator types), `tests/`
- **Model:** frontier_model
- **Dependencies:** none (pure domain model)
- **Ready:** after Phase 8 close

### P9-T02 — Implement adapter capability surface protocol
- **Status:** done
- **Description:** Define the optional adapter capability interface (`detect_scope`, `collect_context`, `analyze_impact`, `validate_changes`, `export_artifacts`, `suggest_followups`). Implement graceful degradation when capabilities are absent. Update `AdapterProfile` or add a companion protocol class in `src/forge/domain/adapters.py`.
- **Files:** `src/forge/domain/adapters.py`, `src/forge/adapters/adapter_config.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P9-T01
- **Ready:** after P9-T01

### P9-T03 — Implement orchestration service — task-level
- **Status:** done
- **Description:** Add `orchestration_service.py` to `src/grain/services/`. Implement task-level orchestration: adapter detection from scope description, split-vs-single recommendation, cross-domain dependency identification, `PacketSequencePlan` draft generation. All outputs produce `OrchestratorPlan` proposals, not task packets.
- **Files:** `src/grain/services/orchestration_service.py` (new), `src/grain/domain/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P9-T01, P9-T02
- **Ready:** yes

### P9-T04 — Implement orchestration service — phase-level
- **Status:** done
- **Description:** Extend the orchestration service with phase-level capabilities: phase shape proposals, dependency chain detection across packet candidates, replan candidate generation. Outputs are `OrchestratorPlan` proposals with `phase_shape_proposal` type.
- **Files:** `src/grain/services/orchestration_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P9-T03
- **Ready:** yes

### P9-T05 — Add `forge adapter list` and `forge adapter show`
- **Status:** done
- **Description:** Implement the `forge adapter` command group. `list` displays all known adapter profiles from `docs/runtime/adapter_profiles.md`. `show --id <adapter-id>` displays one profile's full contract fields. Support `--format text|json`.
- **Files:** `src/grain/cli/` (new adapter group), `tests/`
- **Model:** open_model
- **Dependencies:** P9-T02
- **Ready:** yes

### P9-T06 — Add `forge orchestrate scope` and `forge orchestrate plan`
- **Status:** done
- **Description:** Implement the `forge orchestrate` command group. `scope --scope <text>` queries relevant adapters and reports domain signals. `plan --scope <text>` produces a draft `OrchestratorPlan` and writes it to `docs/working/proposals/` as an inspectable artifact. Support `--format text|json`.
- **Files:** `src/grain/cli/` (new orchestrate group), `src/grain/services/orchestration_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P9-T03, P9-T04, P9-T05
- **Ready:** yes

### P9-T07 — OrchestratorPlan validator and integration tests
- **Status:** done
- **Description:** Add a validator for `OrchestratorPlan` artifacts: `plan_id` present, `status` is a valid value, candidate entries contain required fields, `active_adapters` resolve to known adapter IDs. Add integration coverage across `forge orchestrate scope`, `forge orchestrate plan`, and `forge adapter list/show`.
- **Files:** `src/forge/validators/`, `tests/`
- **Model:** open_model
- **Dependencies:** P9-T06
- **Ready:** yes

---

## 13. Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph ✓ CLOSED

> **Status:** CLOSED. All 6 tasks done (T01-T05 + T06 remediation). 575/575 tests passing. Phase closed 2026-04-11. FR-015 Layers 1 + 3 + 4. Absorbs FA-T01.

### P10 Planning Notes
- Scope: tree-sitter structural extraction (Layer 1), JSON knowledge graph on disk using NetworkX (Layer 3), and graph-assisted context selection to replace glob-pattern loading (Layer 4)
- Depends on: stable Phase 9 orchestration service (graph feeds `detect_scope` and `analyze_impact`); adapter context selection confirmed as the token bottleneck
- FA-T01 is absorbed into this phase — it is no longer a standalone future item once Phase 10 is active
- Roadmap reference: FR-015, FR-011

### P10-T01 — Tree-sitter structural entity extraction (Layer 1)
- **Status:** done
- **Description:** Add tree-sitter Python bindings. Implement structural entity extraction for applicable adapters: functions, classes, imports, call sites for code and frontend adapters; link and cross-reference graphs for docs adapter; dependency declarations for devops adapter. Output: normalized structural entity records. No LLM usage. Deterministic only.
- **Files:** `src/forge/services/` (new intelligence module), `tests/`
- **Model:** frontier_model
- **Dependencies:** stable Phase 9 adapter capability surface
- **Ready:** after Phase 9 close

### P10-T02 — Knowledge graph builder (Layer 3)
- **Status:** done
- **Description:** Implement graph builder using NetworkX. Nodes: files, modules, classes, functions, task packets, canonical docs, runtime docs, adapters. Edges typed with confidence labels (EXTRACTED, INFERRED, AMBIGUOUS). Persist as a JSON artifact on disk — inspectable, versionable, and always rebuildable from source artifacts.
- **Files:** `src/forge/services/graph_service.py` (new), `tests/`
- **Model:** frontier_model
- **Dependencies:** P10-T01
- **Ready:** yes

### P10-T03 — Graph-assisted context selection (Layer 4)
- **Status:** done
- **Description:** Replace glob-pattern context loading in `context_service.py` with graph traversal. Prefer packet-local files, then include only structurally connected files by graph distance. Enforce the minimal context rule and traceable selection — every inclusion must have a traceable graph path. No hidden inclusions.
- **Files:** `src/forge/services/context_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P10-T02
- **Ready:** yes

### P10-T04 — Wire graph into orchestration adapter capabilities
- **Status:** done
- **Description:** Connect graph layer outputs to `detect_scope` and `analyze_impact` adapter capabilities from Phase 9. Adapters use graph traversal results instead of static patterns when the graph is available. Fallback to static patterns when graph is absent.
- **Files:** `src/forge/adapters/`, `src/forge/services/orchestration_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P10-T03
- **Ready:** yes

### P10-T05 — Integration tests and graph rebuild validation
- **Status:** done
- **Description:** Add integration coverage across the full structural intelligence path: tree-sitter extraction → graph build → context selection → orchestration scope. Add graph rebuild validation ensuring the graph is always derivable from source artifacts with no hidden state.
- **Files:** `tests/`
- **Model:** open_model
- **Dependencies:** P10-T04
- **Ready:** yes

### P10-T06 — Replace ast/regex extraction with full tree-sitter parser coverage (REMEDIATION)
- **Status:** done
- **Description:** P10-T01 was accepted in review using Python `ast` and regex as substitutes for tree-sitter. This does not meet spec. Replace `structural_intelligence_service.py` with a full tree-sitter implementation covering all languages where tree-sitter grammars exist: Python, TypeScript, JavaScript, TSX, CSS/SCSS, Rust, Go, Java, Bash/Shell, Markdown, YAML, TOML, HCL. Use the `tree-sitter` Python bindings and install the required language grammar packages (`tree-sitter-python`, `tree-sitter-typescript`, `tree-sitter-javascript`, `tree-sitter-rust`, `tree-sitter-go`, `tree-sitter-java`, `tree-sitter-bash`, `tree-sitter-css`, etc.). The `parser` field on `StructuralExtraction` must report `"tree-sitter"` for all supported languages. Fallback to `"none"` only for languages with no available tree-sitter grammar — never fall back silently to regex. Update `pyproject.toml` with required grammar packages. Update all affected tests to assert `parser == "tree-sitter"` for supported languages.
- **Files:** `src/grain/services/structural_intelligence_service.py`, `pyproject.toml`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P10-T01 (replaces its implementation)
- **Ready:** now — Phase 10 is reopened for this task
- **Note:** P10-T02 through P10-T05 consumed extraction output from P10-T01 and remain valid in structure — graph nodes, context selection, and orchestration wiring do not change. Only the extraction layer underneath is being replaced.

---

## 14. Phase 11 — Distribution and Global Install ✓ CLOSED (T05 deferred)

> **Status:** closed — 4/5 tasks done; T05 (Homebrew) deferred by operator. 577/577 tests passing. Phase closed 2026-04-11. FR-004b.

### P11 Planning Notes
- Scope: PyPI publishing, `uv tool install` compatibility, Homebrew formula (macOS), versioned install/upgrade docs, install verification
- This is the public usability gate — after Phase 11, Grain can be installed globally by anyone with `pip install grain`, `uv tool install grain`, or `brew install grain`
- Depends on: stable Phase 10 tree-sitter and context selection (no further breaking changes expected to the core CLI surface)
- Roadmap reference: FR-004b

### P11-T01 — Finalize packaging metadata and build configuration
- **Status:** done
- **Description:** Audit and finalize `pyproject.toml` — classifiers, license, description, homepage, keywords, Python version constraints. Ensure `grain` entry point is cleanly defined. Verify `src/` layout builds a clean wheel with no dev artifacts or editable paths included.
- **Files:** `pyproject.toml`, `src/grain/`
- **Model:** open_model
- **Dependencies:** Phase 10 close
- **Ready:** after Phase 10 close

### P11-T02 — PyPI publish workflow
- **Status:** done
- **Description:** Set up a release workflow for publishing to PyPI. Define a version bump process, build and publish steps (`python -m build`, `twine upload`), and a CI-compatible publish path. Verify `pip install grain` installs the correct binary and package from PyPI.
- **Files:** `pyproject.toml`, build/publish tooling config
- **Model:** open_model
- **Dependencies:** P11-T01
- **Ready:** after P11-T01

### P11-T03 — `uv tool install` compatibility and documentation
- **Status:** done
- **Description:** Verify `uv tool install grain` works correctly and installs the `grain` CLI into the global tool path. Document the recommended install method. Test the installed binary resolves `grain --help` without a virtual environment.
- **Files:** install docs, `README.md`
- **Model:** open_model
- **Dependencies:** P11-T02
- **Ready:** after P11-T02

### P11-T04 — Install verification and troubleshooting docs
- **Status:** done
- **Description:** Write installation verification instructions (`grain --version`, `grain init --help`, expected output). Write a short troubleshooting guide covering PATH issues, Python version mismatches, and venv conflicts. Cover macOS, Linux, and Windows basics.
- **Files:** install/setup docs
- **Model:** open_model
- **Dependencies:** P11-T03
- **Ready:** after P11-T03

### P11-T05 — Homebrew formula (macOS)
- **Status:** blocked
- **Description:** Create a Homebrew formula for `grain` targeting macOS. Formula should install the `grain` CLI via `brew install grain`. Validate formula locally with `brew install --build-from-source`. Document alongside PyPI/uv as a first-class install path.
- **Files:** Homebrew formula (tap or contrib)
- **Model:** open_model
- **Dependencies:** P11-T02
- **Ready:** after P11-T02
- **Note:** Deferred by operator on 2026-04-11. Continue with `pip install grain` and `uv tool install grain` as supported install paths for now.

---

## 15. Phase 12 — Automated Workflow Loop ✓ CLOSED

> **Status:** CLOSED. All 4 tasks done. 595/595 tests passing. Phase closed 2026-04-10. Extends Phase 8 workflow runner primitives and Phase 9 orchestration service.

### P12 Planning Notes
- Scope: `grain workflow loop` command that drives the full execute→review→close cycle automatically using Phase 8 workflow runner primitives. Per-stage agent and model configuration. Configurable supervision level (supervised/gated/autonomous). Orchestrator/loop integration to feed approved OrchestratorPlans into task ordering. No Assay required — existing workflow gates provide safety. Assay (FR-005) will add independent verification on top later.
- Key design principle: the loop is unverified automation — it trusts the agents at each stage. The gates (`grain workflow run` stop points) are the safety layer, not an independent checker. Document this explicitly.
- Architectural boundary: the loop handles *how to execute* workflow stages; the orchestrator handles *what to build and how to structure it*. They are separate layers. The orchestrator feeds approved plans into the loop's task ordering (P12-T04); the loop uses `grain workflow next` as its state machine.
- Roadmap reference: new item — extends Phase 8 workflow runner primitives and Phase 9 orchestration service

### P12-T01 — Per-stage agent and model configuration
- **Status:** done
- **Description:** Define the workflow loop configuration surface. Agent config: two modes — (1) named shortcut (`claude`, `codex`) with optional `model` field, Grain resolves to known CLI invocation pattern; (2) raw `command` string, any shell command accepting a prompt path and returning an exit code. Supervision level config: `supervised` (proposes each action, waits for explicit human approval before executing), `gated` (runs automatically, stops at review/close gates — default), `autonomous` (minimal stops, only pauses on escalation conditions or explicit failures). Both persistent config (`docs/runtime/workflow_loop.yaml`) and CLI flag overrides supported. Token usage reporting: optional structured output contract — agent may emit `{"tokens_used": N, "model": "...", "stage": "...", "started_at": "ISO8601", "completed_at": "ISO8601"}`; loop captures if present, continues normally if absent. Loop driver always records `started_at`/`completed_at` regardless of agent token reporting.
- **Files:** `docs/runtime/workflow_loop.yaml` (new), `src/grain/domain/workflow_loop.py` (new), `src/grain/services/workflow_loop_config_service.py` (new), `tests/`
- **Model:** frontier_model
- **Dependencies:** Phase 11 close
- **Ready:** after Phase 11 close

### P12-T02 — `grain workflow loop` command
- **Status:** done
- **Description:** Implement `grain workflow loop` — reads current workflow state via `grain workflow next`, resolves the configured agent and prompt for the current stage, invokes the agent CLI, waits for completion, then repeats until a stop condition is reached. Stop conditions vary by supervision level: `supervised` stops before every invocation for approval; `gated` stops at review/close gates; `autonomous` stops only on escalation or failure. Supports `--steps N` limit and structured per-step progress output.
- **Files:** `src/grain/cli/workflow.py`, `src/grain/services/workflow_loop_service.py` (new), `tests/`
- **Model:** frontier_model
- **Dependencies:** P12-T01
- **Ready:** after P12-T01

### P12-T03 — Loop safety guardrails and documentation
- **Status:** done
- **Description:** Add explicit guardrails: max step limit to prevent runaway loops, clear per-step logging of agent invocation and result, `--dry-run` mode that prints what would be invoked without executing. Document supervision levels clearly — especially that `autonomous` is unverified automation and Assay (FR-005) is the future independent verification layer. Integration tests for stop-at-gate behavior across all three supervision levels.
- **Files:** `src/grain/cli/workflow.py`, `src/grain/services/workflow_loop_service.py`, loop docs
- **Model:** open_model
- **Dependencies:** P12-T02
- **Ready:** after P12-T02

### P12-T04 — Orchestrator/loop integration
- **Status:** done
- **Description:** Wire approved OrchestratorPlan artifacts into the loop's task ordering. When a plan exists in `docs/working/proposals/` with `accepted` status, the loop consults it for task sequence rather than raw backlog order. Adds `grain orchestrate accept --plan <id>` command to mark a plan as accepted. The loop falls back to backlog order when no accepted plan exists — no breaking change to existing loop behavior. This makes the orchestrator the strategic layer feeding the loop's execution layer without coupling them tightly.
- **Files:** `src/grain/cli/orchestrate.py`, `src/grain/services/orchestration_service.py`, `src/grain/services/workflow_loop_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P12-T03
- **Ready:** after P12-T03

---

## 16. Phase 13 — Existing Project Adoption ✓ CLOSED

> **Status:** CLOSED. All 5 tasks done. 638/638 tests passing. Phase closed 2026-04-12. FR-013. v0.1.0 scope.

### P13 Planning Notes
- Scope: agent-driven `workflow.onboard.existing.md` prompt, `grain onboard` CLI command, draft canonical doc generation from existing codebase scan, auto-generated open_questions and change_proposals stubs. All generated docs marked `draft` — human review required before treating as canonical.
- Key design principle: scan must be additive — never overwrite existing files. Goal is a usable first draft in one pass, not a perfect canonical set.
- Roadmap reference: FR-013
- Depends on: Phase 12 close, stable Phase 7 new-project onboarding surfaces

### P13-T01 — `grain onboard` CLI command + additive scaffold engine (TASK-0094)

- **Status:** done
- **Description:** Implement `grain onboard [path]` CLI command and `OnboardService.scaffold()`. The command creates the Grain directory structure additively into an existing repo — creates `docs/canonical/`, `docs/working/`, `docs/runtime/`, `tasks/`, `prompts/` directories and writes stub files marked `draft` where files don't already exist. Never overwrites existing files. Returns a manifest of what was created vs skipped.
- **Files:** `src/grain/cli/onboard.py`, `src/grain/services/onboard_service.py`, `src/grain/cli/__init__.py`
- **Model:** frontier_model
- **Dependencies:** none

### P13-T02 — Codebase scanner service (TASK-0095)

- **Status:** done
- **Description:** Implement `CodebaseScanner` that inspects an existing repo's directory tree and returns a `ScanResult` domain object. Detects: primary languages (from file extensions), applicable Grain adapters (code_adapter, frontend_adapter, docs_adapter, etc.), key existing files (README, package.json, pyproject.toml, Makefile, CI config), and existing documentation. Scanner output feeds T03 draft doc generation.
- **Files:** `src/grain/services/codebase_scanner.py`, `src/grain/domain/scan_result.py`
- **Model:** frontier_model
- **Dependencies:** P13-T01

### P13-T03 — Draft canonical doc generation from scan (TASK-0096)

- **Status:** done
- **Description:** Implement `OnboardDocGenerator` that takes a `ScanResult` and writes draft canonical docs: `docs/canonical/product_scope.md` (stub from detected project signals), `docs/canonical/architecture.md` (stub from detected adapters and structure), initial `docs/working/backlog.md` stub, and `open_questions.md` entries for every detected gap or undocumented decision. All generated docs include `# DRAFT` header — human review required. Additive only — skip any file that already exists.
- **Files:** `src/grain/services/onboard_doc_generator.py`
- **Model:** frontier_model
- **Dependencies:** P13-T02

### P13-T04 — `workflow.onboard.existing.md` prompt (TASK-0097)

- **Status:** done
- **Description:** Write the agent-driven `prompts/workflow.onboard.existing.md` prompt. The prompt walks an agent through the full existing project adoption flow: run `grain onboard`, review the scan manifest and generated stubs, ask targeted clarifying questions, fill in the draft docs with real content, and record remaining gaps as open_questions entries. Prompt must include mandatory CLI call steps.
- **Files:** `prompts/workflow.onboard.existing.md`
- **Model:** frontier_model
- **Dependencies:** P13-T03

### P13-T05 — Phase 13 integration tests (TASK-0098)

- **Status:** done
- **Description:** Write integration tests covering: `grain onboard` command on a synthetic existing repo (assert additive-only behavior, correct dir creation, skip existing), `CodebaseScanner` on known fixture trees (assert language/adapter detection), `OnboardDocGenerator` output shape and draft markers. Minimum: 15 new tests.
- **Files:** `tests/test_onboard_cmd.py`, `tests/test_codebase_scanner.py`, `tests/test_onboard_doc_generator.py`
- **Model:** frontier_model
- **Dependencies:** P13-T01, P13-T02, P13-T03

---

## 17. Phase 14 — Document and Spreadsheet Adapters ✓ CLOSED

> **Status:** CLOSED. All 4 tasks done. 662/662 tests passing. Phase closed 2026-04-12. v0.1.0 scope complete. FR-002 (spreadsheet), FR-001 docs_adapter.

### P14 Planning Notes
- Scope: implement `spreadsheet_adapter` (Excel .xlsx/.xls, CSV), `docs_adapter` (Word .docx, Markdown), and PDF document reading (.pdf). All three extract text content into the context assembly pipeline. Adds dependencies: `openpyxl` (Excel), `python-docx` (docx), `pdfplumber` (PDF).
- Key design principle: adapters extract readable text and structure from binary/formatted files — they do not modify those files. Output is text context fed into existing context assembly, same as code and markdown files.
- Adapter profiles for `spreadsheet_adapter` and `docs_adapter` must be fully defined in `docs/runtime/adapter_profiles.md`.
- PDF extraction is best-effort — layout-heavy PDFs may lose structure; text-first PDFs work cleanly.
- All three are equally important use cases for the operator.
- Depends on: stable Phase 13 close and existing context assembly service (Phase 4/10)

### P14-T01 — `spreadsheet_adapter` extraction service (TASK-0099)

- **Status:** done
- **Description:** Implement `SpreadsheetExtractor` service that reads `.xlsx`, `.xls`, and `.csv` files using `openpyxl` (Excel) and the stdlib `csv` module. Extracts sheet names, column headers, and row data as readable text. Define full `spreadsheet_adapter` profile in `adapter_profiles.md`. Wire file patterns (`.xlsx`, `.xls`, `.csv`) into context assembly so these files are selected when the adapter is active. Add `openpyxl>=3.1` to `pyproject.toml` dependencies. Tests: ≥ 8.
- **Files:** `src/grain/services/spreadsheet_extractor.py`, `docs/runtime/adapter_profiles.md`, `pyproject.toml`, `tests/test_spreadsheet_extractor.py`
- **Model:** frontier_model
- **Dependencies:** Phase 13 close

### P14-T02 — `docs_adapter` Word/docx extraction service (TASK-0100)

- **Status:** done
- **Description:** Implement `DocsExtractor` service that reads `.docx` files using `python-docx`. Extracts headings, paragraphs, and table content as readable text. Define full `docs_adapter` profile in `adapter_profiles.md` (`.docx` + `.md` file patterns). Add `python-docx>=1.1` to `pyproject.toml` dependencies. Wire into context assembly. Tests: ≥ 8.
- **Files:** `src/grain/services/docs_extractor.py`, `docs/runtime/adapter_profiles.md`, `pyproject.toml`, `tests/test_docs_extractor.py`
- **Model:** frontier_model
- **Dependencies:** P14-T01

### P14-T03 — PDF document reader (TASK-0101)

- **Status:** done
- **Description:** Implement `PdfExtractor` service that reads `.pdf` files using `pdfplumber`. Extracts text content page-by-page. Handles graceful degradation for layout-heavy PDFs (returns partial text with a warning, never raises on extraction failure). Add `pdfplumber>=0.11` to `pyproject.toml` dependencies. Wire `.pdf` patterns into context assembly under `docs_adapter`. Tests: ≥ 8 including graceful degradation behavior.
- **Files:** `src/grain/services/pdf_extractor.py`, `docs/runtime/adapter_profiles.md`, `pyproject.toml`, `tests/test_pdf_extractor.py`
- **Model:** frontier_model
- **Dependencies:** P14-T02

### P14-T04 — Phase 14 integration tests (TASK-0102)

- **Status:** done
- **Description:** Write cross-adapter integration tests covering: `grain context build` selects spreadsheet/docx/pdf files when adapter is active, extracted text feeds correctly into context bundle, mixed-file-type context bundles work end-to-end, graceful handling of corrupt or unreadable files. Tests must use synthetic fixture files (no real docs committed). Minimum: 12 new tests.
- **Files:** `tests/test_document_adapters_integration.py`, `tests/fixtures/` (synthetic .xlsx, .docx, .pdf fixtures)
- **Model:** frontier_model
- **Dependencies:** P14-T01, P14-T02, P14-T03

---

## 18. Phase 15 — Workflow Hardening and Automation (in progress) — archived

> **Status:** seeded — ready to begin on `dev` branch. v0.2.0 scope. Depends on Phase 14 close (complete).

### P15 Planning Notes
- Scope: close known workflow gaps from field use before building intelligence layers on top
- Promoted from: Assay TN #5 (phase close gate), Vault TN #6 (auto-packet), QD-01 (`workflow reconcile`)
- Depends on: stable Phase 14 close (complete)

### P15-T01 — `grain phase close` command
- **Status:** done
- **Description:** Implement a hard lifecycle gate that requires explicit `grain phase close` invocation before the workflow engine routes to the next phase. Currently a phase boundary is only a `stop_reason`; a determined operator can bypass it by manually editing `current_focus.md`. This task: (1) adds `grain phase close` CLI command that validates all phase tasks are done and no active task is open; (2) writes a phase-close marker to `current_focus.md`; (3) updates the workflow state evaluator to check for this marker before allowing next-phase routing; (4) blocks bypass via manual working-doc edits.
- **Files:** `src/grain/cli/phase.py` (new), `src/grain/services/workflow_service.py`, `src/grain/domain/workflow.py`
- **Model:** frontier_model
- **Dependencies:** none

### P15-T02 — `grain workflow run` auto-packet bootstrap
- **Status:** done
- **Description:** When `grain workflow run` or `grain workflow next` resolves `next_action: task_execute` but the candidate task has no packet directory, offer to create one inline rather than stopping dead with a tip. Behavior: if candidate task has no packet, prompt operator to confirm (or accept `--yes`); if confirmed, call task create with defaults (or `--simple` if task is flagged as lightweight). Closes Vault TN #6.
- **Files:** `src/grain/cli/workflow.py`, `src/grain/services/workflow_service.py`, `src/grain/services/task_service.py`
- **Model:** frontier_model
- **Dependencies:** P15-T01

### P15-T03 — `grain workflow reconcile`
- **Status:** done
- **Description:** Implement `grain workflow reconcile` to detect drift across working docs and optionally repair it. Checks: (1) `backlog.md` task statuses match any existing packet `Status:` fields; (2) `current_task.md` Task ID matches the active in-progress packet (if any); (3) `current_focus.md` phase progress counts match backlog done/open counts; (4) no open `needs_fix` tasks are invisible to the workflow engine. Output: list of inconsistencies with severity. `--fix` flag auto-repairs safe drift (status sync, current_task.md pointer). Promoted from QD-01.
- **Files:** `src/grain/cli/workflow.py`, `src/grain/services/workflow_service.py` (new `ReconcileService`)
- **Model:** frontier_model
- **Dependencies:** P15-T01

### P15-T04 — Phase 15 integration tests
- **Status:** done
- **Description:** Integration test coverage for Phase 15 deliverables: `grain phase close` happy path and bypass-prevention; `grain workflow run` auto-packet bootstrap (confirm + skip paths); `grain workflow reconcile` drift detection and `--fix` repair. Minimum 12 new tests.
- **Files:** `tests/test_phase_close_cmd.py` (new), `tests/test_workflow_reconcile_cmd.py` (new)
- **Model:** open_model
- **Dependencies:** P15-T01, P15-T02, P15-T03

### P15-T05 — `AGENTS.md` generation (`grain init` / `grain onboard`)
- **Status:** done
- **Description:** Emit a grain-managed `AGENTS.md` block at repo root during `grain init` and `grain onboard`. The block is delimited by `<!-- grain:workflow-instructions:start/end -->` markers so it can be updated in-place without clobbering user customizations below the markers. Content: run `grain workflow next --format json` before any code change; key commands (workflow next, workflow run, task close, workflow reconcile). Not Claude-specific — works with Codex CLI, Cursor, and any agent that reads `AGENTS.md`. Re-running `grain init --update-agents` regenerates only the grain block. Addresses the agent discipline gap where agents bypass the workflow in conversational sessions.
- **Files:** `src/grain/services/init_service.py`, `src/grain/cli/init.py`, `src/grain/services/onboard_service.py`
- **Model:** frontier_model
- **Dependencies:** P15-T04

### P15-T06 — `grain phase archive` command
- **Status:** done
- **Description:** Implement `grain phase archive <N>` to formally archive a closed phase's task packets. Validates: (1) phase N has a grain-verified closed marker in `current_focus.md`; (2) packets for phase N exist in `tasks/`; (3) target `tasks/archive/phase-N/` does not already exist. Moves all `P<N>-T*` directories from `tasks/` to `tasks/archive/phase-N/`. Updates the phase section header in `backlog.md` to append `— archived`. Text and JSON output. `--dry-run` mode. Makes archiving a first-class workflow step rather than manual housekeeping. Promoted from operator request during Phase 15.
- **Files:** `src/grain/cli/phase.py`, new `src/grain/services/phase_archive_service.py`
- **Model:** open_model
- **Dependencies:** P15-T01

---

## 19. Phase 16 — Semantic Enrichment Layer

> **Status:** ACTIVE. Depends on Phase 15 close. FR-015 Layer 2. v0.2.0 scope.

### P16 Planning Notes
- Scope: embeddings for semantic similarity, similar-task detection, doc-to-task matching, duplicate/overlap detection. All outputs labeled as inferred — not authoritative.
- Embedding provider decision: RESOLVED — `none` (BM25, default), `ollama`, `local` (sentence-transformers), `openai` (opt-in). Config field: `grain.embedding_provider` in `docs_manifest.yaml`.
- Depends on: stable Phase 15 close and Phase 10 knowledge graph (graph provides the structural backbone; embeddings add semantic enrichment on top)

### P16-T01 — Define embedding domain model, resolver, and config surface
- **Status:** done
- **Description:** Add the shared semantic-scoring domain model: `EmbeddingProvider`, `ScoredCandidate`, provider status/result types, and `EmbeddingProviderResolver`. Extend manifest config parsing to recognize `ollama` and provider-specific model settings while preserving graceful fallback to BM25.
- **Files:** `src/grain/domain/` (new embedding types), `src/grain/adapters/manifest.py`, `src/grain/services/` (new resolver module), `tests/`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes

### P16-T02 — Implement `BM25Provider`
- **Status:** done
- **Description:** Implement deterministic keyword-based scoring with no new dependencies. BM25 is the always-available fallback provider and the baseline for all semantic-layer comparisons.
- **Files:** `src/grain/services/` (new provider module), `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T01
- **Ready:** after P16-T01

### P16-T03 — Implement `OllamaProvider`
- **Status:** done
- **Description:** Add local-server embedding scoring using Ollama with graceful degradation when the server is unreachable or embeddings are unavailable.
- **Files:** `src/grain/services/` (new provider module), `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T01, P16-T02
- **Ready:** after P16-T02

### P16-T04 — Implement `LocalProvider`
- **Status:** done
- **Description:** Add sentence-transformers-based local embedding scoring with lazy model loading and graceful degradation when the optional dependency is absent.
- **Files:** `src/grain/services/` (new provider module), `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T01, P16-T02
- **Ready:** after P16-T02

### P16-T05 — Implement `OpenAIProvider`
- **Status:** done
- **Description:** Add OpenAI embedding scoring with optional runtime import, `GRAIN_OPENAI_API_KEY` support, and deterministic fallback behavior when configuration is incomplete.
- **Files:** `src/grain/services/` (new provider module), `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T01, P16-T02
- **Ready:** after P16-T02

### P16-T06 — Integrate semantic scoring into context selection
- **Status:** done
- **Description:** Wire the provider resolver into `context_service.py` so semantic scores rerank graph-derived candidates without inventing new context sources or breaking deterministic selection traces.
- **Files:** `src/grain/services/context_service.py`, `src/grain/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T02, P16-T03, P16-T04, P16-T05
- **Ready:** after providers are stable

### P16-T07 — Add `grain embedding show`
- **Status:** done
- **Description:** Surface the active provider, configured model, reachability/availability state, and fallback mode through a dedicated CLI command with text and JSON output.
- **Files:** `src/grain/cli/` (new embedding group or command), `src/grain/services/`, `tests/`
- **Model:** open_model
- **Dependencies:** P16-T01, P16-T03, P16-T04, P16-T05
- **Ready:** after resolver/provider status contracts are stable

### P16-T08 — Phase 16 integration tests
- **Status:** done
- **Description:** Add end-to-end coverage for provider resolution, graceful degradation, and context-selection scoring behavior across BM25, Ollama, Local, and OpenAI configurations.
- **Files:** `tests/`
- **Model:** open_model
- **Dependencies:** P16-T06, P16-T07
- **Ready:** after implementation tasks land

---

## 20. Phase 17 — Ranking and Decision Layer (seeded, not yet planned)

> **Status:** seeded — not yet started. Depends on Phase 16 close. FR-015 Layer 7. v0.2.0 scope.

### P17 Planning Notes
- Scope: deterministic scoring across graph distance, semantic similarity, authority level, packet-local priority, and telemetry signals. Applied to context selection, next-task suggestion, and impacted-file identification.
- Key principle: all scoring must be deterministic and inspectable — no opaque ranking decisions.
- Depends on: stable Phase 16 semantic layer and Phase 10 graph layer.
- Note: P17 is the layer that makes the Advisory/Intelligence Layer significantly more capable without breaking Grain's determinism model.

### P17-T01 — Add ranking domain model and score breakdown contracts
- **Status:** done
- **Description:** Define the inspectable ranking data model: weighted score components, deterministic breakdown structures, and result types used by the ranking layer.
- **Files:** `src/grain/domain/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P16-T01
- **Ready:** after Phase 16 close

### P17-T02 — Build deterministic ranking service
- **Status:** done
- **Description:** Implement the ranking service that combines graph distance, semantic similarity, authority level, and packet-local priority into a deterministic weighted score with exposed breakdowns.
- **Files:** `src/grain/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P17-T01, P16-T06
- **Ready:** after ranking contracts are stable

### P17-T03 — Integrate ranked scoring into context selection
- **Status:** done
- **Description:** Replace static adapter-priority ordering in context selection with the ranking service while preserving deterministic traces and exposing score components in bundle metadata.
- **Files:** `src/grain/services/context_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P17-T02
- **Ready:** after ranking service behavior is stable

### P17-T04 — Add ranked next-task advisory signals
- **Status:** done
- **Description:** Add a proposal-only advisory surface for ranked next-task suggestions so already-eligible candidate tasks can be scored and explained without changing authoritative `workflow next` / `task next` routing.
- **Files:** `src/grain/services/`, `src/grain/cli/`, `tests/`
- **Model:** open_model
- **Dependencies:** P17-T02
- **Ready:** after core ranking service exists
- **Note:** Q17 resolved — ranked task suggestions stay advisory-only and must live on a separate surface from authoritative workflow selection

### P17-T05 — Add ranked impacted-file advisory signals
- **Status:** done
- **Description:** Apply the ranking layer to impacted-file identification so graph and semantic signals produce inspectable, proposal-only file rankings.
- **Files:** `src/grain/services/`, `tests/`
- **Model:** open_model
- **Dependencies:** P17-T02
- **Ready:** after core ranking service exists

### P17-T06 — Phase 17 integration tests
- **Status:** done
- **Description:** Add end-to-end coverage for ranking stability, score-breakdown inspectability, and context/advisory behavior across the new ranking layer.
- **Files:** `tests/`
- **Model:** open_model
- **Dependencies:** P17-T03, P17-T04, P17-T05
- **Ready:** after implementation tasks land

---

## 21. Phase 18 — Data Adapter (seeded, not yet planned)

> **Status:** planned — ready to start. v0.2.0 scope. Promoted from v0.2.1.

### P18 Planning Notes
- Scope: a dedicated `data_adapter` for data science and ML workflows
- Notebook support (`.ipynb`) is already delivered in v0.1.2 via `code_adapter` — `data_adapter` extends the domain with richer data science context
- Candidate additions:
  - `.ipynb` migrated from `code_adapter` to `data_adapter` as primary home
  - data file patterns: `.parquet`, `.feather`, `.arrow`, `.h5`, `.hdf5`
  - schema/config files: `requirements.txt`, `environment.yml`, `Pipfile`
  - model artifact awareness: `.pkl`, `.joblib`, `.pt`, `.onnx` (metadata only — not content extraction)
  - data pipeline scripts and notebooks as first-class context sources
- Key decision gate: resolved in Q18 — Phase 18 data files and ML artifacts are metadata-only context sources
- Can begin after Phase 16 or in parallel with Phase 17

### P18-T01 — Define `data_adapter` contract and extraction boundaries
- **Status:** done
- **Description:** Define the Phase 18 adapter contract and supporting boundary docs: `data_adapter` profile shape, file-pattern ownership, notebook migration intent, and the metadata-only extraction policy for data/model artifacts. Update adapter runtime docs and any phase-planning notes needed to make the implementation slices inspectable.
- **Files:** `docs/runtime/adapter_profiles.md`, `docs/working/current_focus.md`, `docs/working/open_questions.md`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P17-T06
- **Ready:** yes — Q18 resolved

### P18-T02 — Implement metadata extractor for data and model artifacts
- **Status:** done
- **Description:** Add a deterministic extractor/service for Phase 18 file types that reports metadata for dataset and model artifacts (`.parquet`, `.feather`, `.arrow`, `.h5`, `.hdf5`, `.pkl`, `.joblib`, `.pt`, `.onnx`) without sampling contents. Include graceful degradation for missing optional libraries and lightweight schema hints only when they can be read cheaply.
- **Files:** `src/grain/services/`, `tests/`, `pyproject.toml`
- **Model:** frontier_model
- **Dependencies:** P18-T01
- **Ready:** after the `data_adapter` contract is written

### P18-T03 — Migrate notebook ownership into `data_adapter`
- **Status:** done
- **Description:** Move `.ipynb` primary ownership from `code_adapter` to `data_adapter`, preserving existing notebook extraction behavior while adding data-science-specific review/context hints. Keep the migration additive and backward-compatible for existing packet/context flows.
- **Files:** `docs/runtime/adapter_profiles.md`, `src/grain/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P18-T01
- **Ready:** after adapter contract is stable

### P18-T04 — Integrate `data_adapter` into context and scope selection
- **Status:** done
- **Description:** Wire the new adapter and extractor signals into context assembly and orchestration/scope analysis so data workflows select the right sources deterministically. Preserve the current explainability and proposal-only behavior in orchestration outputs.
- **Files:** `src/grain/services/context_service.py`, `src/grain/services/orchestration_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P18-T02, P18-T03
- **Ready:** after extractor and notebook migration land

### P18-T05 — Improve onboarding and scanner detection for data workflows
- **Status:** done
- **Description:** Expand codebase scanning and onboarding hints so repos with notebooks, dataset artifacts, and ML model files recommend `data_adapter` cleanly and stop defaulting those signals to `code_adapter` alone.
- **Files:** `src/grain/services/`, `tests/`, `docs/working/`
- **Model:** open_model
- **Dependencies:** P18-T03
- **Ready:** after `data_adapter` profile exists

### P18-T06 — Phase 18 integration tests
- **Status:** done
- **Description:** Add end-to-end Phase 18 coverage across adapter-profile loading, metadata-only extraction, notebook ownership migration, context selection, and orchestration/scope analysis for a representative data-science repo layout.
- **Files:** `tests/`
- **Model:** open_model
- **Dependencies:** P18-T02, P18-T03, P18-T04, P18-T05
- **Ready:** after implementation tasks land

---

## 22. Phase 19 — Community Adapter Registry (planned, not yet started)

> **Status:** planned — ready to start. Depends on adapter contract review. v0.2.0 scope. Promoted from v0.2.1.

### P19 Planning Notes
- Scope: discovery, distribution, and review pipeline for community-contributed adapter profiles
- Adapter contract is already stable — community adapters follow the same schema as official adapters
- Three tiers:
  - **Official** — maintained by Diwata Labs, fully validated (existing adapters)
  - **Community** — submitted via PR to one dedicated reviewed community registry repo, with automated schema validation + maintainer review before merge
  - **Local/private** — user-defined, stays in their own repo (already works today, no changes needed)
- Community adapters proven reliable over time may be promoted to Official
- Key decision gate: resolved in Q19 — Community adapters live in a dedicated reviewed registry repo, separate from the main Grain source repo
- Key open question: promotion criteria — what does a community adapter need to demonstrate before being promoted to Official?

### P19-T01 — Define community registry hosting and trust contract
- **Status:** done
- **Description:** Resolve the authoritative hosting/distribution model for community adapters and write the minimal trust contract: where community adapters live, how install sources are addressed, what “official/community/local” means operationally, and what promotion to Official requires at a high level. This is the decision-and-contract slice that unblocks the rest of Phase 19.
- **Files:** `docs/working/`, `docs/canonical/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P18-T06
- **Ready:** yes — Q19 is the task decision/output

### P19-T02 — Add adapter package validation service
- **Status:** done
- **Description:** Implement schema/compliance validation for installable adapter packages or registry entries, including file-shape checks, adapter-profile parsing, and deterministic error reporting before installation.
- **Files:** `src/grain/services/`, `src/grain/validators/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P19-T01
- **Ready:** after the hosting/trust contract is stable

### P19-T03 — Implement `grain adapter install`
- **Status:** done
- **Description:** Add the install command for community adapters from an approved source descriptor or registry handle. The command must remain explicit, inspectable, and bounded by the Phase 19 trust contract.
- **Files:** `src/grain/cli/`, `src/grain/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P19-T01, P19-T02
- **Ready:** after validation rules are stable

### P19-T04 — Scaffold registry/review artifacts
- **Status:** done
- **Description:** Add the repository-side scaffold and templates for community adapters: submission layout, adapter template, contribution guidance, and review metadata expected by the validation/install flow.
- **Files:** `contrib/`, `docs/`, `tests/`
- **Model:** open_model
- **Dependencies:** P19-T01
- **Ready:** after the hosting model is chosen

### P19-T05 — Add CI validation and author guidance
- **Status:** done
- **Description:** Add automated validation coverage for community adapter submissions plus author-facing documentation that explains packaging, validation expectations, and review/promotion boundaries.
- **Files:** `.github/`, `docs/`, `tests/`
- **Model:** open_model
- **Dependencies:** P19-T02, P19-T04
- **Ready:** after validation service and scaffold exist

### P19-T06 — Phase 19 integration tests
- **Status:** done
- **Description:** Add end-to-end coverage across install-source validation, adapter install behavior, registry/review artifacts, and CI-facing validation paths for the chosen Phase 19 hosting model.
- **Files:** `tests/`
- **Model:** open_model
- **Dependencies:** P19-T02, P19-T03, P19-T04, P19-T05
- **Ready:** after implementation tasks land

---

## 23. Phase 20 — Workflow Drift Remediation from Field Usage ✓ CLOSED

> **Status:** CLOSED. 6 tasks done (P20-T01 through P20-T06). Closed 2026-04-23 after workflow correctness, state handling, upgrade-safety, and packet-first prompt hardening landed. P20-T07 deferred as a lower-priority follow-up.

### P20 Planning Notes
- Scope: fix real workflow drift discovered while using Grain across Assay, DOMICILE, CRM, and other Grain-managed repos
- Primary target: make the authoritative workflow surfaces (`workflow next`, `workflow run`, task ID allocation, project terminal state, upgrade safety) match real operator expectations
- Excluded from this phase:
  - Assay ingestion or other Assay-specific feature work
  - TUI/GUI work
  - bugs already fixed in v0.1.10 through v0.1.11 or Phase 15
- Source signals consolidated from:
  - `Assay/docs/working/tooling_notes.md`
  - `Documents/DOMICILE/docs/working/tooling_notes.md`
  - `Documents/Limitless Vault/docs/working/tooling_notes.md`
  - `Limitless/CRM/docs/working/tooling_notes.md`

### P20-T01 — Route executed tasks to review instead of execute (TASK-0135)
- **Status:** done
- **Description:** Fix workflow evaluation so an active task with execution artifacts already recorded does not keep routing to `task_execute`. Once execution output exists, `grain workflow next` and `grain workflow run` should surface review as the next legal step unless the packet is already reviewed/closeable by contract.
- **Files:** `src/grain/services/`, `src/grain/domain/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes — reproduced in Limitless Vault tooling notes

### P20-T02 — Make task IDs globally monotonic across archived packets (TASK-0136)
- **Status:** done
- **Description:** Fix packet ID allocation so `TASK-XXXX` values remain globally monotonic even after packets are archived under `tasks/archive/`. `next_task_id()` must scan both active and archived packet directories and keep deterministic behavior for new packet creation.
- **Files:** `src/grain/domain/`, `src/grain/services/`, `tests/`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** after P20-T01 is complete to keep Phase 20 execution deterministic

### P20-T03 — Treat completed current task state as non-active workflow state (TASK-0137)
- **Status:** done
- **Description:** Harden workflow evaluation so `current_task.md` pointing at a `done` packet does not cause `workflow next` to keep routing against that completed task. Grain should recognize terminal task status, clear or ignore stale active-task state deterministically, and route to the correct next phase/task boundary.
- **Files:** `src/grain/services/`, `src/grain/domain/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P20-T01
- **Ready:** after review-routing semantics are stable

### P20-T04 — Add a recognized terminal project-complete workflow state (TASK-0138)
- **Status:** done
- **Description:** Add a valid terminal state for `docs/working/current_focus.md` so a completed project does not fail phase parsing. `grain workflow next` should stop cleanly with a deterministic no-op/project-complete signal instead of `required_docs_invalid` when the repo is intentionally complete.
- **Files:** `src/grain/services/`, `src/grain/domain/`, `docs/canonical/`, `docs/runtime/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** after P20-T01 and P20-T03 settle the workflow-state semantics

### P20-T05 — Make upgrade safer for customized repo doc layouts
- **Status:** done
- **Description:** Harden `grain upgrade` so repos with deliberate working-doc or canonical-doc customization do not get noisy or misleading diffs that appear to revert the project back to Grain defaults. Detect clearly customized managed files and surface bounded guidance rather than proposing destructive-looking rewrites.
- **Files:** `src/grain/services/`, `src/grain/data/`, `tests/`, `README.md`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** after the core workflow-state fixes land

### P20-T06 — Strengthen packet-first guidance in bundled prompts and agent instructions
- **Status:** done
- **Description:** Harden the bundled prompt and instruction surface so resumed AI sessions do not skip task packet creation and jump straight to implementation. Add explicit packet-first guardrails to the relevant prompt/instruction assets without introducing hidden workflow steps or Assay coupling.
- **Files:** `prompts/`, `src/grain/data/prompts/`, `docs/runtime/`, `tests/`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** after the workflow-state fixes land so prompts match the final behavior

### P20-T07 — Normalize tooling-notes schema expectations for Grain-managed repos
- **Status:** draft
- **Description:** Standardize the `tooling_notes.md` contract so Grain-managed repos use the same machine-readable columns (`Date`, `Type`, `Command`, `Observation`, `Severity`, `Status`) and migration guidance. This is a lower-priority follow-up that improves cross-repo triage and reduces ambiguity when mining tooling notes for backlog work.
- **Files:** `src/grain/data/runtime/`, `docs/canonical/`, `docs/runtime/`, `tests/`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** optional follow-up after the correctness fixes land

---

## 24. Phase 21 — v0.3.0 Planning and Operator Surface Definition (planned, ready to start)

> **Status:** planned — updated on 2026-04-27 after the official v0.2.0 release. This phase defines the first concrete v0.3.0 execution slice on `dev`, aligned with release-state planning already locked on `main`. Any v0.2.x fixes remain on `hotfix`.

### P21 Planning Notes
- Scope: lock the first v0.3.0 milestone around a real operator surface, writable office/document workflows, desktop-app compatibility, and explicit Obsidian support decisions
- Primary target: turn the broad `TUI next` direction into an execution-ready plan with bounded phases and task inventory
- Milestone theme: **Operator Surface for Structured Knowledge Work**
- Milestone summary: v0.3.0 makes Grain usable not just for code/task orchestration, but for day-to-day operator workflows across task packets, document artifacts, spreadsheets, and markdown vaults from the environments the operator actually uses.
- Branching intent:
  - `main` — release-state and approved planning truth
  - `dev` — v0.3.0 execution and planning refinement before coding starts
  - `hotfix` — any quick fixes to the released v0.2.0 line
- Core deliverables required for v0.3.0:
  - first usable Grain TUI for workflow navigation and common actions
  - writable `.docx` and spreadsheet flows
  - reviewable non-code artifact changes with validators and safety modes
  - explicit desktop invocation strategy, including a thin MCP path where required
  - explicit Obsidian support decision with at least one supported vault-aware path
  - first-class `database_adapter` planning and implementation slice
  - first-class `crawler_adapter` planning and implementation slice
- Stretch deliverables if core lands cleanly:
  - reusable workflow recipes for repeated office, vault, database, and crawler workflows
  - richer TUI inspection surfaces such as context bundle views and prompt previews
  - contract freshness warnings for prompt/runtime drift during long sessions
- Success criteria:
  - an operator can navigate active workflow state from the TUI without dropping to raw file inspection for common actions
  - an operator can safely update a `.docx` artifact and a spreadsheet artifact through Grain-managed flows
  - those updates produce reviewable outputs before closure
  - Grain has a credible desktop integration story for both Claude-style MCP environments and Codex-style CLI usage
  - Obsidian support is no longer ambiguous in planning or adapter boundaries
- Explicit non-goals for v0.3.0:
  - broad GUI beyond the first TUI slice
  - cloud sync, hosted state, or team collaboration backend
  - full Sentinel work
  - broad new adapter proliferation beyond the office/document and Obsidian surfaces
- Product assumptions for v0.3.0:
  - a TUI is required
  - writable `.docx` and spreadsheet flows are in scope
  - database workflows are in scope
  - crawler and scraping workflows are in scope through a dedicated `crawler_adapter`
  - desktop-app compatibility should be explicit, especially for Claude ecosystem MCP and OpenAI Codex workflows
  - likely integration split: CLI-first for Codex execution paths; MCP/server wrapper for Claude Desktop and ChatGPT app surfaces
  - Obsidian may justify a dedicated adapter if vault semantics exceed generic markdown/docs handling
  - non-code artifact writes must be reviewable through change summaries or diffs before close
  - safety modes should exist for office-style artifacts (`propose`, `apply`, `export-as-new-file` or equivalent)
  - reusable workflow recipes are in scope if they simplify repeated operator tasks without introducing hidden state
- Excluded from this phase until execution begins:
  - Assay feature work inside Grain
  - broad speculative GUI work beyond the first TUI/operator slice
  - remote SaaS infrastructure unless required by the chosen desktop integration path

### P21-T01 — Define the v0.3.0 milestone contract
- **Status:** done
- **Description:** Milestone contract defined on 2026-04-27. Theme: `Operator Surface for Structured Knowledge Work`. Core: TUI, writable office artifacts, reviewable non-code diffs/validators/safety modes, desktop integration path, and explicit Obsidian support shape. Stretch: reusable workflow recipes, richer TUI inspection, and contract-freshness warnings if the core lands cleanly.
- **Files:** `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/implementation_plan.md`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** complete

### P21-T02 — Define the first Grain TUI slice
- **Status:** done
- **Description:** First TUI slice defined on 2026-04-27 as a thin operator shell over the existing CLI/file-backed workflow. Required surfaces: workflow dashboard, current task/phase view, backlog-by-phase list, packet artifact inspector, prompt preview, and context-bundle inspector. Required actions: launch task execute/review/close flows, open packet artifacts, view blockers, and trigger safe non-code review actions when those land. Navigation model: one app shell with pane switching, detail panel, and command/status footer. Stack choice: Python + Textual, running in-process with existing Grain services and CLI/domain logic. The TUI must call stable Grain commands and read the same files the CLI already uses; it must not invent hidden state or alternate workflow transitions.
- **Files:** planning docs, future canonical proposal inputs if needed
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** complete

### P21-T03 — Define writable document and spreadsheet workflows
- **Status:** done
- **Description:** Writable office workflow defined on 2026-04-28. Grain should support direct local updates to `.docx` and spreadsheet artifacts, but only through explicit safety modes and review surfaces. Default mode is `propose`: generate a change plan plus human-readable diff/change summary without mutating the source file. `apply` writes in place only after operator approval or explicit command intent. `export-as-new-file` writes a sibling artifact for low-trust or comparison-first workflows. Every write-capable flow must attach to a task packet, record touched artifact paths in `results.md`, emit a reviewable summary before close, and run artifact-specific validators before reporting ready. `.docx` flows should review heading/section/table preservation and summarize textual/structural edits; spreadsheet flows should review touched sheets, ranges, formulas, and required-table invariants. The workflow is direct-write capable, not patch-file-only, but must always produce a text review surface before closure.
- **Files:** planning docs, adapter planning docs, potential canonical proposal inputs
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** complete

### P21-T04 — Define desktop-app integration strategy
- **Status:** done
- **Description:** Desktop integration strategy defined on 2026-04-28. Grain should keep the CLI as the canonical operator surface and command contract. Codex-style environments use Grain directly through CLI invocation. Claude/Desktop-style environments use a thin local MCP wrapper over the same Grain command surfaces, preferably stdio-first for local operation. ChatGPT/OpenAI app-style integrations, if pursued, should reuse the same shared tool contract through an MCP/app-server layer rather than introducing a separate bespoke command model. The integration priority is one core Grain tool contract with multiple adapters at the boundary: CLI-native where possible, MCP-wrapped where required. The desktop path must remain local-first, file-backed, and compatible with the monorepo contract layer so Grain can participate in broader toolkit workflows without becoming a hosted service.
- **Files:** planning docs, runtime guidance, future roadmap docs if needed
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** complete

### P21-T05 — Decide Obsidian support shape
- **Status:** done
- **Description:** Obsidian support shape defined on 2026-04-28. Grain should ship a dedicated `obsidian_adapter` rather than treating Obsidian as generic `docs_adapter` scope. The reason is that vault semantics materially exceed plain markdown: wiki-links, frontmatter-heavy workflows, `.obsidian/` config, canvases, attachments, and vault conventions such as daily notes all affect context selection, safe edits, and validation. Minimum v0.3.0 surface: vault-aware context loading, wiki-link/reference validation, frontmatter-sensitive review, and safe note-maintenance workflows. `docs_adapter` remains responsible for generic markdown/docx/pdf content; `obsidian_adapter` specializes markdown-vault workflows.
- **Files:** planning docs, adapter profiles, future design docs if needed
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** complete

### P21-T06 — Define reviewable diffs, validators, and safety modes for non-code artifacts
- **Status:** done
- **Description:** Non-code review and safety model defined on 2026-04-28. Every non-code write flow must produce a review bundle before close. Minimum review bundle: touched artifact paths, operation mode (`propose` / `apply` / `export-as-new-file`), structured change summary, validator results, and explicit residual-risk notes when validation is partial or best-effort. `.docx` review surfaces should include heading/section/table change summaries; spreadsheet review surfaces should include touched sheets/ranges/formulas and schema-sensitive changes; Obsidian review surfaces should include wiki-link/frontmatter/reference changes. Validators are required before an artifact can report ready: structure validators (headings/tables/sheets), reference validators (wiki-links, required sheet names, required headings), and policy validators (safe mode honored, expected files updated, comparison artifact created when required). Grain should automatically force `propose` or `export-as-new-file` instead of `apply` when the artifact is high-risk, validation is partial, or the operator has not given explicit in-place mutation intent. Binary changes are allowed only when accompanied by a human-readable review surface; opaque mutation without review artifacts is out of scope.
- **Files:** planning docs, adapter planning docs, review docs, future design docs if needed
- **Model:** frontier_model
- **Dependencies:** P21-T01, P21-T03, P21-T05
- **Ready:** complete

### P21-T07 — Define reusable workflow recipes
- **Status:** done
- **Description:** Recipe layer and adapter-scope expansion defined on 2026-04-28. Grain should ship a small recipe layer for repeated structured workflows, but recipes remain thin entrypoints over the existing packet/workflow model rather than a second orchestration system. Initial v0.3.0 recipe set: update PRD or planning doc from source inputs, revise meeting or research notes, update spreadsheet/report artifact, fix Obsidian vault links or metadata drift, plan a database schema or migration change, and review crawler extraction/config updates. At the same time, v0.3.0 scope is expanded to include first-class `database_adapter` and `crawler_adapter` work. `crawler_adapter` is the preferred name because it covers scraping as one subset of a broader crawl/extraction domain.
- **Files:** planning docs, runtime docs, future prompt or recipe docs if needed
- **Model:** open_model
- **Dependencies:** P21-T01
- **Ready:** complete

### P21-T08 — Normalize tooling-notes schema and migration guidance
- **Status:** draft
- **Description:** Carry forward the deferred Phase 20 schema cleanup so Grain-managed repos use one machine-readable `tooling_notes.md` contract and clear migration guidance across seeded runtime docs and docs-facing instructions.
- **Files:** `src/grain/data/runtime/`, `docs/runtime/`, `docs/canonical/`, `tests/`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** optional follow-up after the operator-surface plan is stable

### P21-T09 — Seed the first v0.3.0 execution phases and tasks
- **Status:** done
- **Description:** Execution phases seeded on 2026-04-28. v0.3.0 now breaks into Phase 22 (TUI foundation and workflow surfaces), Phase 23 (writable office artifacts), Phase 24 (desktop integrations and Obsidian support), Phase 25 (database adapter), Phase 26 (crawler adapter), and Phase 27 (recipe layer and operator ergonomics). This turns the expanded operator-surface scope into implementation-ready buckets instead of one broad milestone.
- **Files:** `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/implementation_plan.md`
- **Model:** frontier_model
- **Dependencies:** P21-T01 through P21-T07
- **Ready:** complete

---

## 25. Phase 22 — TUI Foundation and Workflow Surfaces (planned, ready to start)

> **Status:** planned — Phase 21 scope is now locked enough to begin TUI execution. This phase delivers the first usable operator shell over Grain’s existing CLI and file-backed workflow.

### P22 Planning Notes
- Scope: operator-first TUI for local Grain usage
- Initial surfaces:
  - workflow status dashboard
  - current task and phase view
  - backlog-by-phase list with ready/in-progress/review state visibility
  - task execute/review/close launch points
  - prompt and packet artifact inspection
  - context bundle inspection
  - review-safe action launches for non-code artifact updates
  - quick access to reusable workflow recipes
- Navigation model:
  - single terminal app shell
  - left or top navigation for major views
  - main detail pane for selected task/phase/artifact
  - command and status footer for available actions and workflow blockers
- TUI rules:
  - no hidden workflow state
  - no alternate lifecycle transitions
  - CLI remains the source of truth for execution
  - TUI actions should wrap existing Grain commands before introducing new stateful behavior
  - implementation stack is Python + Textual
  - prefer in-process reuse of Grain services over a separate JS/TS frontend runtime
- Explicitly deferred from the first slice:
  - embedded agent execution consoles
  - multi-project dashboarding
  - live collaboration or remote sessions
  - broad form-based canonical editing
  - separate web or Electron-style UI stack

### P22-T01 — Scaffold Textual app shell
- **Status:** done
- **Description:** Create the base Textual application shell and project structure for the Grain TUI. Include app bootstrap, screen/pane layout skeleton, keyboard/action wiring foundation, and a clear boundary for calling existing Grain services without duplicating workflow logic.
- **Files:** `src/grain/tui/` (new), CLI/TUI entry wiring, tests
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes

### P22-T02 — Workflow dashboard and status summary
- **Status:** done
- **Description:** Build the first dashboard view showing current phase, active task, next legal action, blockers, and key working-doc state in a compact operator-readable layout.
- **Files:** TUI views, state adapters, tests
- **Model:** frontier_model
- **Dependencies:** P22-T01
- **Ready:** after the app shell exists

### P22-T03 — Backlog, task, and packet inspector views
- **Status:** done
- **Description:** Add backlog-by-phase navigation plus focused inspectors for packet metadata and packet artifact files so the operator can move from phase overview to task detail without leaving the TUI.
- **Files:** TUI views, packet/backlog readers, tests
- **Model:** frontier_model
- **Dependencies:** P22-T01
- **Ready:** after the app shell exists

### P22-T04 — Action launcher wiring for execute/review/close flows
- **Status:** done
- **Description:** Wire safe TUI actions that launch or wrap existing Grain execute/review/close commands and show status or errors without creating alternate workflow transitions.
- **Files:** TUI action layer, command wrappers, tests
- **Model:** frontier_model
- **Dependencies:** P22-T02, P22-T03
- **Ready:** after the core views exist

### P22-T05 — Prompt preview, context inspection, and blocker detail
- **Status:** done
- **Description:** Add prompt-preview and context-bundle inspection views plus a detailed blocker/status footer so operators can see why a workflow state is blocked and what Grain expects next.
- **Files:** TUI views, context/prompt readers, tests
- **Model:** frontier_model
- **Dependencies:** P22-T02, P22-T03
- **Ready:** after the core views exist

### P22-T06 — TUI tests, smoke flow, and docs
- **Status:** done
- **Description:** Add focused TUI tests and a smoke execution path for the first operator shell, then document how the TUI fits with the CLI and what is intentionally deferred.
- **Files:** tests, docs, runtime guidance
- **Model:** open_model
- **Dependencies:** P22-T04, P22-T05
- **Ready:** after interactive surfaces are stable

---

## 26. Phase 23 — Writable Office Artifacts (closed)

> **Status:** closed — Phase 23 shipped the first packet-first writable office artifact workflow on 2026-05-05.

### P23 Planning Notes
- Scope: safe local updates to Office-style artifacts
- Initial surfaces:
  - docx read/update/export flow
  - spreadsheet read/update/export flow
  - review-safe diff or change-summary outputs
  - artifact-specific validators
  - explicit write safety modes such as `propose`, `apply`, and `export-as-new-file`
- Workflow rules:
  - every write operation belongs to an active task packet
  - `propose` is the default write posture
  - `apply` requires explicit operator intent
  - `export-as-new-file` remains available for cautious comparison-first workflows
  - every successful write path must emit a human-readable review surface before close
  - validators run before a packet can claim the artifact update is ready for review
- Artifact-specific review expectations:
  - `.docx`: heading/section preservation, table integrity, and structural change summary
  - spreadsheets: touched sheets/ranges, formula changes, and required-table/sheet validation

### P23-T01 — Shared office write contracts and safety modes
- **Status:** done
- **Description:** Define the shared domain model and service boundary for non-code artifact writes. Lock the operation modes (`propose`, `apply`, `export-as-new-file`), review-bundle contract, validator result shape, and artifact-operation metadata that both `.docx` and spreadsheet flows will reuse.
- **Files:** domain models, service contracts, tests
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes

### P23-T02 — `.docx` propose and export workflow
- **Status:** done
- **Description:** Implement the first `.docx` write path with safe `propose` and `export-as-new-file` support. Include document load/update/save behavior plus structural change-summary output suitable for review.
- **Files:** office/docx services, tests, fixtures
- **Model:** frontier_model
- **Dependencies:** P23-T01
- **Ready:** after shared contracts exist

### P23-T03 — Spreadsheet propose and export workflow
- **Status:** done
- **Description:** Implement the first spreadsheet write path with safe `propose` and `export-as-new-file` support. Include workbook load/update/save behavior, touched-sheet or touched-range reporting, and formula-aware summary output.
- **Files:** office/spreadsheet services, tests, fixtures
- **Model:** frontier_model
- **Dependencies:** P23-T01
- **Ready:** after shared contracts exist

### P23-T04 — Review bundle and validator pipeline for office artifacts
- **Status:** done
- **Description:** Wire the shared review bundle output and validator pipeline across `.docx` and spreadsheet operations. Enforce structure/reference/policy validation and require residual-risk notes when validation is partial.
- **Files:** review services, validator services, tests
- **Model:** frontier_model
- **Dependencies:** P23-T02, P23-T03
- **Ready:** after both artifact write paths exist

### P23-T05 — CLI entrypoints and workflow-safe mutation commands
- **Status:** done
- **Description:** Add Grain CLI entrypoints for office artifact mutations and review inspection. Commands must keep packet-first workflow discipline and surface operation mode, artifact outputs, and validation status without bypassing review.
- **Files:** CLI commands, service wiring, tests
- **Model:** frontier_model
- **Dependencies:** P23-T04
- **Ready:** after write and review services are stable

### P23-T06 — Office artifact tests, smoke flow, and docs
- **Status:** done
- **Description:** Add end-to-end tests, smoke flows, and documentation for the first office-artifact slice. Cover `.docx` and spreadsheet propose/export behavior, validator gating, and review-bundle expectations.
- **Files:** tests, docs, runtime guidance
- **Model:** open_model
- **Dependencies:** P23-T05
- **Ready:** after the CLI and review path are stable

---

## 27. Phase 24 — Desktop Integrations and Obsidian Support (seeded, not started)

> **Status:** seeded — implementation phase for external tool surfaces after the writable artifact plan is approved.

### P24 Planning Notes
- Scope: external invocation and markdown-vault specialization
- Initial surfaces:
  - thin MCP wrapper for Claude/Desktop-style environments
  - CLI-first Codex integration guidance and helpers
  - Obsidian vault semantics, whether via dedicated adapter or an extended docs profile
  - reusable recipes for desktop-driven office and vault workflows
- Desktop integration rules:
  - CLI remains the canonical Grain command surface
  - Codex-style usage should call Grain directly where command execution is available
  - Claude/Desktop-style usage should wrap the same actions through a local MCP server layer
  - ChatGPT/OpenAI app-style integrations should reuse the same shared tool contract rather than inventing a parallel API surface
  - local-first file-backed behavior is required; hosted desktop orchestration is deferred

### Future Adapter Notes
- Obsidian support is promoted into a dedicated `obsidian_adapter` for v0.3.0 rather than remaining inside `docs_adapter`.
- Database-related work is promoted into a dedicated `database_adapter` for v0.3.0 rather than being overloaded into `data_adapter`.
- Crawler and scraping work is promoted into a dedicated `crawler_adapter` for v0.3.0 with clear boundaries around crawl configs, selectors, extraction schemas, robots/rate-limit policies, and output validation.

### P24-T01 — Local MCP wrapper scaffold for desktop invocation
- **Status:** done
- **Description:** Add the first thin local MCP wrapper surface for Claude/Desktop-style environments while keeping Grain CLI commands canonical. Scope this to local tool exposure and shared action routing, not hosted orchestration.
- **Files:** MCP wrapper module(s), CLI/service wiring, tests, docs
- **Model:** frontier_model
- **Dependencies:** Phase 23
- **Ready:** yes

### P24-T02 — Codex and CLI integration guidance/helpers
- **Status:** done
- **Description:** Add explicit Codex-facing guidance and any small helper surfaces needed for CLI-first usage in desktop or tool-execution environments. Keep this thin and documentation-heavy unless a real helper command is justified.
- **Files:** docs, optional helper commands, tests
- **Model:** open_model
- **Dependencies:** P24-T01
- **Ready:** after the local MCP wrapper shape is stable

### P24-T03 — `obsidian_adapter` domain profile and vault contract scaffold
- **Status:** done
- **Description:** Create the first dedicated `obsidian_adapter` profile and vault-specific contract surface. Define supported artifact patterns, wiki-link/frontmatter expectations, and the initial adapter rationale.
- **Files:** adapter profiles, adapter/domain code, tests, docs
- **Model:** frontier_model
- **Dependencies:** Phase 23
- **Ready:** after Phase 24 starts

### P24-T04 — Obsidian vault context and wiki-link handling
- **Status:** done
- **Description:** Implement the first Obsidian-specific vault context behavior, including wiki-link-aware selection or export behavior and vault-safe note adjacency handling.
- **Files:** adapter/context services, tests, docs
- **Model:** frontier_model
- **Dependencies:** P24-T03
- **Ready:** after the adapter scaffold exists

### P24-T05 — Desktop and Obsidian smoke tests, docs, and closeout
- **Status:** done
- **Description:** Add smoke coverage and operator docs for the first desktop integration and Obsidian slices. Confirm the CLI-first boundary, local-first MCP wrapper behavior, and the dedicated Obsidian adapter surface.
- **Files:** tests, docs, runtime guidance
- **Model:** open_model
- **Dependencies:** P24-T01, P24-T04
- **Ready:** after the desktop wrapper and Obsidian context flows exist

---

## 28. Phase 25 — Database Adapter (seeded, not started)

> **Status:** seeded — implementation phase for full-stack database workflows after the operator-surface foundations are in place.

### P25 Planning Notes
- Scope: first-class `database_adapter` for recurring database work
- Initial surfaces:
  - schema and migration artifact awareness
  - query-file and ORM-surface context hints
  - database-specific review and validation guidance
  - migration/change-planning recipe hooks

### P25-T01 — `database_adapter` profile and contract scaffold
- **Status:** done
- **Description:** Create the first dedicated `database_adapter` profile and contract surface. Define supported artifact patterns, schema/migration/query expectations, and the initial adapter rationale so database work is no longer implied through generic code context alone.
- **Files:** adapter profiles, adapter/context code, tests, docs
- **Model:** frontier_model
- **Dependencies:** Phase 24
- **Ready:** after Phase 25 starts

### P25-T02 — Schema and migration context selection
- **Status:** done
- **Description:** Implement the first database-specific context behavior so `database_adapter` can prioritize schema files, migration directories, and adjacent data-model artifacts ahead of unrelated code.
- **Files:** context services, tests, docs
- **Model:** frontier_model
- **Dependencies:** P25-T01
- **Ready:** after the adapter scaffold exists

### P25-T03 — Query and ORM surface hints
- **Status:** done
- **Description:** Extend `database_adapter` context behavior to include query files, ORM models, and repository/data-access layers as secondary context when the task objective points at query or persistence work.
- **Files:** context services, tests, runtime guidance
- **Model:** frontier_model
- **Dependencies:** P25-T02
- **Ready:** after schema and migration selection is stable

### P25-T04 — Database review and validation guidance
- **Status:** done
- **Description:** Add database-specific review focus and validation guidance covering migration safety, destructive-change awareness, rollback expectations, and schema/query drift surfaces.
- **Files:** runtime docs, adapter guidance, tests
- **Model:** open_model
- **Dependencies:** P25-T01, P25-T03
- **Ready:** after the core database context surfaces exist

### P25-T05 — Database smoke tests, docs, and closeout
- **Status:** done
- **Description:** Add integrated smoke coverage and operator docs for the first database adapter slice. Confirm the packet-first database workflow, adapter context behavior, and review/validation boundaries before Phase 25 closes.
- **Files:** tests, docs, runtime guidance
- **Model:** open_model
- **Dependencies:** P25-T02, P25-T03, P25-T04
- **Ready:** after the database adapter slices above exist

---

## 29. Phase 26 — Crawler Adapter ✓ CLOSED

> **Status:** CLOSED. All 5 tasks done (P26-T01 through P26-T05). Phase closed 2026-05-06.

### P26 Planning Notes
- Scope: first-class `crawler_adapter` for crawl/extraction workflows
- Initial surfaces:
  - crawl-config and selector awareness
  - extraction-schema and output-validation guidance
  - robots/rate-limit/retry review focus
  - crawler-change review recipe hooks

### P26-T01 — `crawler_adapter` profile and contract scaffold
- **Status:** done
- **Description:** Create the first dedicated `crawler_adapter` profile and contract surface. Define supported crawl-config, selector, extraction-schema, and output artifact patterns so crawler work is no longer implied through generic code or docs context alone.
- **Files:** adapter profiles, adapter/context code, tests, docs
- **Model:** frontier_model
- **Dependencies:** Phase 25
- **Ready:** after Phase 26 starts

### P26-T02 — Crawl config and selector context selection
- **Status:** done
- **Description:** Implement the first crawler-specific context behavior so `crawler_adapter` can prioritize crawl configs, selector definitions, and extraction-schema artifacts ahead of unrelated code.
- **Files:** context services, tests, docs
- **Model:** frontier_model
- **Dependencies:** P26-T01
- **Ready:** after the adapter scaffold exists

### P26-T03 — Output-validation and extraction-surface hints
- **Status:** done
- **Description:** Extend `crawler_adapter` context behavior to include output schemas, normalization steps, and validation fixtures when the task objective is about extraction quality or downstream crawl outputs.
- **Files:** context services, tests, runtime guidance
- **Model:** frontier_model
- **Dependencies:** P26-T02
- **Ready:** after crawl-config and selector selection is stable

### P26-T04 — Crawler review and safety guidance
- **Status:** done
- **Description:** Add crawler-specific review focus and validation guidance covering robots constraints, rate limits, retry policy risk, selector brittleness, and extraction-schema drift.
- **Files:** runtime docs, adapter guidance, tests
- **Model:** open_model
- **Dependencies:** P26-T01, P26-T03
- **Ready:** after the core crawler context surfaces exist

### P26-T05 — Crawler smoke tests, docs, and closeout
- **Status:** done
- **Description:** Add integrated smoke coverage and operator docs for the first crawler adapter slice. Confirm the packet-first crawler workflow, adapter context behavior, and review/validation boundaries before Phase 26 closes.
- **Files:** tests, docs, runtime guidance
- **Model:** open_model
- **Dependencies:** P26-T02, P26-T03, P26-T04
- **Ready:** after the crawler adapter slices above exist

---

## 30. Phase 27 — Recipe Layer and Operator Ergonomics ✓ CLOSED

> **Status:** CLOSED. All 3 tasks done (P27-T01 through P27-T03). Phase closed 2026-05-06.

### P27 Planning Notes
- Scope: thin reusable recipes over the normal workflow and packet model
- Initial surfaces:
  - planning-doc update recipe
  - notes-revision recipe
  - spreadsheet/report update recipe
  - Obsidian maintenance recipe
  - database-change planning recipe
  - crawler-change review recipe
  - lightweight observability and token-budget surfaces for aggressive multi-agent usage
  - TUI inspection panels that explain execution state and context cost without adding hidden state

### P27-T01 — Task-level observability metadata and CLI surfaces
- **Status:** done
- **Description:** Add lightweight, file-backed observability metadata for task execution: executor identity, model class used, stage timestamps, and last workflow action. Surface the data through CLI-readable files or outputs without introducing background services or hidden state.
- **Files:** workflow/task services, CLI outputs, tests
- **Model:** frontier_model
- **Dependencies:** Phase 22 TUI foundation, existing workflow services
- **Ready:** after Phase 23 stabilizes

### P27-T02 — Token-efficiency and context-budget reporting
- **Status:** done
- **Description:** Add task-scoped context-cost surfaces: source counts, context-size proxies, ranked source-trimming hints, and optional token-budget warnings when runtimes expose usage or when Grain can estimate cost proxies.
- **Files:** context services, workflow/reporting outputs, tests
- **Model:** frontier_model
- **Dependencies:** P27-T01
- **Ready:** after observability metadata exists

### P27-T03 — TUI observability and context-cost panels
- **Status:** done
- **Description:** Extend the TUI with execution and debugging panels that show executor identity, model class, last action, recent packet-result changes, and context-budget summaries while staying a thin shell over existing services and files.
- **Files:** `src/grain/tui/`, tests, docs
- **Model:** frontier_model
- **Dependencies:** P27-T01, P27-T02
- **Ready:** after observability and token-budget data exists

---

## 31. Phase 28 — Assay Verification Integration

> **Status:** ready for close — all 5 Phase 28 tasks are complete and the workflow now lands on phase review/close.

### P28 Planning Notes
- Scope: verification bridge between Grain workflow and Assay packet outputs
- Primary outcomes:
  - first-class `grain verify` command group
  - task-scoped verification submission and status checks
  - payload ingestion into packet-local workflow artifacts
  - review/close gate behavior that respects pending or failed verification
  - no auto-close, no auto-packet creation, no canonical mutation side effects

### P28-T01 — Implement `grain verify submit` bridge command
- **Status:** done
- **Description:** Implement `grain verify submit` to create a verification request for a packet and return/store a `verification_id` in packet-local working artifacts. Command should validate task ID, required packet artifacts, and verifier configuration before submitting.
- **Files:** `src/grain/cli/`, verification service layer, packet artifact helpers, tests
- **Model:** frontier_model
- **Dependencies:** existing packet and review services
- **Ready:** now

### P28-T02 — Implement `grain verify status` for pending checks
- **Status:** done
- **Description:** Implement `grain verify status --verification-id` to check current verification state (`pending`, `complete`, `failed`) and surface concise operator-facing outcomes in text/json formats.
- **Files:** `src/grain/cli/`, verification service layer, tests
- **Model:** frontier_model
- **Dependencies:** P28-T01
- **Ready:** after submit flow exists

### P28-T03 — Implement `grain verify ingest` for Assay payloads
- **Status:** done
- **Description:** Implement `grain verify ingest --verification-id --payload <path>` to validate and ingest Assay result payloads (`verification_id`, `task_id`, `outcome`, `severity`, `summary`, `artifact_refs`, `followup_candidates`, `verified_at`) into packet-local review artifacts and workflow-facing state.
- **Files:** `src/grain/cli/`, verification payload validator, review artifact writers, tests
- **Model:** frontier_model
- **Dependencies:** P28-T01
- **Ready:** after verification artifact location is finalized

### P28-T04 — Wire verification gates into review and close flow
- **Status:** done
- **Description:** Update workflow/review/close paths so unresolved verification state blocks closure, completed verification is visible during review, and failed verification requires explicit operator decision before task completion.
- **Files:** workflow service, review service, task close checks, CLI outputs, tests
- **Model:** frontier_model
- **Dependencies:** P28-T02, P28-T03
- **Ready:** after ingest + status are stable

### P28-T05 — Operator docs and integration examples (Grain + Assay)
- **Status:** done
- **Description:** Add docs and prompt guidance for the full loop (`workflow next` -> execute -> `assay run --submit` -> `grain verify ingest` -> review -> close), including error handling and expected non-zero states.
- **Files:** `README.md`, `docs/canonical/cli_spec.md`, `docs/runtime/PROJECT_RULES.md`, prompts, tests where applicable
- **Model:** open_model
- **Dependencies:** P28-T01 through P28-T04
- **Ready:** after command behavior stabilizes

---

## 32. Phase 29 — Workflow Compliance Hardening

> **Status:** planned — reduce live-session redirection by making Grain and Assay workflow boundaries harder to bypass and easier to diagnose.

### P29 Planning Notes
- Scope: workflow compliance, agent redirection reduction, and packet/verification guardrail hardening
- Primary outcomes:
  - clearer runtime guidance when an agent drifts off the Grain/Assay loop
  - earlier detection of stale packet state and invalid workflow transitions
  - stronger prompt/runtime/test coverage for packet-first and verifier-first behavior
  - small operator diagnostics that explain why the workflow is blocked
  - no new background services, no hidden state, no autonomous side channels

### P29-T01 — Harden runtime and prompt guidance for Grain/Assay loop discipline
- **Status:** done
- **Description:** Tighten the shipped runtime docs and prompt assets so active-task, packet-first, and verification-loop rules are repeated in the places agents actually read during execution and close. Focus on reducing “forgot to use Grain/Assay” drift in long sessions.
- **Files:** `docs/runtime/AGENTS.md`, `docs/runtime/PROJECT_RULES.md`, `docs/runtime/CLAUDE.md`, prompt assets, release-surface tests
- **Model:** open_model
- **Dependencies:** P28 close
- **Ready:** now

### P29-T02 — Add workflow misuse blockers for common off-rails states
- **Status:** done
- **Description:** Detect and surface common drift states earlier: execution attempts with no active packet, close/review attempts while verification is still pending, and packet pointers that no longer match backlog state. Keep all checks read-only except where existing reconcile flows already own the fix path.
- **Files:** workflow service, review/task services, tests
- **Model:** frontier_model
- **Dependencies:** P29-T01
- **Ready:** after Phase 29 starts

### P29-T03 — Reduce runner packet/template drift on activation
- **Status:** done
- **Description:** Harden `workflow run` and task activation so runner-created packets are immediately usable without manual template replacement, and reduce the stale `current_task.md` / backlog drift that still appears after closeout.
- **Files:** workflow run service, packet bootstrap helpers, reconciliation logic, tests
- **Model:** frontier_model
- **Dependencies:** P29-T02
- **Ready:** after misuse blockers are stable

### P29-T04 — Add operator-facing workflow diagnostics
- **Status:** done
- **Description:** Add a lightweight diagnostic surface that explains why Grain is blocked and what file-backed action resolves it, without adding daemon state. This can be a `workflow doctor` or `workflow explain` style surface if that stays thin over existing services.
- **Files:** CLI surface, workflow/readiness services, tests, docs
- **Model:** frontier_model
- **Dependencies:** P29-T02
- **Ready:** after blocker signals are explicit enough

### P29-T05 — Hardening smoke tests and closeout docs
- **Status:** done
- **Description:** Add focused smoke/integration coverage for long-session workflow discipline and update operator docs with the hardened loop. This task closes the phase only after the common live-session redirection paths are covered by tests.
- **Files:** tests, `README.md`, runtime docs, workflow metrics/current focus
- **Model:** open_model
- **Dependencies:** P29-T01 through P29-T04
- **Ready:** after behavior stabilizes

---

## 33. Phase 30 — v0.4.0 Planning and Toolkit Boundary Definition

> **Status:** CLOSED 2026-06-11 — 14 tasks done (T01–T14, TASK-0190 through TASK-0203). 11 core deliverables. All spec docs written. Phase 31 (DX Hardening) is next.

### P30 Planning Notes
- Scope: milestone definition and execution seeding for `v0.4.0`
- Primary outcomes:
  - lock `grain suggest` as a core v0.4.0 deliverable — proactive task suggestion with human approval gate
  - promote recipes from planned direction into explicit executable scope
  - define Grain ↔ toolkit contract AND multi-repo workspace resolution model
  - decide where office/vault artifact flows can safely graduate from `propose/export` into `apply`
  - map DX friction from tooling_notes into an early execution phase — not stretch
  - fix `grain init` scaffold seeding gaps so it is immediately useful out of the box

### P30-T01 — Lock the `v0.4.0` milestone contract
- **Status:** done
- **TASK-ID:** TASK-0190
- **Description:** Formalize the v0.4.0 milestone contract. Locks `grain suggest` as core, maps tooling_notes DX items to execution phase order, resolves four open design questions (recipe unit, transport format, apply threshold, suggest signal quality bar).
- **Files:** `docs/working/v0.4.0_contract.md` (new), `docs/working/current_focus.md`
- **Model:** frontier_model
- **Dependencies:** Phase 29 close
- **Ready:** now

### P30-T02 — Define toolkit contract boundary and multi-repo workspace model
- **Status:** done
- **TASK-ID:** TASK-0191
- **Description:** Two specs: (1) inter-tool contract for how Assay/Conclave/DAEMON interoperate with Grain — transport format, version model, extension points; (2) workspace context model for monorepo resolution, `grain context link`, and `grain workspace list`.
- **Files:** `docs/canonical/toolkit_contract.md` (new), `docs/canonical/workspace_model.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T03 — Spec the `grain recipe` command group
- **Status:** done
- **TASK-ID:** TASK-0192
- **Description:** Full design spec for `grain recipe` — what recipes are, how `grain recipe run` works, recipe file format, relationship to workflow loop and toolkit contract.
- **Files:** `docs/canonical/recipe_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01, P30-T02
- **Ready:** after milestone contract and toolkit contract exist

### P30-T04 — Spec `apply` graduation criteria for office/Obsidian artifacts
- **Status:** done
- **TASK-ID:** TASK-0193
- **Description:** Define exact conditions for graduating artifact workflows from `propose`/`export` to safe in-place `apply`. Assess `.docx`, spreadsheets, and Obsidian notes. Decide which type(s) graduate in v0.4.0.
- **Files:** `docs/working/apply_graduation.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T05 — Spec source-tree / version-alignment diagnostics
- **Status:** done
- **TASK-ID:** TASK-0194
- **Description:** Design the diagnostic surface for dev/runtime alignment. Spec `grain doctor` or an extension to `grain --version` that detects when the installed binary lags the repo source.
- **Files:** `docs/working/dev_runtime_alignment.md` (new)
- **Model:** open_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T06 — Scaffold audit: fix seeding gaps, add standard doc types
- **Status:** done
- **TASK-ID:** TASK-0195
- **Description:** Fix `grain init` seeding gaps (canonical and working docs that are in the manifest but never created). Add: decisions.md, landscape.md, roadmap.md, CHANGELOG.md (Keep a Changelog), proposals/ directory. Add `--name` and `--type` flags to `grain init`. Fix tooling_notes `read_when: never`.
- **Files:** `src/grain/data/runtime/` templates, `init_service.py`, `src/grain/cli/init.py`, `docs_manifest.yaml`
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T07 — Spec the `grain suggest` command group
- **Status:** done
- **TASK-ID:** TASK-0196
- **Description:** Full design spec for `grain suggest`. Analyzes project state (open questions, tooling_notes, backlog, git log) and outputs ranked suggestions: `pick-up` (existing task to prioritize) or `new-task` (net-new work not in backlog). Approval gate: `grain suggest accept` creates packet or flips status; `grain suggest dismiss` excludes from future runs. `--format json` for agent consumption.
- **Files:** `docs/canonical/suggest_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01, P30-T02
- **Ready:** after milestone contract and toolkit contract exist

### P30-T08 — Spec agent enforcement model — packet-first discipline and session resume protocol
- **Status:** done
- **TASK-ID:** TASK-0197
- **Description:** Design agent-agnostic enforcement of packet-first discipline. Primary enforcement is through Grain's own state machine and hooks — not agent-specific config files. Covers: (1) `grain workflow next` refusing to route to `task_execute` without an open in_progress packet; (2) `grain workflow guard` command for point-in-time checks; (3) `grain hooks install` for pre-commit and post-checkout git hooks; (4) `prompts/workflow.resume.md` — agent-agnostic session resume protocol any agent follows; (5) PROJECT_RULES.md hard rule additions; (6) AGENTS.md block improvements. All primary enforcement works with zero AI involvement.
- **Files:** `docs/canonical/enforcement_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T09 — Spec upstream feedback loop — `grain report` and opt-in telemetry
- **Status:** done
- **TASK-ID:** TASK-0198
- **Description:** Design the path from a user's local tooling_notes.md to a Grain GitHub issue. Two surfaces: (1) `grain report` — scans tooling_notes for open Grain friction items, lets user select which to report, constructs a pre-filled GitHub issue URL, marks row as `reported`; (2) opt-in internal error telemetry — Grain queues its own exceptions locally and asks before sending on next invocation; (3) `grain notes` command group — `list`, `add`, `resolve` — so any agent can log friction via CLI without editing the file directly; (4) mandatory tooling notes rule added to the bundled PROJECT_RULES.md template. Nothing is sent without explicit user action. Default telemetry is off.
- **Files:** `docs/canonical/feedback_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T10 — Spec working document consistency auditing — `grain docs audit`
- **Status:** done
- **TASK-ID:** TASK-0199
- **Description:** Design `grain docs audit` — a broad working doc health check that goes beyond `grain workflow reconcile`. Checks: current_task.md stale pointer, backlog in_progress/packet mismatches, current_focus.md staleness, open_questions accumulation, tooling_notes high-severity triage, change_proposals aging, structural integrity of all registered docs. Read-only. <2s execution. Configurable thresholds. Output: text table + `--format json`. Integrates with `grain workflow guard --check-docs` and the post-checkout hook.
- **Files:** `docs/working/docs_audit_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T11 — Spec the archiving model — automatic, suggested, and explicit archive surfaces
- **Status:** done
- **TASK-ID:** TASK-0200
- **Description:** Design a coherent archiving model covering three surfaces: (1) automatic — working doc snapshots at phase close, proposal pruning when signals resolve; (2) suggested — `grain suggest` surfaces milestone-archive and workspace-idle-archive at natural boundaries; (3) explicit — `grain archive snapshot`, `grain archive milestone <version>`, `grain archive list/show`. Consistent with existing `grain phase archive` behavior.
- **Files:** `docs/working/archive_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T12 — Spec CLI output ergonomics improvements
- **Status:** done
- **TASK-ID:** TASK-0201
- **Description:** Design improvements to the Grain CLI output surface for both agent consumption and direct human use. Covers: (1) output contract hardening — every automation-relevant command must have a stable `--format json` surface; (2) text output visual quality — consistent use of symbols, alignment, color (where supported); (3) progress indicators that don't pollute machine-readable output; (4) stop reason vocabulary — standardized, documented set of stop reasons across all state machine commands; (5) `grain status` — a single command that shows the complete workspace state at a glance.
- **Files:** `docs/working/cli_ergonomics_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T13 — Spec TUI extension for v0.4.0 command surface
- **Status:** done
- **TASK-ID:** TASK-0202
- **Description:** Extend the v0.3.0 TUI (Python + Textual) to surface v0.4.0 commands for direct terminal users. New TUI panels/actions: `grain suggest` results + accept/dismiss flow, `grain docs audit` findings view, `grain archive` controls, `grain doctor` status panel, `grain recipe list` + run flow. Design must not require changes to the CLI contract — the TUI shells over existing commands. Includes a TUI extension spec that defines which views and actions are in scope for v0.4.0 vs. deferred.
- **Files:** `docs/working/tui_extension_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

### P30-T14 — Spec upgrade enforcement — forced upgrade gate
- **Status:** done
- **TASK-ID:** TASK-0203
- **Description:** Design forced upgrade enforcement when a workspace requires a newer Grain version than installed. `upgrade_policy` block in `docs_manifest.yaml` declares `min_version`, `enforce` (default false), and `enforce_after_days` grace period. Enforce mode blocks all commands except `grain upgrade`, `grain --version`, and `grain doctor`. Warn-only mode shows a startup banner to stderr. `grain upgrade` automatically ratchets `min_version` on success. Override escape hatch (`GRAIN_SKIP_VERSION_CHECK=1`) auto-logs to tooling_notes.
- **Files:** `docs/working/upgrade_enforcement_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** P30-T01
- **Ready:** after milestone contract exists

---

## 11. Future — Adapter Context Selection (absorbed into Phase 10)


> **Status:** draft — FA-T01 is preserved here for reference. Once Phase 10 is active, FA-T01 is absorbed into P10-T01 and this section becomes historical.

### FA-T01 — Tree-sitter dependency graph for adapter context selection

- **Status:** draft
- **Description:** Replace static glob-pattern context selection in adapters with a tree-sitter import/call graph pass. Parse the dependency graph of task-touched files locally (zero LLM tokens), then pass only structurally connected files into context assembly. Expected outcome: smaller context bundles, fewer tokens per execute stage, more precise file selection. Applicable to: `code_adapter` (Python, Rust, Go, Java), `frontend_adapter` (TypeScript, JavaScript, TSX, CSS), `docs_adapter` (Markdown link/reference graphs), `devops_adapter` (Bash, Dockerfile, HCL, YAML). Not applicable to `spreadsheet_adapter`.
- **Files:** `src/forge/adapters/adapter_config.py`, `src/forge/services/context_service.py`, `docs/runtime/adapter_profiles.md`
- **Model:** frontier_model
- **Dependencies:** stable Phase 8 context service, tree-sitter Python binding
- **Ready:** absorbed into Phase 10 — P10-T01 is the implementation task
- **Reference:** Graphify (MIT) — tree-sitter + parallel subagent pattern; FR-011 (Token Efficiency), FR-015

---

## 22. v0.1.x — Field-Reported Bugs (Assay + Obsidian, 2026-04-15) ✓ FIXED

Bugs discovered while using Grain in the Assay project and an Obsidian vault.
Fixed in v0.1.10 patch.

### GB-001 — `grain task prepare` did not detect stub packet files ✓ FIXED
- **Status:** done
- **Description:** `grain task prepare` reported `ok` with `missing_inputs: 0` even when
  `context.md`, `plan.md`, `deliverable_spec.md` were unedited template stubs containing
  `TASK-####` placeholders. Fixed by adding `_is_stub()` detection in `task_prepare_service.py`.
  Stubs are now surfaced as `stub packet file: <name> (contains unresolved placeholders)`.
- **Files:** `src/grain/services/task_prepare_service.py`, `tests/test_task_prepare_cmd.py`

### GB-002 — No lightweight packet mode for small tasks ✓ FIXED
- **Status:** done
- **Description:** `grain task create` always generated a full 7-file packet. For small mechanical
  tasks, `context.md`, `plan.md`, `deliverable_spec.md` add overhead without value. Fixed by
  adding `--simple` flag: generates `task.md` + `results.md` only, sets `Mode: simple` in task
  metadata. `grain task prepare` detects simple mode and skips planning file requirements.
- **Files:** `src/grain/cli/task.py`, `src/grain/services/task_service.py`,
  `src/grain/services/task_prepare_service.py`, `tests/`

### GB-003 — Execute prompt fragile when AI session is already in progress
- **Status:** partially addressed by GB-001
- **Description:** GB-001 fix means `grain task prepare` now flags stub planning files before
  execution, surfacing the problem at the prepare gate. Remaining friction (AI jumping to
  implementation without reading execute prompt) is a user choice — starting a fresh session
  is not required, just recommended for complex tasks.
- **Suggested improvement:** `grain task prepare` output could nudge the user toward the
  execute prompt when stubs are detected, e.g. "tip: for best results, use prompts/task.execute.md
  in a fresh conversation." Non-blocking suggestion only.

### OB-001 — `grain onboard` did not create `workflow_metrics.md` ✓ FIXED
- **Status:** done
- **Description:** `docs validate` failed after onboarding because `workflow_metrics.md` was
  listed in `docs_manifest.yaml` but not created by `onboard_service.py`. Fixed by adding it
  to `_STUB_FILES`.
- **Files:** `src/grain/services/onboard_service.py`, `tests/test_onboard_cmd.py`

### OB-002 — Scaffolded working docs were not machine-parseable ✓ FIXED
- **Status:** done
- **Description:** `current_task.md` stub had only `# DRAFT` prose, causing `workflow next`
  to hard-fail (missing `Task ID:`, `Task Path:`, `Status:` fields). `current_focus.md` stub
  had no phase line, causing phase parse failure. Fixed by updating stubs to parse-safe bootstrap
  defaults: `current_task.md` now has `Task ID: none / Task Path: none / Status: unset`;
  `current_focus.md` now has `Phase 0 — Bootstrap` marker.
- **Files:** `src/grain/services/onboard_service.py`

### OB-003 — `workflow next` hard-errored on bootstrap state ✓ FIXED
- **Status:** done
- **Description:** After `grain onboard`, `grain workflow next` returned `required_docs_invalid`
  instead of a structured bootstrap state. Fixed by detecting `Phase 0` in `workflow_service.py`
  and returning `stop_reason: bootstrap_incomplete` with `recommended_prompt: prompts/workflow.onboard.existing.md`.
- **Files:** `src/grain/services/workflow_service.py`, `tests/test_workflow_state_service.py`

### OB-004 — Onboarding prompt had stop-condition conflict ✓ FIXED
- **Status:** done
- **Description:** The prompt said "stop on any command failure" but `docs validate` and
  `workflow next` both produce expected non-zero results during bootstrap state, blocking the
  draft-fill phase. Fixed by adding an "expected bootstrap results" section to the prompt
  distinguishing bootstrap failures (continue) from real failures (stop).
- **Files:** `prompts/workflow.onboard.existing.md`

### OB-005 — Implicit scaffold-to-draft handoff boundary ✓ FIXED
- **Status:** done
- **Description:** It was unclear whether onboarding was "complete" after `grain onboard` or after
  the agent filled stubs. Fixed by adding an explicit "Onboarding Phases" section to the prompt
  clarifying that both CLI scaffold and agent draft are required.
- **Files:** `prompts/workflow.onboard.existing.md`

### OB-006 — Managed-file drift warnings during onboarding ✓ FIXED
- **Status:** done
- **Description:** `_maybe_warn_if_upgrade_needed` fired at CLI startup for every invocation
  including `grain onboard`, producing stale-file hints before the command had a chance to seed
  the files. Fixed by adding `"onboard"` to the skip list in `cli/__init__.py` (mirrors the
  existing `"upgrade"` skip). After `grain onboard` runs, files are at the current bundled
  version, so the next invocation's upgrade check will correctly report no drift.
- **Files:** `src/grain/cli/__init__.py`

### OB-007 — Template defaults too weak for stateful workflow system
- **Status:** done (subsumed by OB-002)
- **Description:** Addressed by OB-002 fix — `current_task.md` and `current_focus.md` now use
  parse-safe bootstrap defaults. All other working doc stubs remain human-readable prose stubs
  since they are not parsed by the workflow engine.

---

## 7. Backlog Maintenance Rules

1. backlog items must remain concrete and implementable
2. backlog items should map to one or more future task packets
3. large backlog items may later be split before execution
4. backlog items must not redefine canonical rules
5. items that require canonical change should link to a proposal, not silently change scope
