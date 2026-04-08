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

### 2.1 Forge

`Forge` is a CLI-first workflow orchestration system for AI-assisted software development.

Forge is the **build and execution system**. Its role is to structure software development work so that humans and external coding agents can operate through:
- explicit documentation layers
- scoped task packets
- minimal context loading
- model-agnostic execution paths
- reviewable, human-controlled canonical change flow

Forge is not a coding agent. It does not replace external coding tools. It prepares, structures, and governs work so external tools can execute tasks with clearer boundaries, less unnecessary context, and less token waste across repeated agent conversations.

Forge exists in part because agent-CLI users often lose throughput to broad context dumps, repeated planning, stale-context drift, and avoidable retries before usage limits refresh. Forge should improve the amount of useful work completed per context window by making execution state explicit and task-scoped.

Forge is also suitable for content-management workflows when the content lives in structured local files, especially markdown-first repositories such as documentation systems, knowledge bases, editorial systems, and site content collections.

Forge extends to any domain whose work can be expressed through repo artifacts, task packets, and explicit review — including DevOps, VPS provisioning, deployment automation, system administration, reverse-proxy configuration, firewall and SSH hardening, service management, backup planning, containerization, rollback procedures, and local-ops repositories.

Forge supports domain-specific execution through a **contract-driven adapter model**. Adapters are structured, repo-visible domain bridges that tune context selection, validation hints, and review focus for a specific execution domain without changing core workflow semantics. Official adapters are maintained by the Forge project. Custom adapters may be defined locally by users for any domain.

Forge evolves toward an **assistant-guided system** while preserving precision and reliability. Intelligence and advisory behavior are supported but are explicitly separated from execution authority and contract enforcement. Forge should not be characterized as a purely dumb executor — advisory capability is part of its design — but all advisory outputs are proposals until validated, never direct mutations.

### 2.2 Sentinel

`Sentinel` is the companion **verification and reproducibility system** to Forge.

Where Forge asks **"how do we build it?"**, Sentinel asks **"does it work?"**

Sentinel operates as a separate system that feeds structured verification results back into Forge as work inputs. It is a paid product built on top of a stable Forge foundation.

### 2.3 Product System

Together, Forge and Sentinel form a complete AI-assisted development system:

- **Forge** — build, execution, workflow orchestration
- **Sentinel** — verification, reproducibility, issue detection and ingestion

### 2.3a Improvement Boundary

Forge and Sentinel improve the overall system through different loops.

Forge owns workflow improvement:
- detect repeated friction in planning, packetization, review, and closure
- surface token waste, context drift, retry churn, and automation candidates
- turn those findings into proposals, backlog items, or scoped task packets

Sentinel owns verification improvement:
- run automated tests and validation
- search for bugs or failure states
- capture reproducible artifacts from runtime behavior
- turn those findings into structured verification outputs and candidate follow-up work

Neither system should silently rewrite canonical rules.
Improvement remains proposal-driven and gated by explicit review.

### 2.4 Recursive Validation Principle

Forge is intended to be used recursively:

1. to build Forge itself
2. to build Sentinel on top of Forge
3. later, to build additional workflow and verification capabilities using the same disciplined loop

This is a product validation strategy, not just a development preference.

Reason:
- it tests whether Forge's workflow survives real iterative use
- it exposes token waste, context drift, retry churn, and workflow friction early
- it proves whether task packets, review gates, and minimal-context execution hold up under actual product development

Recursive validation is strong evidence, but it is not sufficient on its own.
Forge must also work for projects that were not shaped around Forge from the start.

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
6. Reduce token waste, retry churn, and stale-context drift in agent-driven execution.
7. Preserve human control over canonical project changes.
8. Remain lightweight enough for daily CLI usage.
9. Support content-management workflows that rely on inspectable local files and explicit review.
10. Support domain-specific execution across software, docs, content, DevOps, and operational domains through a contract-driven adapter model.

### 3.2 Secondary Goals

1. Improve repeatability of AI-assisted development work.
2. Reduce prompt sprawl and broad, underspecified build requests.
3. Make project state inspectable through files on disk.
4. Support reuse across multiple projects with similar workflow needs.
5. Increase useful work completed per agent context window.
6. Make markdown-first content workflows easier to structure, review, and close.

---

## 4. Product Non-Goals

The toolkit must not become any of the following in v1:

### 4.1 Not a Coding Agent
The toolkit does not directly design, write, or refactor production code as its core responsibility.

### 4.2 Not a Project Management Suite
It is not a general PM platform, issue tracker, kanban system, or collaboration workspace.

Forge does manage execution structure through phases, backlog items, task packets, review gates, and closure state. However, that workflow management exists to support agent-driven build execution, not to become a generic team planning product.

### 4.3 Not a Multi-User Coordination System
It does not manage permissions, teams, approvals, or multi-user workflow state.

### 4.4 Not a Database-Centric System
It does not require a database, hosted backend, or remote service for core operation.

### 4.5 Not a GUI Product
There is no UI requirement for v1. All primary workflows must succeed through CLI and local files.

