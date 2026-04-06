# Workflow Initialization Prompt

Metadata:
- scope: project
- stage: initialize
- recommended_model_class: frontier_model

Create the documentation and execution system for a software project using the Forge workflow.

---

## How to Use This Prompt

Fill in the **Project Context** section below before running. Replace every placeholder value with your project's specifics. The agent will use this context to generate the full canonical doc set, working docs, manifest, initial backlog, and open questions.

If any context is unclear or missing, the agent should ask follow-up questions before generating output — do not guess at project constraints.

---

## Project Context

<!-- Replace all values below before running -->

**Project Name:** [Your project name]

**Purpose:**
[What this project does and why it exists. 2–4 sentences. Be specific — vague descriptions produce vague docs.]

**Key Capabilities:**
[Bullet list of main features, focus areas, or what the system will do]

**Constraints:**
[What the project must or must not do — technical, scope, or operational. Examples: CLI-first, no backend service, single-user, human approval required for canonical changes]

**Target User:**
[Who uses this system, in what context, and what they already know]

**Tech Stack:**
[Languages, frameworks, platforms, tools — e.g. Python, Rust, TypeScript, React, Tauri, Storybook, Excel. Used to generate appropriate adapter config and manifest structure]

**Adapters Needed:**
[Which Forge adapters apply — e.g. backend_adapter, frontend_adapter, docs_adapter, spreadsheet_adapter. List all that apply.]

**v1 Scope Boundaries:**
[What is explicitly in scope for v1, and what is explicitly out. Be concrete.]

**Known Open Questions:**
[Any unresolved decisions that should be logged as open questions at init time — e.g. "deployment target TBD", "auth strategy not decided". Leave blank if none.]

---

<!-- Reference example — do not modify below this line -->
<!-- EXAMPLE (Forge): 
Project Name: Forge
Purpose: CLI-first toolkit that structures and manages AI-assisted software development workflows. Enforces a building workflow, build loop, and separation of canonical/working/runtime/task-packet layers.
Key Capabilities: task packet system, doc authority system, build loop enforcement, model-agnostic execution, context assembly and export
Constraints: CLI-first (no UI for v1), filesystem-based, single-user, integrates with external coding agents, minimal context loading, human approval required for canonical changes
Target User: Single developer or technical operator using external AI coding agents, values inspectable files over opaque orchestration
Tech Stack: Python, Click CLI, Markdown, YAML
Adapters Needed: backend_adapter, docs_adapter
v1 Scope Boundaries: In scope — local CLI, filesystem state, task packets, doc validation, context export. Out of scope — GUI, hosted service, multi-user, autonomous execution.
Known Open Questions: None
-->

---

## Required Output

### 1. Documentation System

Define:

* canonical docs
* working docs
* runtime docs
* task packet system

For each:

* name
* purpose
* authority
* edit permissions

---

### 2. docs_manifest.yaml

Provide full structure:

* canonical
* working
* runtime
* tasks
* rules

Include adapter entries appropriate to the project's tech stack.

---

### 3. docs_index.md

Define:

* hierarchy
* read order
* edit permissions

---

### 4. PROJECT_RULES.md

Define:

* execution rules
* authority rules
* context rules
* completion rules
* CLI implementation rules (placeholder command behavior)
* the foundational intelligence rule: intelligence may generate proposals; only validated proposals may affect system state

---

### 5. agent_profiles.md

Define model classes appropriate to the project:

* open_model — use cases, avoid cases, preferred models, escalation targets
* frontier_model — use cases, avoid cases, preferred models, escalation targets
* reviewer_model — use cases, avoid cases, preferred models, escalation targets

---

### 6. Phase Breakdown

Define 4–6 phases with:

* objective
* deliverables
* risks

Ground phases in the project's stated scope and tech stack.

---

### 7. Initial Backlog

Provide 10–20 concrete tasks grouped by phase.

Tasks must be:

* implementable
* scoped to one coherent unit of work
* grounded in the project's stated capabilities and constraints

---

### 8. Initial Open Questions

Log any known open questions from the Project Context plus any the agent identifies during generation. Format as `open_questions.md` entries with status `decision_needed`.

---

### 9. Model Strategy

Define:

* model classes and their workflow roles
* escalation rules
* how model class maps to workflow stages for this project type

---

### 10. Prompt Library Structure

Define:

* categories
* naming convention
* mapping to workflow stages

---

### 11. Risks

Identify:

* workflow risks
* agent risks
* doc drift risks
* over-engineering risks
* risks specific to the project's tech stack or domain

---

## Rules

* ask follow-up questions if project context is ambiguous before generating
* avoid duplication across docs
* separate responsibilities clearly
* optimize for agent CLI use — users will have an agent CLI (e.g. Claude Code)
* keep v1 practical — do not generate aspirational complexity the project cannot yet support
* all generated docs are draft until human review confirms them as canonical

---

## Goal

Output should be directly usable to create repo files and begin execution. A developer should be able to take this output, run `forge init`, write the generated files, and start executing task packets in the same session.
