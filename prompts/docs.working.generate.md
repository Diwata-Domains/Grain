# Working Docs Generation Prompt

Generate execution-layer working documents.

---

## Inputs

Use canonical docs:

* product_scope.md
* architecture.md
* any additional project-specific canonical docs that the repo actually needs

---

## Required Documents

1. docs/working/implementation_plan.md
2. docs/working/backlog.md
3. docs/working/current_focus.md
4. docs/working/open_questions.md
5. docs/working/change_proposals.md

---

## Requirements

### Derived Only

* must align with canonical docs
* no new scope or architecture

### Execution-Focused

* what to build
* in what order

### Clear Separation

* plan vs backlog vs focus vs questions

### Agent-Friendly

* structured
* concise
* actionable

---

## Document Instructions

### implementation_plan.md

* phases (4–6 max)
* goals per phase
* dependencies

---

### backlog.md

* tasks grouped by phase
* each task concrete
* include:

  * name
  * description
  * status (draft)

---

### current_focus.md

* current phase
* immediate goals
* constraints
* what NOT to do

---

### open_questions.md

* unresolved decisions
* why they matter

---

### change_proposals.md

Template only:

* title
* affected docs
* reason
* summary
* impact

---

## Additional Output

### Task Readiness Check

* is system ready to start build loop?

### First Task Suggestion

* name
* objective
* files
* model class

---

## Rules

* no canonical changes
* no over-engineering
* keep lightweight

---

## Output

1. implementation_plan.md
2. backlog.md
3. current_focus.md
4. open_questions.md
5. change_proposals.md

Then:
6. readiness check
7. first task suggestion
