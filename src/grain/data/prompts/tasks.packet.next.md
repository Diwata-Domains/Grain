# Generate Next Task Packet

You are generating the next task packet for this project.

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

* docs/working/current_task.md

* docs/canonical/product_scope.md

* docs/canonical/architecture.md
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to packet generation

* templates/tasks/task_packet.md

If `docs/working/current_task.md` points to an existing task, read that task folder only to understand what was just completed or what is currently in progress.

At minimum, if present, read:

* task.md
* results.md
* handoff.md

Do not read unrelated task folders.

---

## Step 2 — Select the Next Task

From backlog.md, choose ONE task that:

* belongs to the current phase
* is not completed
* logically follows the current task, if one exists
* is concrete and implementable
* is small enough for a single task packet
* helps unblock future work

Do NOT:

* combine multiple backlog tasks
* invent a new task
* skip ahead to future phases
* select a task that depends on unfinished prerequisites

If multiple tasks qualify, choose the simplest valid next task.

---

## Step 3 — Validate the Task

Before generating the packet, confirm:

* the task aligns with canonical docs
* the task does not require redefining architecture or scope
* the task is narrow enough for one packet
* the likely files are limited and reasonable
* acceptance criteria can be stated clearly

If the selected task appears too broad, narrow it to the smallest valid unit that still matches the backlog.

If narrowing would create a new task not represented in the backlog, stop and report that the backlog item should be split in working docs first via `prompts/task.plan.next.md`.

---

## Step 4 — Generate the Task Packet

Using `templates/tasks/task_packet.md`, generate a complete task packet for the selected task.

Use the current task packet contract and fill all required sections.

Keep the packet:

* narrow
* executable
* minimally scoped
* consistent with project rules

List only the files that are likely to change for this task.

Do not generate code.

Do not modify canonical docs.

Do not include unnecessary narrative.

---

## Step 5 — Set the Active Task

After generating the packet, also generate the contents for:

`docs/working/current_task.md`

Use this format exactly:

# Current Task

Task ID: [TASK-ID]
Task Path: tasks/[TASK-ID]/
Status: ready

If the task packet is only draft-quality due to ambiguity, set:
Status: draft

---

## Model Selection Rules

Assign:

* `open_model` if the task is mechanical, repetitive, or low-risk
* `frontier_model` if the task affects structure, CLI behavior, coordination, or has ambiguity
* `reviewer_model` as the review layer

Include short reasoning.

---

## Constraints

* DO NOT generate multiple task packets
* DO NOT generate code
* DO NOT expand scope
* DO NOT modify canonical docs
* DO NOT use files outside the listed inputs unless absolutely required by the active task contract
* DO NOT silently reinterpret backlog intent

---

## Output

Return ONLY:

1. the completed task packet
2. the updated contents for `docs/working/current_task.md`

No explanation.
