# Workflow Initialization Prompt

Create the documentation and execution system for a software project.

---

## Project Overview

Project Name: Forge

Purpose:
A CLI-first toolkit that structures and manages AI-assisted software development workflows.

It enforces:

* Building Workflow (full lifecycle)
* Build Loop (iterative execution)
* separation of canonical, working, runtime, and task packet layers
* model-agnostic execution (open_model, frontier_model, reviewer_model)

---

## Constraints

* CLI-first (no UI for v1)
* filesystem-based
* single-user
* integrates with external coding agents
* minimal context loading
* human approval required for canonical changes

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

---

### 5. Phase Breakdown

Define 4–6 phases with:

* objective
* deliverables
* risks

---

### 6. Initial Backlog

Provide 10–20 concrete tasks grouped by phase.

---

### 7. Model Strategy

Define:

* model classes
* usage rules
* escalation rules

---

### 8. Prompt Library Structure

Define:

* categories
* naming
* mapping to workflow stages

---

### 9. Risks

Identify:

* workflow risks
* agent risks
* doc drift risks
* over-engineering risks

---

## Rules

* avoid duplication
* separate responsibilities clearly
* optimize for CLI agent use
* keep v1 practical

---

## Goal

Output should be directly usable to create repo files and begin execution.
