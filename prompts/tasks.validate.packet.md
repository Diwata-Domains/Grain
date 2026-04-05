# Validate Task Packet

Validate a single task packet against the packet contract and current workflow rules.

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
* docs/canonical/data_contracts.md

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* context.md
* plan.md
* deliverable_spec.md
* results.md if present
* handoff.md if present

---

## Step 2 - Validate the Packet

Check:

* required packet files are present
* task metadata is complete and well-formed
* packet status matches the current state
* phase and task ID align with the folder name
* deliverable_spec.md is explicit enough to judge completion
* context.md lists only the minimum required materials
* plan.md matches the task scope
* no canonical or workflow conflict is hidden

If the packet is missing required structure, identify the smallest fix needed.

---

## Step 3 - Assess Readiness

Determine whether the packet is:

* ready for implementation
* ready for review
* blocked
* malformed and needs correction before use

If the packet is blocked, state the blocking issue and the next file that should change.

---

## Constraints

* do not generate code
* do not modify files directly
* do not broaden scope beyond one packet
* do not silently repair canonical conflicts

---

## Output

Return ONLY:

1. packet validated
2. issues found
3. required fixes
4. readiness

No explanation.
