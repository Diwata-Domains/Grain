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

The architecture should be organized around the following top-level concerns:

1. **CLI surface**
2. **application services**
3. **document system**
4. **task packet system**
5. **context selection**
6. **model routing**
7. **external agent integration**
8. **validation**
9. **template/scaffolding support**

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

Use-case orchestration.

### 6.3 `domain/`

Core domain models and pure logic, such as:

- packet identity
- packet state
- document references
- manifest structures
- routing decisions

### 6.4 `adapters/`

Provider-specific bridges, such as:

- filesystem adapter
- external CLI adapters
- config adapter

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