### 4.6 Not a Fully Autonomous Builder
The toolkit should not decide broad product direction independently or perform uncontrolled multi-step implementation loops without explicit task structure.

Advisory intelligence is supported — Forge may suggest tasks, phases, roadmap items, and efficiency improvements. However, advisory outputs are proposals, not authoritative decisions. Only validated proposals may affect system state. Forge must never autonomously mutate canonical state, task structure, or system contracts without explicit human approval.

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
- cares about reducing wasted tokens, retries, and context reloads during agent-driven work

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

### 5.3 Agent CLI Assumption
Users of Forge are expected to have access to an agent CLI (e.g. Claude Code or equivalent). The primary workflow surface is agent-driven prompts, not raw CLI commands alone. The CLI handles mechanical operations; the agent handles reasoning, planning, and content generation. Documentation, prompts, and onboarding flows should be designed with this assumption.

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

### 6.6 AdapterProfile

A structured, repo-visible domain bridge that extends Forge workflow behavior for a specific execution domain. An adapter profile specifies context selection hints, validation patterns, review focus, deliverable expectations, and optional model-routing guidance. Adapters extend the workflow; they do not override it.

Two categories of adapter are supported:
- **official adapters** — maintained by the Forge project; shipped as part of the core distribution
- **custom adapters** — defined locally within a repo for domain-specific or private use cases

### 6.7 Proposal Objects
First-class objects representing advisory outputs before they are validated and committed. Proposal objects are distinct from committed work and may not directly alter canonical state.

Types:
- `recommendation` — general advisory suggestion
- `candidate_task` — a proposed task not yet accepted into the backlog
- `candidate_phase` — a proposed phase not yet committed to the plan
- `candidate_roadmap_item` — a proposed roadmap entry not yet accepted

Proposal objects become governed artifacts only after human review and validation. They must not bypass the canonical change flow.

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

### 7.7 Manage Content Repositories
A user organizes markdown-first content systems, documentation sites, editorial repositories, or knowledge bases with explicit review and change flow.

### 7.8 Manage DevOps and System Operations Workflows
A user manages VPS provisioning, deployment setup, reverse-proxy configuration, service management, firewall and SSH hardening, backup planning, monitoring setup, and rollback procedures through repo-local task packets. An adapter profile tunes context selection and validation hints for operational work while preserving the same workflow loop used for software tasks.

### 7.9 Improve Workflow From Real Usage
A user captures workflow friction, token waste, repeated failure patterns, and verification findings so the system can generate better follow-up work without bypassing review.

---

## 8. v1 Scope

### 8.1 In Scope

#### Documentation System
- local markdown/yaml documentation layers
- clear authority separation
- explicit canonical docs
- task packet templates and lifecycle support
- content repositories, documentation sites, and knowledge bases

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

#### Domain Adapter System
- official core adapters for supported domains (`code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`)
- custom user-defined adapters for repo-local or private domains
- adapter-informed context selection, validation hints, and review focus
- adapter contract validation through the manifest and doc system
- DevOps, VPS provisioning, system administration, and local-ops workflows are valid adapter domains

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

8. **Intelligence proposes, validation commits**
   - advisory outputs from agents or intelligence layers are proposals, not authoritative decisions
   - only validated proposals may affect system state
   - this is a foundational constraint, not a style preference

9. **Open-core posture**
   - Forge core functionality should be genuinely useful without artificial limitation
   - paid capabilities derive value from verification, reproducibility, intelligence, and multi-project coordination — not from withholding basic execution capability

10. **Domain-adaptable, workflow-invariant**
    - the workflow loop, packet lifecycle, and review gates remain the same across every domain
    - adapters change execution hints, context selection, and validation focus — not workflow law
    - an adapter that requires changing core workflow semantics has the wrong boundary

---

## 11. Product Ladder

Forge and Sentinel follow an open-core model.

### 11.1 Forge Core — Open
The core Forge system is open and generous. It includes:
- full workflow orchestration (build loop, task packets, lifecycle management)
- context assembly and export
- model routing
- documentation registry and validation
- official core adapters: `code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`
- custom adapter support: users may define repo-local adapter profiles for any domain (DevOps, VPS, local ops, content, or any domain expressible through repo artifacts and task packets)
- prompt library and templates

Forge Core should be fully usable for individual developers and small teams without payment.

### 11.2 Forge Pro — Future Paid Layer
A possible future paid layer covering advanced capabilities:
- intelligence and advisory features (candidate task generation, roadmap suggestions, efficiency analysis)
- multi-project coordination and visibility
- advanced project management features

This is secondary to Sentinel monetization and may not exist in v1 or v2. Basic Forge Core must remain useful and complete without it.

### 11.3 Sentinel — Paid Product
Sentinel is a paid verification and reproducibility system. Monetization is based on:
- automated testing and validation
- reproducible artifact generation
- bug detection and issue ingestion
- observability and workflow intelligence
- structured issue feedback into Forge as work inputs

Sentinel derives value from what it adds, not from limiting Forge.

---

## 12. Success Criteria

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

## 13. Scope Boundaries for Downstream Decisions

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
