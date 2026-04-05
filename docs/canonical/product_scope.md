# Product Scope

## 1. Purpose

This document defines the product boundary for `Forge`.

It governs:
- project purpose
- target users
- primary use cases
- non-goals
- v1 constraints
- success criteria at the product level

It controls decisions about:
- what the toolkit is intended to do
- what classes of problems it should solve
- what must be excluded from v1
- what product behaviors are in scope versus out of scope

It does not cover:
- internal module design
- filesystem layout details beyond scope implications
- execution flow details
- packet lifecycle implementation details
- CLI command definitions
- runtime agent rules

Those belong in architecture and workflow specifications.

---

## 2. Product Definition

`Forge` is a CLI-first workflow orchestration toolkit for AI-assisted software development.

Its role is to structure software development work so that humans and external coding agents can operate through:
- explicit documentation layers
- scoped task packets
- minimal context loading
- model-agnostic execution paths
- reviewable, human-controlled canonical change flow

The toolkit is not a coding agent. It does not replace external coding tools. It prepares, structures, and governs work so external tools can execute tasks with clearer boundaries and less unnecessary context.

---

## 3. Product Goals

### 3.1 Primary Goals

1. Enforce a structured **Building Workflow** and **Build Loop**.
2. Maintain clear separation between:
   - canonical design authority
   - active execution planning
   - runtime execution guidance
   - task-local execution materials
3. Generate and manage **task packets** as the primary unit of execution.
4. Support **model-agnostic** workflows across multiple coding-agent ecosystems.
5. Minimize context passed into task execution.
6. Preserve human control over canonical project changes.
7. Remain lightweight enough for daily CLI usage.

### 3.2 Secondary Goals

1. Improve repeatability of AI-assisted development work.
2. Reduce prompt sprawl and broad, underspecified build requests.
3. Make project state inspectable through files on disk.
4. Support reuse across multiple projects with similar workflow needs.

---

## 4. Product Non-Goals

The toolkit must not become any of the following in v1:

### 4.1 Not a Coding Agent
The toolkit does not directly design, write, or refactor production code as its core responsibility.

### 4.2 Not a Project Management Suite
It is not a general PM platform, issue tracker, kanban system, or collaboration workspace.

### 4.3 Not a Multi-User Coordination System
It does not manage permissions, teams, approvals, or multi-user workflow state.

### 4.4 Not a Database-Centric System
It does not require a database, hosted backend, or remote service for core operation.

### 4.5 Not a GUI Product
There is no UI requirement for v1. All primary workflows must succeed through CLI and local files.

### 4.6 Not a Fully Autonomous Builder
The toolkit should not decide broad product direction independently or perform uncontrolled multi-step implementation loops without explicit task structure.

---

## 5. Target User

### 5.1 Primary User
A single developer or technical operator coordinating AI-assisted software development locally.

Typical characteristics:
- works in a repository directly
- uses external coding agents or model CLIs
- wants stronger structure than ad hoc prompting
- values inspectable files over opaque orchestration
- is willing to review and approve canonical changes manually

### 5.2 User Capabilities Assumed
The primary user can:
- run CLI commands
- edit repository files
- review markdown and YAML artifacts
- choose when to escalate or approve changes

The toolkit should not assume:
- team workflow infrastructure
- cloud service dependencies
- advanced prompt engineering knowledge
- custom database administration

---

## 6. Core Product Objects

This section defines the core product-level entities. Detailed implementation belongs elsewhere.

### 6.1 Canonical Docs
Stable source-of-truth project documents defining product intent, architecture, and workflow.

### 6.2 Working Docs
Mutable planning documents used to guide active execution and track open work.

### 6.3 Runtime Docs
Execution-facing documents that define operational behavior for tooling and agents.

### 6.4 Task Packets
Scoped bundles of task-specific execution materials used to prepare and govern one coherent unit of work.

### 6.5 Model Classes
Abstract execution roles:
- `open_model`
- `frontier_model`
- `reviewer_model`

These are workflow roles, not vendor bindings.

---

## 7. Core Use Cases

