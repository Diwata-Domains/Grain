# Replan Current Or Next Phase

Replan the current or next phase when blockers, completed work, or new constraints make the existing phase shape wrong.

Metadata:
- scope: phase
- stage: replan
- recommended_model_class: frontier_model
- escalation_model_class: reviewer_model

## Objective

Adjust phase structure without letting execution drift silently.

Use this when:
- the current phase is no longer coherent
- the next phase should be split, merged, or resequenced
- repeated task-level blockers show the plan is wrong

---

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
* docs/working/future_roadmap.md
* docs/working/v2_plan.md if present
* docs/working/v2_adapters.md if present
* docs/working/v2_onboarding.md if present
* docs/canonical/product_scope.md
* docs/canonical/architecture.md
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that materially affect replanning

Read the task packets relevant to the replanning trigger.

At minimum, if present, read:

* task.md
* results.md
* handoff.md

---

## Step 2 — Diagnose Why Replanning Is Needed

Identify whether the problem is:

* bad phase scope
* wrong task order
* missing dependencies
* a now-ready roadmap item
* unresolved decision pressure

Do not use replanning to hide implementation mistakes or bypass review.

---

## Step 3 — Replan

Update only what is needed:

* current phase definition
* next phase definition
* backlog sequencing
* carryover or deferred items
* current focus

Rules:

* preserve stable completed work
* keep one active phase at a time
* do not create implementation packets in this prompt
* route canonical changes through proposals

---

## Output

Return ONLY:

1. replanning trigger identified
2. phase changes made
3. working-doc files updated
4. carryover, deferred, or newly sequenced items
5. next planning or execution step

No explanation.
