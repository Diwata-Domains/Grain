# Generate First Task Packet

You are generating the first task packet for this project.

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

* docs/canonical/product_scope.md

* docs/canonical/architecture.md

* docs/canonical/workflow_spec.md

* templates/tasks/task_packet.md

Do not read any task folders unless they already exist and are explicitly referenced in working docs.

---

## Step 2 — Select the First Task

Choose ONE task that:

* belongs to Phase 1
* establishes foundational structure
* unblocks future tasks
* is concrete and implementable
* is small enough for a single packet

Prefer foundational tasks such as:

* CLI entrypoint
* command registry
* repo scaffold
* config loading
* initial doc/task directory bootstrap

Do NOT:

* choose advanced logic
* choose automation layers
* combine multiple tasks
* skip foundational setup

If multiple tasks qualify, choose the simplest valid foundation task.

---

## Step 3 — Validate

Confirm:

* the task aligns with canonical docs
* the task fits current phase intent
* the task does not require architecture changes
* acceptance criteria can be stated clearly

If unclear, choose the narrowest valid task.

---

## Step 4 — Generate the Task Packet

Using `templates/tasks/task_packet.md`, generate a complete task packet.

Keep it:

* narrow
* executable
* foundational
* consistent with project rules

Do not generate code.

Do not modify canonical docs.

---

## Step 5 — Set the Active Task

Also generate the contents for:

`docs/working/current_task.md`

Use this format exactly:

# Current Task

Task ID: [TASK-ID]
Task Path: tasks/[TASK-ID]/
Status: ready

If the packet is incomplete due to ambiguity, set:
Status: draft

---

## Model Selection Rules

Assign:

* `frontier_model` if the task is structural or affects CLI design
* `open_model` only if the task is purely mechanical
* `reviewer_model` as the review layer

Include short reasoning.

---

## Constraints

* DO NOT generate multiple task packets
* DO NOT generate code
* DO NOT expand scope
* DO NOT modify canonical docs

---

## Output

Return ONLY:

1. the completed first task packet
2. the contents for `docs/working/current_task.md`

No explanation.
