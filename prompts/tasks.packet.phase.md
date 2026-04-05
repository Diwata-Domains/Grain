# Generate Phase Task Packet Plan

You are generating the task packet plan for the current phase of this project.

## Objective

Identify the tasks required for the current phase and produce a structured, ordered task plan for the phase.

This is not for generating all full task packets yet.

It is for:

* identifying the tasks for the phase
* ordering them correctly
* defining scope boundaries
* identifying likely dependencies
* preparing for later one-at-a-time task packet generation

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

* docs/canonical/product_scope.md

* docs/canonical/architecture.md

* docs/canonical/workflow_spec.md

Do not read unrelated task folders unless current_focus.md explicitly references them.

## Step 2 — Identify Current Phase

Determine the active phase from:

* current_focus.md
* implementation_plan.md
* backlog.md

Use the current phase defined in working docs.

Do not invent a new phase.

## Step 3 — Select Phase Tasks

From backlog.md, identify the tasks that belong to the current phase.

For each selected task:

* keep it concrete
* keep it small enough that it could later become a single task packet
* keep it aligned with canonical docs
* do not invent major new tasks
* do not merge unrelated tasks

If a backlog item is too large for one future packet, mark it as needing split before execution.

## Step 4 — Order the Tasks

Create the recommended execution order for the current phase.

For each task, include:

* task name
* objective
* why it belongs in this phase
* dependencies
* likely files or areas affected
* recommended model class
* whether it is ready for immediate packet generation or should wait

## Step 5 — Identify Packetization Guidance

For the phase as a whole, identify:

* which tasks should be packetized first
* which tasks depend on previous implementation
* which tasks may need human clarification before packet generation
* any backlog items that should be split or deferred

## Step 6 — Update Backlog

For each task in the current phase, update its entry in `docs/working/backlog.md` to include:

* **Files:** likely files or areas affected
* **Model:** recommended model class (`open_model`, `frontier_model`, or `reviewer_model`)
* **Dependencies:** other tasks this depends on
* **Ready:** `yes`, `after <task>`, or `blocked — <reason>`

Only update the entries for the current phase.
Do not change task status.
Do not modify other phases.

## Constraints

* DO NOT generate full task packets
* DO NOT generate code
* DO NOT modify canonical docs
* DO NOT skip ahead to future phases
* DO NOT invent new architecture

## Output

Return ONLY:

1. current phase identified
2. ordered phase task plan
3. tasks ready for immediate packet generation
4. tasks that should wait
5. backlog items that need split, clarification, or deferral
6. confirmation that backlog has been updated

No explanation.
