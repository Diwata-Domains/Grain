# Review Summary

Produce a structured summary of the active packet for final inspection.

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
* any canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to the active packet

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* deliverable_spec.md
* results.md if present
* handoff.md if present

---

## Step 2 - Summarize State

Summarize:

* packet identity
* current status
* deliverable state
* user review state
* verification state
* unresolved blockers
* review findings
* likely next status

---

## Constraints

* do not generate code
* do not modify files directly
* do not expand scope

---

## Output

Return ONLY:

1. packet state
2. deliverable state
3. blockers
4. next status recommendation

No explanation.
