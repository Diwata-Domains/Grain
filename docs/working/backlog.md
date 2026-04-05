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

## 2. Phase 1 — Repository Foundation and Core CLI

### P1-T01 — Create base repository source structure
- **Status:** done
- **Description:** Create `src/forge/` with initial module directories for `cli`, `services`, `domain`, `adapters`, `validators`, and `templates`.

### P1-T02 — Implement CLI entrypoint
- **Status:** done
- **Description:** Add the main executable entrypoint and top-level command dispatch for the CLI.

### P1-T03 — Scaffold command groups
- **Status:** done
- **Description:** Add command group handlers for `init`, `docs`, `task`, `context`, `model`, and `review`.

### P1-T04 — Add repository root resolution
- **Status:** done
- **Description:** Implement logic to resolve repository root from current path or explicit `--repo` option.

### P1-T05 — Implement `forge init`
- **Status:** done
- **Description:** Create the initialization command that scaffolds required repo directories and starter files without silently overwriting protected artifacts.

### P1-T06 — Create template directory structure
- **Status:** done
- **Description:** Add `templates/docs/`, `templates/tasks/`, and `templates/prompts/` structure with placeholder template loading support.

### P1-T07 — Add CLI output formatting base
- **Status:** done
- **Description:** Implement shared output formatting for text output and prepare a stable interface for optional JSON output.

### P1-T08 — Add exit code and error handling conventions
- **Status:** done
- **Description:** Implement shared error types and exit code mapping aligned with canonical CLI rules.

### P1-T09 — Add initial CLI smoke tests
- **Status:** done
- **Description:** Create basic tests that verify CLI invocation, help output, and command group loading.

---

## 3. Phase 2 — Documentation Registry and Validation

### P2-T01 — Implement manifest file loader
- **Status:** done
- **Description:** Load `docs/runtime/docs_manifest.yaml` from repository-relative path.
- **Files:** `src/forge/adapters/manifest.py`, `pyproject.toml` (add `PyYAML`)
- **Model:** open_model
- **Dependencies:** none (Phase 1 complete)
- **Packet:** TASK-0010 (draft)
- **Ready:** yes

### P2-T02 — Implement manifest schema validation
- **Status:** done
- **Description:** Validate required top-level manifest sections and required fields for doc entries and task config.
- **Files:** `src/forge/validators/manifest_validator.py`
- **Model:** frontier_model
- **Dependencies:** P2-T01
- **Ready:** after P2-T01 implemented

### P2-T03 — Implement document registry model
- **Status:** done
- **Description:** Create in-memory structures for document records and layer-aware lookup.
- **Files:** `src/forge/domain/documents.py`
- **Model:** frontier_model
- **Dependencies:** P2-T01, P2-T02
- **Ready:** after P2-T02 implemented

### P2-T04 — Implement document existence validation
- **Status:** done
- **Description:** Validate that manifest-declared files and directories exist where required.
- **Files:** `src/forge/validators/doc_existence_validator.py`
- **Model:** open_model
- **Dependencies:** P2-T03
- **Ready:** after P2-T03 implemented

### P2-T05 — Implement authority-order validation
- **Status:** done
- **Description:** Validate manifest authority ordering and detect invalid editable/authority combinations where applicable.
- **Files:** `src/forge/validators/authority_validator.py`
- **Model:** frontier_model
- **Dependencies:** P2-T03
- **Ready:** after P2-T03 implemented

### P2-T06 — Implement `forge docs validate`
- **Status:** done
- **Description:** Expose repository documentation validation through CLI. Composes schema, existence, and authority validators.
- **Files:** `src/forge/cli/docs.py`, `src/forge/services/docs_service.py`
- **Model:** frontier_model
- **Dependencies:** P2-T02, P2-T04, P2-T05
- **Ready:** after P2-T05 implemented

### P2-T07 — Implement `forge docs show`
- **Status:** done
- **Packet:** P2-T07-TASK-0016
- **Description:** Show metadata and path information for one manifest-registered document.
- **Files:** `src/forge/cli/docs.py`
- **Model:** open_model
- **Dependencies:** P2-T03
- **Ready:** after P2-T03 implemented (can run in parallel with P2-T04/T05)

