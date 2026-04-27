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

## 24. Phase 21 — v0.3.0 Planning and Release Confidence (planning not started)

> **Status:** planning not started — seeded at Phase 20 close on 2026-04-23. This phase will define the first v0.3.0 execution slice after a full v0.2.0 once-over.

### P21 Planning Notes
- Scope: perform a full release-surface once-over, identify any remaining v0.2.0 blockers, and lock the first concrete v0.3.0 roadmap slice
- Primary target: convert the current post-Phase-20 repo state into a publish-ready v0.2.0 release baseline plus an explicit Phase 21/22 direction
- Excluded from this phase until planned:
  - TUI/GUI implementation
  - Assay feature work inside Grain
  - broad speculative roadmap expansion without scoped backlog items

### P21-T01 — Finalize v0.2.0 versioning and release notes
- **Status:** ready
- **Description:** Update package/release metadata for the actual v0.2.0 release: bump `pyproject.toml`, add a clean `0.2.0` changelog entry, and align any repo-local release references that still advertise `0.1.11`.
- **Files:** `pyproject.toml`, `CHANGELOG.md`, `README.md`, release-facing docs as needed
- **Model:** open_model
- **Dependencies:** none
- **Ready:** yes — release blocker identified during Phase 21 once-over

### P21-T02 — Run full v0.2.0 release validation and smoke install pass
- **Status:** draft
- **Description:** Recreate the release-validation flow in a clean environment, run the full targeted pre-publish checks, and verify wheel/sdist install behavior plus key CLI smoke commands from built artifacts.
- **Files:** `README.md`, release notes, validation artifacts if recorded
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** after versioning and release notes are finalized

### P21-T03 — Refresh or defer the Homebrew release surface explicitly
- **Status:** draft
- **Description:** Decide whether the in-repo formula remains part of the public release story. If yes, update it to the actual v0.2.0 artifact filename and sha; if not, move or mark it more explicitly as deferred so it does not present stale release metadata.
- **Files:** `Formula/grain.rb`, `README.md`, related release docs
- **Model:** open_model
- **Dependencies:** P21-T01
- **Ready:** after the final release artifact exists

### P21-T04 — Remove runner post-create retry friction and reduce close-time reconcile drift
- **Status:** draft
- **Description:** Harden the workflow runner so newly created packets activate cleanly on the first `workflow run`, and reduce the routine need for `workflow reconcile --fix` after normal task closure when no true drift exists.
- **Files:** `src/grain/services/`, `src/grain/cli/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** after release-confidence tasks are no longer blocking publication

### P21-T05 — Normalize tooling-notes schema and migration guidance
- **Status:** draft
- **Description:** Carry forward the deferred Phase 20 schema cleanup so Grain-managed repos use one machine-readable `tooling_notes.md` contract and clear migration guidance across seeded runtime docs and docs-facing instructions.
- **Files:** `src/grain/data/runtime/`, `docs/runtime/`, `docs/canonical/`, `tests/`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** optional follow-up after immediate release-confidence work

### P21-T06 — Define the first concrete v0.3.0 roadmap slice
- **Status:** draft
- **Description:** Convert post-v0.2.0 planning into a bounded roadmap: decide the first v0.3.0 milestone theme, identify 1–2 follow-on phases, and seed execution-ready backlog tasks instead of broad roadmap prose.
- **Files:** `docs/working/current_focus.md`, `docs/working/backlog.md`, `docs/working/implementation_plan.md`, roadmap/planning docs if needed
- **Model:** frontier_model
- **Dependencies:** P21-T01
- **Ready:** after the release baseline and immediate blockers are clear

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
