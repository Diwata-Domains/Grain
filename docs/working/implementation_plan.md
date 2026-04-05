# Implementation Plan

## 1. Purpose

This document defines the execution sequence for building `Forge`.

It is derived from the canonical docs and is limited to:
- implementation sequencing
- phase objectives
- major deliverables
- dependencies between phases

It does not redefine:
- product scope
- architecture boundaries
- workflow semantics
- canonical data contracts

---

## 2. Execution Strategy

Build v1 in five phases.

Sequencing rule:
- finish the minimum stable foundation of each phase before expanding breadth
- prefer validation and inspectability before automation convenience
- keep Phase 1 and Phase 2 narrow so task packet execution can start early
- treat token efficiency as an execution-quality metric: reduce unnecessary context loads, retries, and artifact rewrites as the workflow stabilizes

---

## 3. Phase Breakdown

## Phase 1 — Repository Foundation and Core CLI ✓ CLOSED

### Objective
Establish the minimum runnable repository structure and CLI shell required to support the rest of the system.

### Major Deliverables
- base source tree under `src/forge/` ✓
- CLI entrypoint (Click, `forge` command) ✓
- command group scaffolding (all 6 groups, 18 subcommands) ✓
- repository root resolution (`adapters/filesystem.py`) ✓
- repository init command (`forge init`) ✓
- template directory structure and loader ✓
- CLI output formatting base (`CommandResult`, `--format text|json`) ✓
- exit code and error handling conventions (7 typed exceptions, exit codes 1–7) ✓
- initial test harness for CLI smoke checks (63 tests, subprocess smoke suite) ✓

### Output Focus
This phase should make it possible to:
- initialize a repo structure
- run a CLI command successfully
- establish a stable location for services, validators, adapters, and templates

### Dependencies
- depends only on canonical docs
- no upstream implementation dependencies

---

## Phase 2 — Documentation Registry and Validation ✓ CLOSED

### Objective
Implement manifest parsing and repository document validation.

### Major Deliverables
- docs manifest loader ✓ (TASK-0010)
- manifest schema validator ✓ (TASK-0011)
- document existence validator ✓ (TASK-0013)
- authority-aware document registry model ✓ (TASK-0012)
- docs validation CLI commands (`forge docs validate`) ✓ (TASK-0015)
- docs inspection command (`forge docs show`) ✓ (P2-T07-TASK-0016)
- validator test fixtures ✓ (P2-T09-TASK-0017)
- `forge docs index` baseline behavior ✓ (P2-T08-TASK-0018)

### Output Focus
This phase should make it possible to:
- load and validate `docs_manifest.yaml` from the CLI ✓
- inspect document metadata through CLI ✓
- detect missing or malformed required docs ✓

### Notes
- 154/154 tests passing at phase close
- CP-001/CP-002 applied: packet directory naming now uses `P<N>-T<NN>-TASK-####` consistently across runtime and canonical docs
- Q5 resolved: manifest primary, `docs_index.md` generated — unblocked and completed P2-T08
- Q4 resolved: parse ID, status, phase only from task.md metadata block

### Dependencies
- requires Phase 1 CLI foundation ✓

---

## Phase 3 — Task Packet System ✓ CLOSED

### Objective
Implement task packet creation, validation, and lifecycle state handling.

### Major Deliverables
- task ID generation ✓ (P3-T01-TASK-0019)
- packet templates ✓ (P3-T02-TASK-0020)
- packet directory creation ✓ (P3-T03-TASK-0021)
- `forge task create` ✓ (P3-T04-TASK-0022)
- `forge task list` ✓ (P3-T05-TASK-0023)
- `forge task show` ✓ (P3-T06-TASK-0024)
- packet status parser/updater ✓ (P3-T07-TASK-0025)
- `forge task status` ✓ (P3-T08-TASK-0026)
- packet file validation ✓ (P3-T09-TASK-0027)
- `forge task validate` ✓ (P3-T10-TASK-0028)
- closure validation rules ✓ (P3-T11-TASK-0029)
- `forge task close` ✓ (P3-T12-TASK-0030)
- packet lifecycle tests ✓ (P3-T13-TASK-0031)

### Output Focus
This phase should make it possible to:
- create a valid packet ✓
- move it through lifecycle states ✓
- validate whether a packet is execution-ready or closeable ✓

