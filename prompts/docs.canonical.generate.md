# Canonical Docs Generation Prompt

Metadata:
- scope: project
- stage: initialize
- recommended_model_class: frontier_model

Generate canonical reference documents for a project using the Forge document authority model.

---

## How to Use This Prompt

Fill in the **Project Context** section below before running. The agent will use this to generate `product_scope.md`, `architecture.md`, and `workflow_spec.md` tailored to the project.

If context is ambiguous or incomplete, ask clarifying questions before generating.

---

## Project Context

<!-- Replace all values below before running -->

**Project Name:** [Your project name]

**Purpose:**
[What this project does and why it exists. Be specific.]

**Key Capabilities:**
[Bullet list of main features or system responsibilities]

**Constraints:**
[Technical, scope, and operational constraints — e.g. CLI-first, no database, single-user, human approval for canonical changes]

**Tech Stack:**
[Languages, frameworks, platforms — used to generate architecture appropriate to the project]

**Adapters:**
[Which Forge adapters apply — backend_adapter, frontend_adapter, docs_adapter, spreadsheet_adapter, or other]

**v1 Scope:**
[What is in and out of scope for v1]

---

<!-- Reference example — do not modify below this line -->
<!-- EXAMPLE (Forge):
Project Name: Forge
Purpose: CLI-first toolkit for structuring AI-assisted development workflows.
Key Capabilities: task packet system, doc authority system, build loop enforcement, model-agnostic execution, context assembly and export
Constraints: CLI-first, filesystem-based, single-user, minimal context loading, human approval for canonical changes
Tech Stack: Python, Click CLI, Markdown, YAML
Adapters: backend_adapter, docs_adapter
v1 Scope: In — local CLI, filesystem state, task packets, doc validation, context export. Out — GUI, hosted service, multi-user, autonomous execution.
-->

---

## Required Documents

Generate ONLY these three:

1. `docs/canonical/product_scope.md`
2. `docs/canonical/architecture.md`
3. `docs/canonical/workflow_spec.md`

---

## Requirements

### Each document must

* define what it governs
* define what it does NOT cover
* include concrete structures and rules, not just narrative
* have no overlap in responsibility with the other two docs

### product_scope.md must include

* product definition and positioning
* primary and secondary goals
* non-goals
* target user and assumed capabilities (including agent CLI assumption)
* core product objects
* core use cases
* v1 scope (in / conditionally in / out)
* product constraints
* product principles — including the open-core posture and the intelligence/proposal rule
* product ladder if applicable (core free tier, pro tier, paid companion systems)
* success criteria
* scope boundaries

### architecture.md must include

* architectural overview with layered subsystem model:
  - Runtime Core (execution, packet lifecycle, contract enforcement, state transitions)
  - Advisory / Intelligence Layer (proposals only — never direct state mutation)
  - Telemetry / Observability Layer (metrics, signals, efficiency data)
  - Review / Gate Layer (validates proposals before commit)
* foundational authority rule: intelligence may generate proposals; only validated proposals may affect system state
* core architectural principles including constrained autonomy model (observe → suggest → draft → constrained commit)
* primary system components appropriate to the project
* repository structure
* internal module boundaries
* core data structures including Proposal Object
* architectural flows including advisory proposal flow (propose → validate → commit)
* architectural constraints including no unvalidated advisory mutation
* integration boundary definition
* architecture decisions for v1

### workflow_spec.md must include

* workflow model (Building Workflow + Build Loop)
* workflow stages
* build loop steps
* task packet lifecycle and states
* required packet contents
* context loading rules
* model class usage in workflow
* workflow authority handling
* completion requirements
* failure and recovery behavior
* practical v1 rules

### Consistent terminology across all three docs

* task packets
* model classes (open_model, frontier_model, reviewer_model)
* doc layers (canonical, working, runtime, task-local)
* workflow stages
* proposal objects (recommendation, candidate_task, candidate_phase, candidate_roadmap_item)
* propose → validate → commit flow

### Agent-friendly formatting

* structured headings
* scannable, referenceable
* minimal narrative prose

---

## Additional Output

### Authority Summary

* authority level for each doc
* override rules between docs

### Dependencies

* how the three docs relate to each other
* read order by scenario (execution, review, canonical change, onboarding)

### Task-to-Doc Mapping

Provide examples mapping workflow activities to the doc that governs them.

---

## Rules

* do not generate working docs, runtime docs, or task packets in this prompt
* do not include project-specific implementation details in canonical docs
* do not over-engineer — v1 docs should be practical and immediately usable
* all generated docs are draft until human confirms them as canonical
* if any project context is too vague to generate a good doc, surface the ambiguity rather than guessing

---

## Output

1. `product_scope.md`
2. `architecture.md`
3. `workflow_spec.md`

Then:

4. Authority summary
5. Dependencies
6. Task-to-doc mapping
