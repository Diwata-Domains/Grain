# Review Handoff

Check handoff artifacts for a packet that is approaching closure.

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

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* deliverable_spec.md
* results.md if present
* handoff.md if present

---

## Step 2 - Review the Handoff

Check whether the handoff artifacts clearly state:

* what was completed
* what remains open
* any blockers or follow-up items
* what the next owner needs to know

---

## Step 3 - Assess Readiness

Determine whether the handoff is:

* complete
* needs fixes
* blocked
* unnecessary for this packet

---

## Constraints

* do not generate code
* do not modify files directly
* do not invent missing completion details

---

## Output

Return ONLY:

1. handoff issues
2. required fixes
3. optional improvements
4. handoff readiness

No explanation.