### P2-T08 — Implement `forge docs index` baseline behavior
- **Status:** done
- **Packet:** P2-T08-TASK-0018
- **Description:** Generate `docs_index.md` from the manifest as the authoritative source. Manifest is primary; index is derived. `forge docs index` writes or refreshes the index file from registered manifest entries.
- **Files:** `src/forge/services/docs_service.py`, `src/forge/cli/docs.py`, `docs/runtime/docs_index.md`
- **Model:** frontier_model
- **Dependencies:** P2-T03 (done)
- **Q5 decision:** manifest primary, index generated — resolved 2026-04-02
- **Ready:** yes

### P2-T09 — Add validator test fixtures for docs
- **Status:** done
- **Packet:** P2-T09-TASK-0017
- **Description:** Create valid and invalid manifest/doc structure test fixtures for all Phase 2 validators.
- **Files:** `tests/fixtures/`, `tests/test_docs_*.py`
- **Model:** open_model
- **Dependencies:** P2-T06 (all validators exist)
- **Ready:** after P2-T06 implemented

---

## 4. Phase 3 — Task Packet System

### P3-T01 — Implement task ID generator
- **Status:** done
- **Description:** Generate packet IDs in `TASK-####` format with zero-padding.
- **Files:** `src/forge/domain/packets.py` (new)
- **Model:** open_model
- **Dependencies:** none
- **Ready:** yes

### P3-T02 — Create packet template files
- **Status:** done
- **Description:** Add templates for `task.md`, `context.md`, `plan.md`, `deliverable_spec.md`, `results.md`, and `handoff.md`.
- **Files:** `templates/tasks/task.md`, `templates/tasks/context.md`, `templates/tasks/plan.md`, `templates/tasks/deliverable_spec.md`, `templates/tasks/results.md`, `templates/tasks/handoff.md`
- **Model:** open_model
- **Dependencies:** none
- **Ready:** yes

### P3-T03 — Implement packet directory creation
- **Status:** done
- **Description:** Create packet directories under `tasks/` using valid task IDs.
- **Files:** `src/forge/services/task_service.py` (new), `src/forge/adapters/filesystem.py`
- **Model:** open_model
- **Dependencies:** P3-T01, P3-T02
- **Ready:** after P3-T01 and P3-T02 implemented

### P3-T04 — Implement `forge task create`
- **Status:** done
- **Description:** Generate a new packet from templates with initial metadata and required files.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** frontier_model
- **Dependencies:** P3-T01, P3-T02, P3-T03
- **Ready:** after P3-T03 implemented

### P3-T05 — Implement `forge task list`
- **Status:** done
- **Description:** List existing task packets with basic metadata and status.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** open_model
- **Dependencies:** P3-T03
- **Ready:** after P3-T03 implemented

### P3-T06 — Implement `forge task show`
- **Status:** done
- **Description:** Display packet metadata, required file presence, and current status.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** open_model
- **Dependencies:** P3-T03, P3-T07
- **Ready:** after P3-T07 implemented

### P3-T07 — Implement packet status parser and updater
- **Status:** done
- **Description:** Read and update packet status using allowed canonical status values.
- **Files:** `src/forge/domain/packets.py`, `src/forge/validators/packet_validator.py` (new)
- **Model:** frontier_model
- **Dependencies:** P3-T01
- **Ready:** after P3-T01 implemented

### P3-T08 — Implement `forge task status`
- **Status:** done
- **Description:** Expose packet status transitions through CLI with validation.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** open_model
- **Dependencies:** P3-T07
- **Ready:** after P3-T07 implemented

### P3-T09 — Implement packet file validation
- **Status:** done
- **Description:** Validate required packet files and required metadata presence. Parse `ID`, `status`, and `phase` from `task.md` metadata block — no deeper parsing required in v1.
- **Q4 decision:** parse ID, status, phase only — resolved 2026-04-02
- **Files:** `src/forge/validators/packet_validator.py`
- **Model:** open_model
- **Dependencies:** P3-T01, P3-T07
- **Ready:** after P3-T07 implemented

