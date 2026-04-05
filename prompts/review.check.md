# Review Packet

Run review-oriented validation on a single task packet.

---

## Step 1 - Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/context_loading.md
* docs/runtime/agent_profiles.md
* docs/working/current_task.md
* docs/working/current_focus.md
* docs/canonical/workflow_spec.md
* docs/canonical/cli_spec.md

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* context.md
* plan.md
* deliverable_spec.md
* results.md if present
* handoff.md if present

Read the files changed by the task when they are available.

---

## Step 2 - Review the Packet

Check:

* scope adherence
* deliverable_spec coverage
* correctness against canonical docs
* missing files or artifacts
* hidden drift
* obvious edge cases

---

## Step 3 - Decide Status

Determine whether the packet is:

* ready
* needs fixes
* blocked
* unclear due to spec conflict

---

## Constraints

* do not generate code
* do not modify files directly
* do not widen scope
* do not approve missing deliverables

---

## Output

Return ONLY:

1. issues found
2. required fixes
3. optional improvements
4. whether the packet meets done criteria
5. recommended next status

No explanation.
