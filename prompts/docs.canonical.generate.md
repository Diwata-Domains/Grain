# Canonical Docs Generation Prompt

Generate canonical reference documents for this project.

---

## Project Context

Project Name: Forge

Purpose:
CLI toolkit for structuring AI-assisted development workflows.

Key features:

* task packet system
* doc authority system
* build loop enforcement
* model-agnostic execution

Constraints:

* CLI-first
* filesystem-based
* single-user
* minimal context loading
* human approval for canonical changes

---

## Required Documents (ONLY THESE)

1. docs/canonical/product_scope.md
2. docs/canonical/architecture.md
3. docs/canonical/workflow_spec.md

---

## Requirements

For each document:

### Purpose

* define what it governs
* define what it does NOT cover

### Implementation-Usable

* include concrete structures
* define flows and rules clearly

### No Overlap

* each doc has distinct responsibility

### Consistent Terminology

* task packets
* model classes
* doc layers
* workflow stages

### Agent-Friendly

* structured headings
* easy to reference
* minimal narrative

---

## Additional Output

### Authority Summary

* authority level
* override rules

### Dependencies

* how docs relate
* read order by scenario

### Task-to-Doc Mapping

Examples:

* CLI work → architecture.md
* task packets → workflow_spec.md
* scope validation → product_scope.md

---

## Rules

* do not generate extra docs
* do not include working/runtime docs
* avoid over-engineering

---

## Output

1. product_scope.md
2. architecture.md
3. workflow_spec.md

Then:
4. authority summary
5. dependencies
6. task mapping
