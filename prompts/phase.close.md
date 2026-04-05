# Close Current Phase

You are closing the current phase of this project.
This is phase-level only; do not use it for individual task closure.

Metadata:
- scope: phase
- stage: close
- recommended_model_class: reviewer_model

## Objective

Close the current phase if it is actually ready, update working documents to reflect the completed phase, and prepare the project for the next phase or next focus area.

## Step 1 — Read Files

Read:

* docs/working/workflow_metrics.md

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

* docs/working/current_task.md

* docs/canonical/product_scope.md

* docs/canonical/architecture.md

* docs/canonical/workflow_spec.md

Read the task folders relevant to the current phase.

At minimum, from each relevant task folder if present, read:

* task.md
* results.md
* handoff.md

Read the implementation artifacts and changed files relevant to those tasks.

## Step 2 — Confirm Closure Eligibility

Determine whether the current phase is actually ready to close.

A phase is ready to close only if:

* its key planned deliverables are complete
* major blockers are either resolved or explicitly recorded
* remaining tasks are either complete, deferred intentionally, or moved appropriately
* working docs can be updated without hiding unresolved issues
* no major unrecorded canonical conflict exists

If the phase is not ready, do not close it.

Instead, return what remains and the recommended status.

## Step 3 — Classify System Improvements

Identify system-level improvements exposed by the closing phase.

Use only these buckets:

* `fix_now`
  * workflow bugs or drift that should be corrected before the next task or next phase begins
* `batch_next_phase`
  * repeated friction, validator ideas, prompt cleanup, or ergonomic improvements worth carrying forward
* `ignore`
  * one-off noise or issues not worth system change

Rules:

* do not create backlog items unless the work is already concrete and scoped
* route unresolved decisions to `open_questions.md`
* route canonical or runtime authority gaps to `change_proposals.md`

## Step 4 — Generate Working Doc Updates

If the phase is ready to close, generate updated contents or targeted patch updates for:

* docs/working/implementation_plan.md
* docs/working/backlog.md
* docs/working/current_focus.md
* docs/working/open_questions.md
* docs/working/change_proposals.md
* docs/working/current_task.md

### Update rules

#### implementation_plan.md

* reflect completed phase status
* identify next phase clearly
* preserve lightweight sequencing

#### backlog.md

* mark completed tasks appropriately
* keep unresolved tasks if they still matter
* move deferred or follow-up work into the correct place
* do not invent major new work unless strongly implied by completed implementation

#### current_focus.md

* shift focus to the next active phase or next immediate priority
* keep concise and actionable

#### open_questions.md

* remove resolved questions
* keep unresolved questions that still matter
* add any newly surfaced unresolved issues

#### change_proposals.md

* add proposal entries only where implementation revealed real canonical mismatch
* do not modify canonical docs directly

#### current_task.md

* if the current task is complete and the phase is closing, set:

# Current Task

Task ID: none
Task Path: none
Status: unset

* if a specific task must remain active into the next phase, reflect that explicitly

## Step 5 — Update Workflow Metrics

Update `docs/working/workflow_metrics.md` with the closing phase's metrics.

For the closing phase, record:

* **Tasks completed:** count of tasks reaching `done` status
* **Blocked tasks:** count of tasks ending in `blocked` or deferred with explicit reason
* **Prompt runs:** total prompt invocations during the phase (packet generation + implementation + review + close)
* **Avg prompt runs per completed task:** prompt runs ÷ completed tasks
* **Manual interventions:** count of human edits, approvals, or corrections outside normal prompt flow
* **First-pass success rate:** tasks or tests that passed without rework on first attempt
* **Rework count:** number of implementations that required a fix after initial attempt
* **Drift incidents:** number of times implementation diverged from canonical docs and required correction
* **Phase duration:** session identifier or date range

Also update the **Notes** section for the closing phase:

* What felt efficient
* What created friction
* What to tighten next phase
* `Fix now`
* `Batch next phase`
* `Ignore`

Update the **Aggregate** section totals.

Do not modify prior phase entries unless correcting a clear factual error.

## Step 6 — Phase Close Summary

Generate a concise phase close summary including:

* phase closed
* what was completed
* unresolved carryover items
* whether canonical proposals were created
* what should happen next

## Step 7 — Readiness for Next Step

Determine one of:

* ready for next task in next phase
* ready for next phase planning
* human review required before continuing

## Constraints

* DO NOT generate code
* DO NOT generate the next task packet
* DO NOT modify canonical docs directly
* DO NOT pretend the phase is complete if meaningful gaps remain
* DO NOT erase unresolved issues

## Output

Return ONLY:

1. phase closure decision
2. system improvements:
   * fix_now
   * batch_next_phase
   * ignore
3. updated contents or targeted updates for working docs
4. updated workflow_metrics.md for the closing phase
5. phase close summary
6. next-step readiness:

   * next task
   * next phase planning
   * human review required

No explanation.