### Notes
- 272/272 tests passing at phase close
- Q4 resolved: parse ID, status, phase only from task.md metadata block
- Q9 resolved: plain markdown templates, simple string replace (no rendering engine)
- Exit code 5 (InvalidTransitionError) requires subprocess tests — established pattern for Phase 4+
- Metadata format: colon inside bold markers (`**key:**`) — enforced by `_METADATA_LINE` regex

### Dependencies
- requires Phase 1 CLI foundation ✓
- depends on Phase 2 contract/manifest validation for shared validation patterns ✓

---

## Phase 4 — Context Assembly and Model Routing ← ACTIVE

### Objective
Implement minimal-context preparation and model-class selection support.

### Major Deliverables
- context selection service
- packet context bundle builder
- context show/export commands
- model profile loader
- model selection logic
- model escalation command

### Output Focus
This phase should make it possible to:
- assemble task-local execution context
- export context for external tools
- map work to `open_model`, `frontier_model`, or `reviewer_model`

### Dependencies
- requires Phase 2 document registry
- requires Phase 3 task packet system

---

## Phase 5 — Review, Handoff, and Hardening

### Objective
Complete the operational workflow with review support, handoff artifacts, and baseline reliability improvements.

### Major Deliverables
- review check command
- handoff generation/validation support
- summary command for packet state
- expanded validation coverage
- golden-path tests across init/docs/task/context/review flows
- CLI ergonomics cleanup

### Output Focus
This phase should make it possible to:
- review packet outputs consistently
- support packet closure and handoff
- run core v1 workflows with confidence

### Dependencies
- requires Phases 1 through 4

---

## 4. High-Level Sequencing

Recommended sequence:

1. create runnable CLI shell
2. scaffold repository initialization
3. implement docs manifest loading and validation
4. implement packet creation and lifecycle handling
5. implement context selection and export
6. implement model routing
7. implement review/handoff support
8. harden with tests and CLI cleanup

---

## 5. Dependency Summary

### Hard Dependencies
- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 1 and benefits from Phase 2
- Phase 4 depends on Phases 2 and 3
- Phase 5 depends on Phases 1 through 4

### Soft Dependencies
- test coverage should begin in Phase 1 and expand each phase
- template work begins in Phase 1 and evolves in Phases 2 and 3
- adapter boundaries should be established in Phase 1 even if full integration waits until Phase 4

---

## 6. Implementation Priorities

Priority order inside the plan:

1. CLI entrypoint and repository structure
2. manifest/document validation
3. task packet creation and validation
4. context assembly
5. model routing

---

## 7. Design Guardrails

Keep the working system minimal and non-duplicative.

Guardrails:
- each document layer should have one clear job
- working docs should guide execution, not restate canonical truth
- prompts should stay narrow and command-shaped
- add backlog items only for concrete work, not general concerns
- if a concern is about process or clarity rather than implementation, record it here instead of the backlog
- if prompt, runtime, or workflow-contract docs change mid-conversation, restart the relevant agent conversation instead of assuming context refreshed automatically

---

## 7. Out-of-Sequence Work to Avoid

Do not start these before their prerequisite phases are stable:
- advanced provider-specific integrations before Phase 4
- rich review automation before basic packet validation exists
- complex prompt systems before context export exists
- plugin abstractions before core flows are working
- database or service-backed state at any point in v1

---

## 8. Phase Completion Standard

A phase is complete when:
- its major deliverables exist
- the core CLI path for that phase works end-to-end
- its outputs are validated at least at a basic level
- downstream phases can proceed without reworking the phase foundation

---

## 9. Phase Retrospective Rule

Use phase review and close to improve the system deliberately, not continuously at random.

At phase review or phase close, classify system-level findings into:
- `fix_now` — workflow bugs or drift that will likely harm the next task or next phase if left unresolved
- `batch_next_phase` — repeated friction, validator ideas, prompt cleanup, metrics cleanup, or ergonomics improvements that are real but not urgent
- `ignore` — one-off noise or issues not worth system change

Rules:
- apply `fix_now` items during phase close or immediately after if they block safe continuation
- record `batch_next_phase` items in working docs and create backlog items only when the work is already concrete and scoped
- do not create backlog work from general opinions alone
- route unresolved decisions to `open_questions.md`
- route canonical or runtime authority gaps to `change_proposals.md`
