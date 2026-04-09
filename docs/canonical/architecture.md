# Architecture

## 1. Purpose

This document defines the structural design of `Forge`.

It governs:
- the major system components
- component responsibilities
- boundaries between components
- key filesystem structures
- data/control flow between components
- architectural constraints for v1

It controls decisions about:
- how the toolkit is organized internally
- how commands interact with repository state
- how task packets are created and validated
- how model routing is abstracted
- how external coding-agent integrations are isolated

It does not cover:
- product scope decisions
- phase planning
- implementation backlog
- runtime policy wording
- detailed workflow stage semantics beyond architectural boundaries

Those belong in product scope and workflow specification.

---

## 2. Architectural Overview

`Forge` is a local CLI application that reads and writes structured repository files in order to orchestrate AI-assisted development workflows.

### 2.1 Layered Subsystem Model

The architecture is organized into four distinct layers. These layers have explicit authority relationships — lower layers may not be mutated by higher layers without passing through the Review/Gate Layer.

```
┌─────────────────────────────────────┐
│     Advisory / Intelligence Layer   │  suggests, proposes, drafts
├─────────────────────────────────────┤
│        Review / Gate Layer          │  validates proposals before commit
├─────────────────────────────────────┤
│     Telemetry / Observability Layer │  observes, measures, records
├─────────────────────────────────────┤
│          Runtime Core               │  executes, enforces contracts, manages state
└─────────────────────────────────────┘
```

**Runtime Core** — task execution, packet lifecycle, contract enforcement, state transitions. This is the authoritative layer. It does not accept unvalidated advisory input.

**Advisory / Intelligence Layer** — suggests next tasks, phases, roadmap items; identifies missing work; provides efficiency and determinism insights. Outputs are proposals only — they do not directly mutate state.

**Telemetry / Observability Layer** — token usage, prompt counts, retries, latency, workflow efficiency, determinism signals, rework/drift/acceptance metrics.

**Review / Gate Layer** — validates advisory proposals; rejects malformed or inconsistent proposals; ensures contract compliance before any proposal is committed to system state.

### 2.2 Foundational Authority Rule

> **Intelligence may generate proposals. Only validated proposals may affect system state.**

This is a foundational architectural constraint. It applies to all advisory outputs, agent-generated content, and intelligence layer suggestions. No advisory output bypasses the Review/Gate Layer.

### 2.3 Component Concerns

The architecture is further organized around these internal concerns:

1. **CLI surface**
2. **application services**
3. **document system**
4. **task packet system**
5. **context selection**
6. **model routing**
7. **external agent integration**
8. **validation**
9. **template/scaffolding support**
10. **domain adapter system**
11. **orchestration service**

The architecture must keep orchestration logic separate from external execution tools.

---

## 3. Core Architectural Principles

1. **Filesystem-first**
   - repository files are the primary system state

2. **Explicit over implicit**
   - configuration, doc roles, and packet structure should be inspectable

3. **Thin CLI, structured services**
   - CLI commands should delegate to application services

4. **Loose provider coupling**
   - external model or coding-agent tools must sit behind adapters

5. **Task-local context assembly**
   - context should be assembled per packet, not globally

6. **Validation before automation**
   - the system should verify structure and authority before adding workflow convenience

7. **Patchable architecture**
   - components should allow extension without forcing rewrite of core flows

8. **Intelligence proposes, validation commits**
   - advisory and intelligence outputs are proposals, not direct state mutations
   - the Review/Gate Layer must validate all proposals before they affect the Runtime Core
   - this applies to agent-generated content, roadmap suggestions, candidate tasks, and all advisory outputs

9. **Constrained autonomy**
   - Forge supports advisory intelligence with an explicit autonomy model: observe → suggest → draft → constrained commit
   - constrained commit means advisory outputs may only affect system state under explicit, documented rules
   - no advisory layer component has unconditional write authority over canonical state

