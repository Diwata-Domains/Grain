# Classify New Feature or Idea

You are classifying a newly introduced feature or idea and determining where it belongs in the project workflow.

## Objective

Determine whether the feature should:

* be added to the current phase backlog
* be added to a future roadmap
* be turned into a change proposal
* be deferred or ignored

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md

* docs/runtime/docs_index.md

* docs/working/implementation_plan.md

* docs/working/backlog.md

* docs/working/current_focus.md

* docs/working/open_questions.md

* docs/working/change_proposals.md

* docs/working/future_roadmap.md if present

* docs/canonical/product_scope.md

* docs/canonical/architecture.md
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to classifying the feature

---

## Step 2 — Analyze the Feature

For the provided feature:

* restate it clearly
* identify what problem it solves
* identify which part of the system it affects
* determine whether it changes:

  * architecture
  * workflow rules
  * data contracts
  * CLI behavior
  * execution patterns

---

## Step 3 — Classification Decision

Classify the feature into ONE of the following:

### A — Current Phase Backlog

Use if:

* it fits the current phase goals
* it is small and implementable
* it does not disrupt phase structure
* it does not require redefining canonical rules

### B — Future Roadmap

Use if:

* it is a larger capability
* it is not required for current phase success
* it would expand scope significantly
* it depends on later phases

### C — Change Proposal Required

Use if:

* it modifies canonical behavior
* it affects architecture, workflow, or contracts
* it changes how the system is defined, not just implemented

### D — Defer or Ignore

Use if:

* it is unclear or low value
* it duplicates existing behavior
* it is premature optimization

---

## Step 4 — Placement Instructions

Provide explicit instructions for what to do next:

* if backlog → where in backlog and which phase
* if roadmap → how to add it to future_roadmap.md
* if proposal → what kind of proposal should be created
* if defer → how to record or discard it

---

## Step 5 — Scope Guidance

If the feature is accepted (backlog or roadmap):

* suggest rough scope boundaries
* suggest whether it should later be split into multiple tasks
* identify any dependencies or prerequisites

---

## Constraints

* DO NOT modify files directly
* DO NOT generate task packets
* DO NOT approve canonical changes
* DO NOT expand scope beyond the feature itself

---

## Output

Return ONLY:

1. feature restatement
2. classification (A, B, C, or D)
3. reasoning
4. placement instructions
5. scope guidance

No explanation.