### P3-T10 — Implement `forge task validate`
- **Status:** done
- **Description:** Validate one packet or all packets through CLI. Relies on parsed ID, status, and phase from P3-T09.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** open_model
- **Dependencies:** P3-T09
- **Ready:** after P3-T09 implemented

### P3-T11 — Implement closure validation rules
- **Status:** done
- **Description:** Validate whether a packet meets closure requirements for `done`.
- **Files:** `src/forge/validators/packet_validator.py`
- **Model:** frontier_model
- **Dependencies:** P3-T07, P3-T09
- **Ready:** after P3-T09 implemented

### P3-T12 — Implement `forge task close`
- **Status:** done
- **Description:** Attempt packet closure after running required validation checks.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/task_service.py`
- **Model:** frontier_model
- **Dependencies:** P3-T11
- **Ready:** after P3-T11 implemented

### P3-T13 — Add packet lifecycle tests
- **Status:** done
- **Description:** Test packet creation, validation, and allowed/disallowed state transitions.
- **Files:** `tests/test_task_create.py`, `tests/test_task_lifecycle.py`, `tests/test_task_validate.py`, `tests/fixtures/`
- **Model:** open_model
- **Dependencies:** P3-T04 through P3-T12
- **Ready:** after P3-T12 implemented

---

## 5. Phase 4 — Context Assembly and Model Routing

### P4-T01 — Implement packet context source discovery
- **Status:** done
- **Description:** Resolve packet-local files and candidate doc sources for one packet into a structured source list. Foundation for all context assembly tasks.
- **Files:** `src/forge/domain/context.py` (new), `src/forge/services/context_service.py` (new)
- **Model:** open_model
- **Dependencies:** none (Phase 3 done)
- **Ready:** completed

### P4-T02 — Implement canonical doc selection logic
- **Status:** done
- **Description:** Select relevant canonical docs for a packet without loading the full canonical set by default. Filter by `read_when` and task context signals; use manifest metadata from Phase 2 doc system.
- **Files:** `src/forge/domain/context.py`, `src/forge/services/context_service.py`
- **Model:** frontier_model
- **Dependencies:** P4-T01, Phase 2 document registry (done)
- **Ready:** completed

### P4-T03 — Implement optional working-doc inclusion logic
- **Status:** done
- **Description:** Include working docs only when explicitly needed for sequencing or blockers. Default: excluded. Add opt-in selection logic to context service.
- **Files:** `src/forge/domain/context.py`, `src/forge/services/context_service.py`
- **Model:** open_model
- **Dependencies:** P4-T01, P4-T02
- **Ready:** completed

### P4-T04 — Implement context bundle model
- **Status:** done
- **Description:** Create `ContextBundle` dataclass: packet files, selected canonical docs, optional working docs, export metadata. Structured output of assembly; input to export.
- **Files:** `src/forge/domain/context.py`
- **Model:** frontier_model
- **Dependencies:** P4-T01, P4-T02, P4-T03
- **Ready:** completed

### P4-T05 — Implement `forge context build`
- **Status:** done
- **Description:** Build a packet-scoped context bundle for a given task ID. Text shows selected sources. JSON serializes bundle.
- **Files:** `src/forge/cli/context.py`, `src/forge/services/context_service.py`
- **Model:** open_model
- **Dependencies:** P4-T04
- **Ready:** completed

### P4-T06 — Implement `forge context show`
- **Status:** done
- **Description:** Display assembled context sources for a packet (display-only, like `forge task show`). Runs after build or independently.
- **Files:** `src/forge/cli/context.py`
- **Model:** open_model
- **Dependencies:** P4-T05
- **Ready:** completed

### P4-T07 — Implement `forge context export`
- **Status:** done
- **Description:** Export assembled context bundle to a portable file for external coding agents. v1 format: single assembled markdown file with metadata header listing sources; `--format json` emits structured source metadata.
- **Files:** `src/forge/cli/context.py`, `src/forge/services/context_service.py`, `src/forge/adapters/export.py` (new)
- **Model:** frontier_model
- **Dependencies:** P4-T04, Q7 resolved
- **Q7 decision:** single assembled markdown file with metadata header — resolved 2026-04-03
- **Q11 decision:** no-tag invocation defaults to `running_tasks` — resolved 2026-04-05
- **CP-006 decision:** command-specific JSON shapes are distinct by design — applied 2026-04-05
- **Ready:** completed

### P4-T08 — Implement model profile configuration loader
- **Status:** done
- **Description:** Load model class definitions from `docs/runtime/agent_profiles.md` (already exists, manifest-registered). Parse open_model, frontier_model, reviewer_model and escalation rules into structured domain objects. No new config file needed in v1.
- **Files:** `src/forge/adapters/model_config.py` (new), `src/forge/domain/routing.py` (new)
- **Model:** open_model
- **Dependencies:** none
- **Q8 decision:** parse existing `agent_profiles.md` as profile source — resolved 2026-04-03
- **Ready:** completed

### P4-T09 — Implement model selection logic
- **Status:** draft
- **Description:** Given a workflow stage or task role, return the appropriate model class. Logic mirrors `agent_profiles.md` escalation rules without hardcoding vendor names.
- **Files:** `src/forge/domain/routing.py`, `src/forge/services/model_service.py` (new)
- **Model:** frontier_model
- **Dependencies:** P4-T08
- **Ready:** after P4-T08

### P4-T10 — Implement `forge model show`
- **Status:** draft
- **Description:** Display configured model classes and their capabilities. Text lists each class and use cases. JSON serializes profiles.
- **Files:** `src/forge/cli/model.py`
- **Model:** open_model
- **Dependencies:** P4-T08
- **Ready:** after P4-T08

### P4-T11 — Implement `forge model select`
- **Status:** done
- **Description:** Resolve model class for a given workflow stage or explicit role. Returns model class name. Thin CLI over routing domain.
- **Files:** `src/forge/cli/model.py`, `src/forge/services/model_service.py`
- **Model:** open_model
- **Dependencies:** P4-T09
- **Ready:** after P4-T09

### P4-T12 — Implement `forge model escalate`
- **Status:** draft
- **Description:** Given current model class and reason, return the escalation target class. Covers open_model → frontier_model and * → reviewer_model escalation paths.
- **Files:** `src/forge/cli/model.py`, `src/forge/services/model_service.py`
- **Model:** open_model
- **Dependencies:** P4-T09
- **Ready:** after P4-T09

### P4-T13 — Add context and routing tests
- **Status:** draft
- **Description:** End-to-end tests: context source selection, bundle completeness, export output, model class resolution, escalation path coverage.
- **Files:** `tests/test_context_build.py`, `tests/test_context_export.py`, `tests/test_model_routing.py`
- **Model:** open_model
- **Dependencies:** P4-T07, P4-T12
- **Ready:** after P4-T12

---

## 6. Phase 5 — Review, Handoff, and Hardening

### P5-T01 — Implement review validation service
- **Status:** draft
- **Description:** Validate packet completion readiness and review preconditions.

### P5-T02 — Implement `forge review check`
- **Status:** draft
- **Description:** Run review-oriented checks against a packet.

### P5-T03 — Implement handoff artifact support
- **Status:** draft
- **Description:** Create or validate handoff summary output for completed or review-ready packets.

### P5-T04 — Implement `forge review handoff`
- **Status:** draft
- **Description:** Expose handoff generation or validation through CLI.

### P5-T05 — Implement `forge review summary`
- **Status:** draft
- **Description:** Produce a structured summary of packet state, validation findings, and next actions.

### P5-T06 — Expand integration tests across core flows
- **Status:** draft
- **Description:** Add end-to-end tests covering init, docs validation, task creation, context export, and review flows.

### P5-T07 — Add golden fixtures for manifests and packets
- **Status:** draft
- **Description:** Create stable test fixtures for core repository and packet artifacts.

### P5-T08 — Improve CLI help and ergonomics
- **Status:** draft
- **Description:** Refine help text, common defaults, and output clarity for daily usage.

### P5-T09 — Clean up error messages and failure reporting
- **Status:** draft
- **Description:** Improve user-facing failure messages while preserving precise failure modes.

---

## 7. Backlog Maintenance Rules

1. backlog items must remain concrete and implementable
2. backlog items should map to one or more future task packets
3. large backlog items may later be split before execution
4. backlog items must not redefine canonical rules
5. items that require canonical change should link to a proposal, not silently change scope