---

## 4. Primary System Components

### 4.1 CLI Layer

#### Responsibility
Expose user-facing commands and flags.

#### Must do
- parse command input
- invoke application services
- format output
- return clear exit codes

#### Must not do
- hold business rules
- directly encode packet or manifest logic
- contain provider-specific orchestration logic

#### Example command groups
- `init`
- `docs`
- `task`
- `context`
- `model`
- `review`

Command naming may evolve, but responsibilities should remain stable.

---

### 4.2 Application Services Layer

#### Responsibility
Implement the toolkit's core use cases.

#### Service categories
- initialization service
- document registry/manifest service
- packet service
- context assembly service
- model routing service
- validation service
- review/handoff service
- orchestration service

#### Must do
- orchestrate file reads/writes
- enforce workflow rules
- compose lower-level helpers
- return structured results to the CLI

#### Must not do
- embed provider CLI specifics deeply into unrelated services

---

### 4.3 Document System

#### Responsibility
Represent and manage the project's documentation layers.

#### Sub-responsibilities
- register doc types and paths
- read doc metadata from manifest
- distinguish authority layers
- support read selection by use case
- validate expected file presence and structure

#### Inputs
- `docs_manifest.yaml`
- repository doc files

#### Outputs
- doc lookup results
- manifest validation results
- selected doc sets for tasks

---

### 4.4 Task Packet System

#### Responsibility
Create, update, validate, and manage task packets as the unit of execution.

#### Minimum packet responsibilities
- create packet directories
- assign packet IDs
- populate required files from templates
- track packet status
- enforce required completion artifacts
- support handoff and review preparation

#### Packet boundary
A packet represents one coherent task, not an entire phase or large feature program.

---

### 4.5 Context Selection System

#### Responsibility
Select the minimum valid set of docs and packet materials for one task.

#### Must do
- use task type and manifest metadata
- include packet-local context first
- add only relevant canonical docs
- optionally include selected working docs when required

#### Must not do
- load the full repository by default
- rely on hidden long-lived state
- infer broad context without traceability

---

### 4.6 Model Routing System

#### Responsibility
Map workflow steps to model classes.

#### Supported model classes
- `open_model`
- `frontier_model`
- `reviewer_model`

#### Must do
- route by workflow role and capability
- remain provider-agnostic
- support escalation

#### Must not do
- hardcode one provider as the architecture
- couple workflow semantics to vendor names

---

### 4.7 External Agent Integration Layer

#### Responsibility
Bridge packet/context outputs to external coding-agent tools.

#### Expected integrations
- Codex CLI
- Claude CLI
- future external tools through the same boundary

#### Must do
- export prepared context bundles
- support invocation-friendly formatting
- isolate provider-specific command assembly

#### Must not do
- subsume coding-agent responsibilities
- make core packet logic depend on one external tool

---

### 4.8 Validation System

#### Responsibility
Verify repository structure and workflow artifacts.

#### Validation targets
- required docs exist
- manifest is well-formed
- packet structure is valid
- packet status transitions are allowed
- authority constraints are respected
- context selection references valid files

#### Design requirement
Validation should be callable independently from execution-oriented commands.

---

### 4.9 Template and Scaffolding System

#### Responsibility
Provide initial file templates for canonical docs, working docs, runtime docs, and task packets.

#### Must do
- initialize a project consistently
- reduce manual setup
- provide stable starter shapes

#### Must not do
- encode project-specific logic into generic templates

---

### 4.10 Advisory / Intelligence Layer

#### Responsibility
Generate proposals, suggestions, and advisory outputs that help the operator plan, prioritize, and improve workflow quality. This layer observes system state and produces structured proposal objects — it does not execute or commit.