### 7.1 Initialize a Repository Workflow System
A user creates the required documentation and task structure for a new project.

### 7.2 Define Work in Small Executable Units
A user converts backlog items or implementation goals into scoped task packets.

### 7.3 Prepare Context for External Coding Agents
A user exports only the docs and instructions needed for one task.

### 7.4 Maintain Canonical Stability During Iteration
A user allows execution work to continue without permitting uncontrolled drift in product or architecture definitions.

### 7.5 Route Work by Model Class
A user assigns drafting, reasoning, or review work to different model classes without binding the system to one provider.

### 7.6 Review and Close Task Work
A user verifies that outputs match the requested deliverable and records results in a consistent structure.

---

## 8. v1 Scope

### 8.1 In Scope

#### Documentation System
- local markdown/yaml documentation layers
- clear authority separation
- explicit canonical docs
- task packet templates and lifecycle support

#### CLI Workflows
- repository initialization
- document validation
- task packet creation
- packet status updates
- packet preparation/export
- review/handoff support

#### Filesystem Operation
- all primary state stored in local repository files
- no database dependency

#### Model-Agnostic Routing
- model classes supported through configuration and workflow logic
- external tool integration through adapter-style boundaries

### 8.2 Conditionally In Scope
Only if lightweight and practical:
- manifest-driven validation
- prompt assembly from packet and doc context
- review checklist generation
- proposal generation for canonical changes

### 8.3 Out of Scope for v1
- GUI or web application
- collaborative state sync
- hosted remote service
- autonomous execution engine
- deep plugin framework
- complex permissions model
- repository-wide semantic indexing service
- heavy long-term memory system

---

## 9. Product Constraints

### 9.1 Interface Constraint
The product must be usable through CLI only in v1.

### 9.2 Storage Constraint
The product must operate on local filesystem state.

### 9.3 User Model Constraint
The system is single-user in v1.

### 9.4 Change Control Constraint
Canonical changes require human approval.

### 9.5 Context Constraint
Each task should load only the minimum valid documentation required.

### 9.6 Execution Boundary Constraint
External coding agents remain separate execution tools. `Forge` orchestrates workflow, context, and task structure.

### 9.7 Complexity Constraint
v1 should favor explicit files and simple flows over abstract orchestration machinery.

---

## 10. Product Principles

1. **Separation of concerns**
   - product definition, execution planning, runtime behavior, and task execution must remain distinct

2. **Minimal context loading**
   - pass only relevant material to task execution

3. **Task-based execution**
   - work should be expressed as small, scoped packets rather than broad build requests

4. **Model-agnostic design**
   - route by capability and workflow role, not provider identity

5. **Patch-over-rewrite**
   - prefer narrow changes and diffs over broad rewrites

6. **Explicit authority hierarchy**
   - every document type has a defined role and precedence

7. **Human-in-the-loop canonical control**
   - execution can move fast; canonical truth changes more slowly and deliberately

---

## 11. Success Criteria

The product is successful in v1 if it can reliably do the following:

1. Initialize a usable documentation and task structure in a repository.
2. Generate a task packet for one concrete task.
3. Identify the minimum set of docs needed for that task.
4. Prepare context for an external coding agent without loading unrelated project material.
5. Preserve separation between canonical docs and execution-layer docs.
6. Support at least basic routing across `open_model`, `frontier_model`, and `reviewer_model`.
7. Validate whether required files and packet structures are present and well-formed.
8. Remain fast and simple enough that the workflow overhead does not dominate the work.

---

## 12. Scope Boundaries for Downstream Decisions

### 12.1 Decisions This Document Controls
- whether a feature belongs in v1
- whether the toolkit is orchestration versus execution
- whether a behavior violates single-user / filesystem-first constraints
- whether a proposed feature introduces forbidden product complexity
- whether a flow aligns with the core principles

### 12.2 Decisions This Document Does Not Control
- exact module names and internal package layout
- exact packet schema fields
- command syntax and flags
- task lifecycle state names beyond product-level intent
- implementation details of adapters or validation routines

Those decisions must conform to this scope but are controlled elsewhere.