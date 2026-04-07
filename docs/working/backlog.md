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
7 tasks done

### P6-T01 — Resolve adapter contract open questions and create adapter_profiles.md
- **Status:** done
- **Description:** Resolve open planning questions from v2_adapters.md §9 (minimal schema, multi-adapter context selection, no-adapter fallback, shared profile file structure). Create `docs/runtime/adapter_profiles.md` with the contract and initial `code_adapter` and `frontend_adapter` profiles.
- **Files:** `docs/runtime/adapter_profiles.md`, `docs/runtime/docs_manifest.yaml` (register new runtime doc), `docs/working/v2_adapters.md` (mark questions resolved)
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes

### P6-T02 — Implement adapter domain model
- **Status:** done
- **Description:** Create `AdapterProfile` dataclass with required fields (`adapter_id`, `domain_type`, `applies_to`) and optional hint sections (`relevant_file_patterns`, `ignore_file_patterns`, `build_or_run_hints`, `test_or_validation_hints`, `review_focus_hints`, `context_priority_rules`, `default_model_bias`). Follow the same domain pattern as `ModelProfile`.
- **Files:** `src/forge/domain/adapters.py` (new)
- **Model:** open_model
- **Dependencies:** P6-T01
- **Ready:** after P6-T01

### P6-T03 — Implement adapter profile loader
- **Status:** done
- **Description:** Parse `docs/runtime/adapter_profiles.md` into structured `AdapterProfile` domain objects. Follow the same loading pattern as the model profile loader (`src/forge/adapters/model_config.py`).
- **Files:** `src/forge/adapters/adapter_config.py` (new)
- **Model:** open_model
- **Dependencies:** P6-T02
- **Ready:** after P6-T02

### P6-T04 — Add adapter metadata fields to task packet templates and parser
- **Status:** done
- **Description:** Add optional `primary_adapter` and `secondary_adapters` fields to `templates/tasks/task.md`. Update the packet metadata parser to read these fields from `task.md`. Fields are optional — absence must degrade safely (adapter-neutral behavior).
- **Files:** `templates/tasks/task.md`, `src/forge/domain/packets.py`, `src/forge/validators/packet_validator.py`
- **Model:** frontier_model
- **Dependencies:** P6-T02, P6-T03
- **Ready:** after P6-T03
- **Note:** if packet schema change requires canonical update to `data_contracts.md`, capture as a change proposal (CP) before editing
- **Test requirement:** include an integration test verifying that existing packets with no adapter fields still parse and validate cleanly after the schema change

### P6-T05 — Wire adapter hints into context assembly
- **Status:** done
- **Description:** When a task packet declares a `primary_adapter`, bias context assembly toward the adapter's `relevant_file_patterns` and apply `context_priority_rules`. Adapter hints supplement existing doc-registry context selection — they do not replace it. No adapter = adapter-neutral, no behavior change.
- **Files:** `src/forge/services/context_service.py`, `src/forge/domain/context.py`
- **Model:** frontier_model
- **Dependencies:** P6-T04
- **Ready:** after P6-T04

### P6-T06 — Surface adapter review and validation hints in context output
- **Status:** done
- **Description:** When an adapter is active, include adapter-specific `review_focus_hints` and `test_or_validation_hints` in the context bundle output (visible in `forge context build` and `forge context export`). These are advisory hints, not enforced rules.
- **Files:** `src/forge/services/context_service.py`, `src/forge/domain/context.py`
- **Model:** open_model
- **Dependencies:** P6-T05
- **Ready:** after P6-T05

### P6-T07 — Add adapter system tests
- **Status:** done
- **Description:** Test adapter profile loading, domain model completeness, packet metadata parsing with and without adapter fields, context assembly with adapter hint wiring active and inactive.
- **Files:** `tests/test_adapter_loading.py` (new), `tests/test_adapter_context.py` (new), `tests/fixtures/` (adapter profile fixtures)
- **Model:** open_model
- **Dependencies:** P6-T01 through P6-T06
- **Ready:** after P6-T06

---

## 9. Phase 7 — New-Project Onboarding Flow

> **Status:** in_progress — planning decisions locked in `P7-T01`. Next ready tasks: `P7-T02`, `P7-T03`.