#### Advisory outputs
- `candidate_task` — proposed task not yet accepted into the backlog
- `candidate_phase` — proposed phase not yet committed to the plan
- `candidate_roadmap_item` — proposed roadmap entry not yet accepted
- `recommendation` — general advisory suggestion (efficiency, sequencing, gaps)
- efficiency insights — token usage patterns, rework signals, drift warnings
- determinism/ambiguity analysis — identifies underspecified areas before execution

#### Must do
- output structured proposal objects
- clearly mark all outputs as advisory/draft
- pass outputs to the Review/Gate Layer before any state change

#### Must not do
- directly mutate canonical docs, task packets, or system state
- bypass the Review/Gate Layer
- autonomously commit proposals without human validation

---

### 4.11 Telemetry / Observability Layer

#### Responsibility
Record, aggregate, and surface workflow quality signals. Provides the data inputs for both human review and the Advisory Layer.

#### Metrics tracked
- token usage (input, output, total per task and phase)
- prompt run counts and conversation restarts
- retry and rework counts
- task latency and phase duration
- workflow efficiency metrics
- determinism signals (variance in outputs for similar tasks)
- drift incidents and acceptance rates

#### Must do
- record metrics non-intrusively alongside normal workflow execution
- expose metrics in structured, inspectable form
- support both exact counts (when runtimes expose them) and proxy metrics

#### Must not do
- block or alter execution flow
- require external telemetry services in v1

---

### 4.13 Domain Adapter Layer

#### Responsibility
Bridge domain-specific execution hints, context selection priorities, validation patterns, and review focus into the Forge workflow without modifying the Runtime Core or workflow law.

#### Adapter categories

**Official adapters** — maintained by the Forge project; distributed as part of the core system. Examples: `code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`.

**Custom adapters** — defined locally within a repo for domain-specific or private use cases. Examples: a `devops_adapter` for VPS provisioning tasks, a `local_ops_adapter` for machine-admin repos, or a domain-specific adapter for any operational workflow expressible through repo artifacts. Custom adapters must conform to the same contract as official adapters.

#### Adapter contract expectations
- each adapter is a declarative, filesystem-visible profile, not runtime code
- adapters specify context selection hints, validation focus, review patterns, deliverable guidance, and optional model-routing hints
- adapters must declare a stable `adapter_id`, a `domain_type`, and at least one context or validation hint
- adapter definitions live in `docs/runtime/adapter_profiles.md` (or a custom location declared in the manifest)

#### Must do
- extend workflow behavior through hints and guidance
- remain declarative and inspectable in repo files
- degrade safely when no adapter is declared (adapter-neutral behavior)
- conform to the Runtime Core validation contract

#### Must not do
- override workflow stages, packet lifecycle states, or closure semantics
- bypass the Review/Gate Layer
- introduce hidden state outside repo-visible files
- directly commit advisory proposals or canonical changes
- depend on opaque environment state as the source of truth
- require a different build loop per domain

#### Adapter capability surface

Adapters may optionally expose structured capabilities that the orchestration service can query. These capabilities are advisory inputs — the orchestration service may use them to inform planning proposals but they do not produce direct state changes.

Optional adapter capabilities:
- `detect_scope` — identify which file patterns, services, or operational areas are relevant to a described work item
- `collect_context` — provide domain-specific context selection hints for a task in this domain
- `analyze_impact` — surface likely dependencies, affected files, or downstream areas given a set of touched files
- `validate_changes` — report domain-specific validation requirements for outputs in this domain
- `export_artifacts` — describe expected deliverable patterns for tasks in this domain
- `suggest_followups` — identify likely follow-up work in this domain given an execution outcome

Adapters that do not implement capability functions remain fully valid. Orchestration degrades gracefully when capabilities are absent. Capabilities do not alter how adapters are selected for task packets — that remains explicit and operator-declared.

A structural analysis tool (such as a tree-sitter-based dependency parser) may be used to implement `detect_scope` and `analyze_impact` locally and without LLM overhead. Tree-sitter is an implementation option for these capabilities, not a workflow authority.

