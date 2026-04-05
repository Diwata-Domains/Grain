# Reconcile Working Docs After Phase

You are reconciling the working documents for this project after a completed phase or batch of implementation work.

## Objective

Update the working docs so they accurately reflect the current state of the repository and the work completed during the phase.

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md

* docs/runtime/docs_index.md

* docs/runtime/docs_manifest.yaml

* docs/runtime/context_loading.md

* docs/runtime/agent_profiles.md

* docs/working/implementation_plan.md

* docs/working/backlog.md

* docs/working/current_focus.md

* docs/working/open_questions.md

* docs/working/change_proposals.md

* docs/canonical/product_scope.md

* docs/canonical/architecture.md

* docs/canonical/workflow_spec.md

Read the task folders relevant to the completed phase or recent batch of work.

At minimum, read from each relevant task folder if present:

* task.md
* results.md
* handoff.md

Read the repository changes relevant to those tasks.

## Step 2 — Compare Docs to Reality

Determine whether the working docs accurately reflect:

* what has been completed
* what remains in backlog
* what the current focus should be next
* what unresolved questions remain
* whether any canonical change proposals should be recorded

Do not infer new product scope.

Do not redefine architecture.

If implementation appears to conflict with canonical docs, do not “fix” this by changing working docs silently. Instead, record it as an open question or change proposal.

## Step 3 — Update Working Docs

Generate updated contents or targeted patch updates for:

* docs/working/implementation_plan.md
* docs/working/backlog.md
* docs/working/current_focus.md
* docs/working/open_questions.md
* docs/working/change_proposals.md

### Rules for each file

#### implementation_plan.md

* reflect actual phase progress
* update sequencing only if implementation reality justifies it
* keep phases clear and lightweight

#### backlog.md

* mark completed tasks appropriately
* keep remaining tasks ordered logically
* do not invent major new work unless clearly implied by completed implementation

#### current_focus.md

* update to the next active phase or next immediate focus
* keep short and actionable

#### open_questions.md

* include unresolved implementation/design questions only
* remove resolved items if appropriate

#### change_proposals.md

* add proposals only if repo changes revealed a real mismatch with canonical docs
* do not modify canonical docs directly

## Step 4 — Readiness Assessment

Determine whether the project is ready for:

* the next task in the current phase
* the next phase
* or a human review before proceeding

## Constraints

* DO NOT modify canonical docs directly
* DO NOT generate new task packets
* DO NOT generate code
* DO NOT rewrite working docs unnecessarily
* DO NOT hide drift between implementation and canonical docs

## Output

Return ONLY:

1. updated contents or targeted updates for working docs
2. a short readiness assessment:

   * continue current phase
   * move to next phase
   * human review needed

No explanation.
