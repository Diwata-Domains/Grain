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

## 14. Phase 11 — Distribution and Global Install

> **Status:** seeded — Phase 10 closed; planning-ready. FR-004b.

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
- **Status:** review
- **Description:** Set up a release workflow for publishing to PyPI. Define a version bump process, build and publish steps (`python -m build`, `twine upload`), and a CI-compatible publish path. Verify `pip install grain` installs the correct binary and package from PyPI.
- **Files:** `pyproject.toml`, build/publish tooling config
- **Model:** open_model
- **Dependencies:** P11-T01
- **Ready:** after P11-T01

### P11-T03 — `uv tool install` compatibility and documentation
- **Status:** ready
- **Description:** Verify `uv tool install grain` works correctly and installs the `grain` CLI into the global tool path. Document the recommended install method. Test the installed binary resolves `grain --help` without a virtual environment.
- **Files:** install docs, `README.md`
- **Model:** open_model
- **Dependencies:** P11-T02
- **Ready:** after P11-T02

### P11-T04 — Install verification and troubleshooting docs
- **Status:** draft
- **Description:** Write installation verification instructions (`grain --version`, `grain init --help`, expected output). Write a short troubleshooting guide covering PATH issues, Python version mismatches, and venv conflicts. Cover macOS, Linux, and Windows basics.
- **Files:** install/setup docs
- **Model:** open_model
- **Dependencies:** P11-T03
- **Ready:** after P11-T03

### P11-T05 — Homebrew formula (macOS)
- **Status:** draft
- **Description:** Create a Homebrew formula for `grain` targeting macOS. Formula should install the `grain` CLI via `brew install grain`. Validate formula locally with `brew install --build-from-source`. Document alongside PyPI/uv as a first-class install path.
- **Files:** Homebrew formula (tap or contrib)
- **Model:** open_model
- **Dependencies:** P11-T02
- **Ready:** after P11-T02

---

## 15. Phase 12 — Automated Workflow Loop

> **Status:** seeded — not yet started. Depends on Phase 11 close.

### P12 Planning Notes
- Scope: `grain workflow loop` command that drives the full execute→review→close cycle automatically using Phase 8 workflow runner primitives. Per-stage agent and model configuration. No Assay required — existing workflow gates provide safety. Assay (FR-005) will add independent verification on top later.
- Key design principle: the loop is unverified automation — it trusts the agents at each stage. The gates (`grain workflow run` stop points) are the safety layer, not an independent checker. Document this explicitly.
- Roadmap reference: new item — extends Phase 8 workflow runner primitives

### P12-T01 — Per-stage agent and model configuration
- **Status:** draft
- **Description:** Define a workflow loop config surface specifying which agent to use per stage (executor, reviewer, closer). Two config modes: (1) named agent shortcut (`claude`, `codex`) with optional `model` field — Grain expands these to their known CLI invocation patterns; (2) raw `command` string — any shell command that accepts a prompt and returns an exit code, enabling custom or third-party agents and scripts with no changes to Grain. Support both a persistent config file (`docs/runtime/workflow_loop.yaml`) and CLI flag overrides. The loop driver treats all agents identically — it invokes the resolved command, passes the prompt path, and waits for exit. Named shortcuts are convenience only; the raw command is the primitive. Token usage reporting: define an optional structured output contract — if an agent emits a JSON block `{"tokens_used": N, "model": "...", "stage": "...", "started_at": "ISO8601", "completed_at": "ISO8601"}` at the end of its run, the loop captures and records it. `started_at` and `completed_at` are always recorded by the loop driver itself (not the agent) so timing data is always available regardless of whether the agent reports tokens. Token fields remain opt-in — if absent, the loop continues normally with no token data for that stage. Named shortcut wrappers (`claude`, `codex`) are responsible for extracting token data from their native output format where possible and emitting the contract shape — if native output doesn't expose token data cleanly, the wrapper emits nothing. Timestamps enable time-of-day correlation analysis against token counts and duration over time.
- **Files:** `docs/runtime/workflow_loop.yaml` (new), `src/grain/cli/workflow.py`, `src/grain/services/workflow_run_service.py`, `tests/`
- **Model:** open_model
- **Dependencies:** Phase 11 close
- **Ready:** after Phase 11 close

### P12-T02 — `grain workflow loop` command
- **Status:** draft
- **Description:** Implement `grain workflow loop` — reads current workflow state via `grain workflow next`, invokes the configured agent CLI with the appropriate stage prompt, waits for completion, then repeats until a stop condition is reached (phase close, review gate requiring human input, or explicit `--steps N` limit). Emits structured progress output per step. Stops cleanly at any gate that requires human decision.
- **Files:** `src/grain/cli/workflow.py`, `src/grain/services/workflow_run_service.py`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P12-T01
- **Ready:** after P12-T01

### P12-T03 — Loop safety guardrails and documentation
- **Status:** draft
- **Description:** Add explicit guardrails: max step limit to prevent runaway loops, clear logging of each agent invocation and result, a `--dry-run` mode that prints what would be invoked without executing. Document that the loop is unverified automation and that Assay (FR-005) is the future independent verification layer. Add integration tests for the stop-at-gate behavior.
- **Files:** `src/grain/cli/workflow.py`, loop docs
- **Model:** open_model
- **Dependencies:** P12-T02
- **Ready:** after P12-T02

---

## 16. Phase 13 — Semantic Enrichment Layer (seeded, not yet planned)

> **Status:** seeded — not yet started. Depends on Phase 12 close and an embedding infrastructure decision. FR-015 Layer 2.

### P13 Planning Notes
- Scope: embeddings for semantic similarity, similar-task detection, doc-to-task matching, duplicate/overlap detection. All outputs labeled as inferred — not authoritative.
- Key decision gate: embedding provider choice (local model, external API, or hybrid) must be resolved as a canonical change proposal before P13 tasks are written. Do not seed task stubs until this decision is made.
- Depends on: stable Phase 12 close and Phase 10 knowledge graph (graph provides the structural backbone; embeddings add semantic enrichment on top)

---

## 17. Phase 14 — Ranking and Decision Layer (seeded, not yet planned)

> **Status:** seeded — not yet started. Depends on Phase 13 close. FR-015 Layer 7.

### P14 Planning Notes
- Scope: deterministic scoring across graph distance, semantic similarity, authority level, packet-local priority, and telemetry signals. Applied to context selection, next-task suggestion, and impacted-file identification.
- Key principle: all scoring must be deterministic and inspectable — no opaque ranking decisions.
- Depends on: stable Phase 13 semantic layer and Phase 10 graph layer.
- Note: P14 is the layer that makes the Advisory/Intelligence Layer significantly more capable without breaking Grain's determinism model.

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

## 7. Backlog Maintenance Rules

1. backlog items must remain concrete and implementable
2. backlog items should map to one or more future task packets
3. large backlog items may later be split before execution
4. backlog items must not redefine canonical rules
5. items that require canonical change should link to a proposal, not silently change scope