#### Adapter boundary rule
If an adapter appears to require changing core workflow semantics, the adapter's boundary is wrong. The workflow is invariant; adapters supply hints within it.

---

### 4.14 Orchestration Service

#### Responsibility
Coordinate work across multiple adapters and workflow surfaces to produce structured planning artifacts. The orchestration service operates above individual adapters, uses adapter capabilities as inputs, and produces packet sequence plans, split recommendations, phase shape proposals, and cross-domain dependency maps.

All orchestration outputs are proposals. They pass through the Review/Gate Layer before affecting system state. No orchestration output directly creates or mutates task packets.

#### Orchestration levels

**Task-level orchestration**
- determine which adapters and domains are relevant to a described work item
- recommend whether work should be one packet or split into multiple packets
- detect cross-domain dependencies and likely follow-up packets
- propose a sequenced set of packet candidates

**Phase-level orchestration**
- assist with phase shaping and task sequencing within a phase
- identify dependency chains across packets in a phase
- detect when a phase boundary should be reconsidered (split, expand, replan)
- produce candidate phase structures as proposals for human review

**Project-level orchestration**
- provide a project-wide coordination surface above individual adapters
- support multi-surface planning without collapsing domain boundaries
- ensure all outputs remain inspectable and file-backed

#### Outputs

All orchestration outputs are typed proposal objects:
- `PacketSequencePlan` — ordered set of packet candidates with dependency links
- `split_recommendation` — advisory recommendation to decompose one work item into multiple packets
- `phase_shape_proposal` — draft phase structure for human review and acceptance
- `cross_domain_dependency` — identified dependency between work spanning separate adapters or domains

#### Must do
- produce structured, inspectable, file-backed outputs
- pass all outputs to the Review/Gate Layer before any system-state change
- accept adapter capability inputs without requiring any specific capability
- degrade gracefully when no adapter is active
- respect the packet lifecycle — candidates must be converted to packets through the normal packet creation flow

#### Must not do
- directly create or mutate task packets without explicit operator action
- bypass the packet lifecycle or packet creation commands
- directly alter canonical docs, the backlog, or the phase plan without passing through review
- replace the task packet as the execution unit
- subsume the Runtime Core or the Review/Gate Layer
- execute a multi-step plan autonomously without an explicit human gate at each step

#### Relationship to other components

The orchestration service is a sibling of other application services (context assembly, packet service, validation service). It is not a replacement for any of them. It coordinates across them — querying adapters for scope signals, recommending packet splits, proposing phase shapes — but it does not own their responsibilities.

The Advisory/Intelligence Layer may feed inputs to the orchestration service. The orchestration service outputs proposals which then pass to the Review/Gate Layer. The orchestrator is not itself an advisory layer — it is a coordination service whose outputs happen to be proposals.

---

### 4.12 Review / Gate Layer

#### Responsibility
Validate advisory proposals before they may affect system state. Acts as the enforcement boundary between the Advisory Layer and the Runtime Core.

#### Gate responsibilities
- validate that proposal objects are well-formed and consistent
- reject proposals that violate canonical constraints, contract rules, or workflow authority
- ensure canonical change proposals follow the approved change flow
- record gate decisions (accepted, rejected, deferred)

#### Must do
- evaluate all advisory proposals against canonical and runtime rules
- provide clear rejection reasons
- support human override as the final approval authority

#### Must not do
- auto-commit proposals without explicit human approval for canonical-impacting changes
- block execution of non-advisory runtime operations

---

## 5. Repository Structure

The architecture should assume a repository layout similar to:

```text
<repo-root>/
  docs/
    canonical/
      product_scope.md
      architecture.md
      workflow_spec.md
    working/
    runtime/
  tasks/
    TASK-0001/
      task.md
      context.md
      plan.md
      deliverable_spec.md
      results.md
      handoff.md
      patches/
  templates/
    docs/
    tasks/
    prompts/
  src/
    forge/
      cli/
      services/
      domain/
      adapters/
      validators/
      templates/
  tests/
```