### P7 Planning Notes
- Scope: guided `forge init` with adapter selection, starter packet generation, basic project scaffolding
- Depends on: Phase 6 stable adapter contract ✓
- Planning doc: `docs/working/v2_onboarding.md`
- Start narrow: prove onboarding with `code_adapter` before generalizing

### P7-T01 — Resolve onboarding planning decisions and lock the minimal new-project flow
- **Status:** done
- **Description:** Resolve `docs/working/v2_onboarding.md` open planning questions for the new-project path, lock the minimal phase scope, and explicitly defer existing-project adoption decisions that are out of this phase's first slice.
- **Files:** `docs/working/v2_onboarding.md`, `docs/working/implementation_plan.md`, `docs/working/backlog.md`, `docs/working/current_focus.md`
- **Model:** frontier_model
- **Dependencies:** none
- **Ready:** yes

### P7-T02 — Add stable new-project onboarding prompt entrypoint
- **Status:** ready
- **Description:** Create a dedicated onboarding prompt entrypoint for new projects with a question-first flow and explicit adapter-selection inputs; keep `prompts/workflow.init.md` as compatibility guidance to the new flow.
- **Files:** `prompts/workflow.onboard.new.md` (new), `prompts/workflow.init.md`, `README.md`
- **Model:** frontier_model
- **Dependencies:** P7-T01
- **Ready:** yes

### P7-T03 — Expand `forge init` scaffolding to write baseline seed files from templates
- **Status:** ready
- **Description:** Update init scaffolding so missing baseline docs/runtime/task-template files are created from templates (not just directories), preserving additive-only behavior and dry-run correctness.
- **Files:** `src/forge/services/init_service.py`, `src/forge/cli/init.py`, `tests/test_init_service.py`
- **Model:** frontier_model
- **Dependencies:** P7-T01
- **Ready:** yes
- **Test requirement:** include coverage proving existing files are skipped and `--dry-run` reports without writing

### P7-T04 — Add adapter-selection options to onboarding initialization
- **Status:** draft
- **Description:** Add `--primary-adapter` and repeatable `--secondary-adapter` init options, validate declared adapters against runtime adapter profiles when available, and surface selected adapters in scaffold/onboarding outputs.
- **Files:** `src/forge/cli/init.py`, `src/forge/services/init_service.py`, `src/forge/adapters/adapter_config.py`, `tests/test_init_service.py`
- **Model:** frontier_model
- **Dependencies:** P7-T03
- **Ready:** after P7-T03

### P7-T05 — Add starter task-packet bootstrap for the onboarding path
- **Status:** draft
- **Description:** Add an optional onboarding bootstrap step that creates one starter task packet after init and initializes `docs/working/current_task.md` as `ready`, using selected adapter defaults where applicable.
- **Files:** `src/forge/services/init_service.py`, `src/forge/services/task_service.py`, `src/forge/cli/init.py`, `templates/tasks/task.md`, `tests/test_init_service.py`, `tests/test_task_create_cmd.py`
- **Model:** frontier_model
- **Dependencies:** P7-T03, P7-T04
- **Ready:** after P7-T04
- **Note:** if starter packet metadata contract changes are required, route through `docs/working/change_proposals.md` before canonical edits

### P7-T06 — Add onboarding integration tests and phase-level docs updates
- **Status:** draft
- **Description:** Add focused integration coverage for the new-project onboarding path (`init` scaffolding, adapter selection, starter packet bootstrap) and update user-facing docs to reflect the supported flow.
- **Files:** `tests/test_phase7_integration.py` (new), `README.md`, `docs/working/current_focus.md`
- **Model:** open_model
- **Dependencies:** P7-T02, P7-T05
- **Ready:** after P7-T05

### P7-T07 — Existing-project adoption prep boundary (deferred in this slice)
- **Status:** blocked
- **Description:** Keep FR-013 implementation out of the active execution loop until the new-project onboarding path is stable; record concrete entry criteria for when adoption flow work can start.
- **Files:** `docs/working/v2_onboarding.md`, `docs/working/future_roadmap.md`, `docs/working/current_focus.md`
- **Model:** open_model
- **Dependencies:** P7-T06
- **Ready:** blocked — after new-project onboarding is reviewed and stable

---

## 7. Backlog Maintenance Rules

1. backlog items must remain concrete and implementable
2. backlog items should map to one or more future task packets
3. large backlog items may later be split before execution
4. backlog items must not redefine canonical rules
5. items that require canonical change should link to a proposal, not silently change scope
