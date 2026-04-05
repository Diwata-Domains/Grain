# Review Active Task

You are reviewing the active task for this project.

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md

* docs/runtime/docs_index.md

* docs/runtime/docs_manifest.yaml

* docs/runtime/context_loading.md

* docs/runtime/agent_profiles.md

* docs/working/current_focus.md

* docs/working/current_task.md

* templates/tasks/results.md

* templates/tasks/handoff.md

* templates/tasks/task_packet.md

Then read the task folder referenced in `docs/working/current_task.md`.

At minimum, read:

* task.md
* context.md
* plan.md
* deliverable_spec.md
* results.md if present
* handoff.md if present

Read the files changed for the task.

Read only the canonical docs referenced by the active task packet.

## Step 2 — Review Against Task Scope

Check:

* correctness
* consistency with canonical docs
* consistency with the task packet
* missing logic
* edge cases
* overreach beyond scope
* missing documentation updates
* missing follow-up notes
* whether deliverable_spec.md is satisfied
* whether `results.md` and `handoff.md` conform to the current task templates

## Step 3 — Determine Status

Decide whether the task is:

* ready
* needs fixes
* blocked
* unclear due to spec conflict

## Step 4 — Classify Review Follow-Ups

Classify follow-ups explicitly so closeout can apply them without guessing from prose.

Use these buckets:

* `open_questions_to_log`
  * use only for real unresolved decisions or ambiguities that should be recorded in `docs/working/open_questions.md`
* `proposal_candidates_to_log`
  * use only for real canonical or runtime mismatches that should be recorded in `docs/working/change_proposals.md`
* `followups_to_log`
  * use for non-blocking implementation notes, next-task cautions, or handoff items that do not belong in working-layer authority docs

Do not place optional improvements or speculative ideas into `open_questions_to_log` or `proposal_candidates_to_log`.

If a bucket is empty, return `None`.

## Step 5 — Persist Review Intake For Closeout

Update `results.md` directly so the structured review outcome is recorded in the task artifacts.

Create or update `handoff.md` directly so closeout and the next task have a durable handoff artifact.

Follow the structure in:

* `templates/tasks/results.md`
* `templates/tasks/handoff.md`

At minimum, persist:

* review decision
* required fixes
* open questions to log
* proposal candidates to log
* follow-ups to log
* residual risks
* efficiency section retained or updated if the task results omitted it

If `handoff.md` does not exist, create it.

## Output

Return ONLY:

1. issues found
2. required fixes
3. optional improvements
4. whether the task meets definition of done
5. recommended next status for the active task
6. `open_questions_to_log`
7. `proposal_candidates_to_log`
8. `followups_to_log`
9. residual risks
10. files updated
11. summary of persisted review intake

No explanation.