This layout is illustrative but establishes the required separations:

- docs are separate from task packets
- templates are separate from live project state
- source code is separate from repository content being managed

---

## 6. Internal Module Boundaries

A practical v1 package layout should separate concerns as follows:

### 6.1 `cli/`

Command parsing and user-facing command handlers.

### 6.2 `services/`

Use-case orchestration. Includes the orchestration service, which produces PacketSequencePlan and related proposal objects. The orchestration service lives here alongside other application services and does not receive its own top-level module.

### 6.3 `domain/`

Core domain models and pure logic, such as:

- packet identity
- packet state
- document references
- manifest structures
- routing decisions

### 6.4 `adapters/`

Two distinct adapter types live here:

**Provider adapters** — bridges to external tools and services:
- filesystem adapter
- external CLI adapters (Codex, Claude, etc.)
- config adapter

**Domain adapters** — bridges to domain-specific execution behavior:
- adapter profile loader (parses `docs/runtime/adapter_profiles.md`)
- domain model (`AdapterProfile`) definitions
- context selection integration (applies adapter hints to context assembly)

These must not collapse. Provider adapters isolate external dependencies. Domain adapters extend workflow behavior for specific execution domains. Neither should carry the other's responsibilities.

### 6.5 `validators/`

Artifact validation and rule enforcement.

### 6.6 `templates/`

Template resolution and rendering logic.

This boundary is recommended for v1. The exact filenames may vary, but responsibilities should not collapse.

---

## 7. Core Data Structures

This section defines the architecture-facing structures, not full schema files.

### 7.1 Document Record

Represents one known project document.

Minimum fields:
- `id`
- `path`
- `layer`
- `purpose`
- `authority`
- `editable_by_agents`
- `read_when`

### 7.2 Task Packet Record

Represents one packet's metadata.

Minimum fields:
- `id`
- `path`
- `status`
- `title`
- `created_at`
- `updated_at`
- `phase` (optional)
- `dependencies` (optional)

### 7.3 Context Bundle

Represents the material assembled for task execution.

Minimum sections:
- packet files
- selected canonical docs
- selected working docs (if needed)
- runtime references (if needed by execution tooling)
- export metadata

### 7.4 Model Profile

Represents one model class configuration.

v1 implemented fields (derived from `docs/runtime/agent_profiles.md`):
- `model_class`
- `use_for`
- `avoid_for`
- `preferred_models`
- `escalation_targets`

Deferred to a later phase:
- `capabilities`
- `cost_class`
- `latency_class`
- `preferred_stages`

These deferred fields were part of the original aspirational schema but are not present in `agent_profiles.md` or the v1 implementation. They may be added when the routing domain is extended.

### 7.5 AdapterProfile

Represents one domain adapter's contract definition. Loaded from `docs/runtime/adapter_profiles.md` (or a custom manifest-declared path).

Required fields:
- `adapter_id` — stable identifier (e.g. `code_adapter`, `devops_adapter`)
- `domain_type` — broad class (e.g. `code`, `frontend`, `devops`, `docs`, `spreadsheet`, `local_ops`)
- `applies_to` — list of languages, frameworks, project types, or operational domains the adapter governs

Required hint presence (at least one of):
- `context_priority_rules`
- `test_or_validation_hints`

Optional hint fields:
- `relevant_file_patterns`
- `ignore_file_patterns`
- `build_or_run_hints`
- `review_focus_hints`
- `default_model_bias`

### 7.6 Proposal Object

Represents an advisory output before it has been validated and committed. Proposal objects are first-class artifacts — they are inspectable, rejectable, and deferrable.

Minimum fields:
- `type` — one of: `recommendation`, `candidate_task`, `candidate_phase`, `candidate_roadmap_item`
- `source` — which layer or agent produced the proposal
- `status` — one of: `draft`, `under_review`, `accepted`, `rejected`, `deferred`
- `summary` — human-readable description of the proposal
- `affected_artifacts` — what canonical docs, packets, or backlog items would be changed if accepted
- `validation_notes` — gate layer findings

### 7.7 OrchestratorPlan

Represents a structured planning artifact produced by the orchestration service. An OrchestratorPlan is a proposal — it must pass through the Review/Gate Layer before affecting system state. Accepted candidates within a plan are converted to task packets through the normal packet creation flow.

Minimum fields:
- `plan_id` — stable identifier for this plan instance
- `scope_summary` — human-readable description of the work being planned
- `active_adapters` — list of adapter IDs whose capabilities were queried
- `packet_candidates` — ordered list of proposed packets with titles, scope, and adapter assignments
- `dependency_links` — identified dependencies between packet candidates
- `cross_domain_flags` — domains or surfaces that span more than one adapter
- `split_recommendations` — any candidate packets flagged for further decomposition before acceptance
- `status` — one of: `draft`, `under_review`, `accepted`, `rejected`, `deferred`
- `produced_by` — which service or agent produced this plan

---

## 8. Architectural Flows

### 8.1 Initialization Flow

1. user invokes init command
2. CLI calls initialization service
3. scaffolding/templates are resolved
4. required directory structure is created
5. seed docs and packet templates are written
6. validation confirms repository is usable

### 8.2 Task Packet Creation Flow

1. user invokes packet creation command
2. packet service allocates packet ID
3. packet directory is created
4. required files are rendered from templates
5. initial metadata is stored
6. packet validation runs

### 8.3 Context Assembly Flow

1. user selects or references a task packet
2. context service reads packet metadata
3. document system identifies relevant docs
4. selected docs are assembled into a context bundle
5. bundle is exported for external execution use

### 8.4 Review / Completion Flow

1. packet marked ready for review
2. validation service checks required artifacts
3. model routing may select `reviewer_model`
4. review output is recorded
5. packet is closed or returned for further work

### 8.5 Canonical Change Proposal Flow

1. execution discovers canonical conflict or missing rule
2. change is recorded as a proposal, not a direct canonical edit
3. proposal is attached to packet or working-doc proposal area
4. human reviews and approves separately

### 8.6 Advisory Proposal Flow

The general flow for all advisory outputs follows a strict propose → validate → commit model:

1. Advisory/Intelligence Layer generates a proposal object (`candidate_task`, `recommendation`, etc.)
2. Proposal is passed to the Review/Gate Layer
3. Gate Layer validates against canonical rules and contracts
4. If valid: proposal is surfaced to the human operator for acceptance
5. If accepted: proposal is committed to the appropriate artifact (backlog, roadmap, canonical doc)
6. If rejected or deferred: proposal is recorded with reason; no state change occurs

At no point does an advisory output directly mutate system state. The operator is the final commit authority for canonical-impacting proposals.

### 8.8 Orchestration Flow

1. operator describes a work item, a phase, or a cross-domain scope to be orchestrated
2. orchestration service queries active adapters using declared capability functions (`detect_scope`, `analyze_impact`, `suggest_followups`) where available
3. adapter capability outputs are collected as input signals — no state changes occur
4. orchestration service produces an `OrchestratorPlan` containing packet candidates, dependency links, cross-domain flags, and split recommendations
5. `OrchestratorPlan` passes to the Review/Gate Layer as a proposal
6. gate validates plan against canonical rules and packet contracts
7. operator reviews and accepts, modifies, or rejects the plan
8. accepted candidates are converted to task packets through the normal packet creation flow (`forge task create`)
9. no packets are created or mutated before step 8

### 8.7 Telemetry Collection Flow

1. workflow events are emitted during task execution, review, and close
2. Telemetry Layer records event data non-intrusively
3. metrics are aggregated at task and phase boundaries
4. aggregated signals are available to the Advisory Layer and human operator
5. efficiency insights may become `recommendation` proposals through the advisory flow

---

## 9. Architectural Constraints

### 9.1 No Database in v1

Persistent state must be derived from files.

### 9.2 No Hidden Workflow State

A user should be able to inspect the current workflow position from repository artifacts.

### 9.3 No Mandatory Background Services

The toolkit should run as an ordinary local CLI application.

### 9.4 No Provider-Locked Core

Core services must not depend on one model vendor or one external coding tool.

### 9.5 No Broad Repository Ingestion by Default

Architecture must preserve targeted context assembly.

### 9.6 No Unvalidated Advisory Mutation

Advisory and intelligence layer outputs must not directly alter canonical docs, task packets, backlog, or system state. All advisory outputs must pass through the Review/Gate Layer and receive explicit human approval before committing to canonical-impacting artifacts.

### 9.8 Adapter Boundary Rule

Domain adapters may extend workflow behavior through hints, context selection priorities, validation focus, and review guidance. Adapters must not:
- override packet lifecycle states or state transition rules
- bypass the Review/Gate Layer
- introduce hidden state outside repo-visible files
- require different canonical authority rules per domain
- directly alter canonical docs, backlog, or task packets without passing through the normal workflow

A custom adapter that requires breaking these rules must be redesigned.

### 9.9 Orchestration Boundary Rule

The orchestration service may coordinate planning across adapters and produce structured proposals. It must not:
- execute workflow stages autonomously without explicit operator approval at each gate
- bypass the packet lifecycle or treat packet candidates as pre-created packets
- mutate canonical docs, backlog, or task packets directly
- require a different workflow loop per domain or per plan type
- collapse adapter boundaries into a unified execution surface
- operate without passing all outputs through the Review/Gate Layer

An orchestration plan that requires bypassing the packet model or the Review/Gate Layer exceeds the orchestration service's boundary. Break the plan into smaller, separately proposed pieces.

### 9.7 Constrained Autonomy Boundary

The permitted autonomy model for advisory components is:
1. **Observe** — read system state without modifying it
2. **Suggest** — generate proposal objects marked as draft
3. **Draft** — produce candidate artifacts for human review
4. **Constrained commit** — update non-canonical artifacts (working docs, task results) only under explicit documented rules

Advisory components must not operate outside this boundary.

---

## 10. Integration Boundary Definition

### 10.1 Input Boundary

The toolkit consumes:
- repository files
- manifest/config files
- CLI arguments
- optional integration configuration for external tools

### 10.2 Output Boundary

The toolkit produces:
- structured docs
- task packet files
- context bundles
- validation results
- review/handoff artifacts
- invocation-ready exports for external tools

### 10.3 External Tool Boundary

External coding agents receive prepared context and instructions but remain outside the core architecture.

The toolkit may help stage their work, but does not own their internal execution behavior.

---

## 11. Architecture Decisions for v1

### 11.1 Required Decisions

- use local files as state
- use task packets as the execution unit
- use manifest/document registry for doc discovery
- use service-oriented command handling
- use adapters for external tool integration
- route models by abstract class

### 11.2 Deferred Decisions

The following may be deferred until later phases:

- advanced caching
- plugin marketplace architecture
- remote storage backends
- multi-project workspace controller
- semantic search/index layer
- advanced event system

---

## 12. Decision Boundaries

### 12.1 Decisions This Document Controls

- major component boundaries
- module responsibility separation
- architectural flows
- integration boundaries
- where validation belongs
- how routing and external adapters are isolated

### 12.2 Decisions This Document Does Not Control

- whether a feature belongs in product scope
- exact workflow stage rules
- packet completion semantics
- approval rules for canonical changes
- detailed read order during task execution

Those must align with this architecture but are governed elsewhere.
