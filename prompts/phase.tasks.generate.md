# Generate Initial Task Slice For Active Phase

Generate the initial backlog task slice for the current phase after the phase has been defined but before execution starts.

Metadata:
- scope: phase
- stage: generate_tasks
- recommended_model_class: frontier_model
- escalation_model_class: reviewer_model

## Objective

Take a newly defined phase and turn it into a concrete, ordered, executable backlog slice.

Use this when:
- a new phase exists in `implementation_plan.md`
- `current_focus.md` points to that phase
- the phase does not yet have usable backlog tasks

Do not generate task packets here.
Do not implement anything here.

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
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to task generation

Read only the recent phase/task artifacts needed to understand the handoff into the new phase.

---

## Step 2 — Identify The Active Phase

Determine the active phase from:

* current_focus.md
* implementation_plan.md
* backlog.md

Use the phase already defined in working docs.
Do not invent a new phase.

---

## Step 3 — Expand The Phase Into Tasks

Generate a concrete task slice for the active phase.

For each task:

* keep it implementable
* keep it small enough for one future task packet
* keep it aligned with canonical docs
* keep dependencies explicit
* assign a likely file set
* assign a recommended model class
* assign a clear readiness rule

If a likely task is still too broad:

* split it now in the backlog
* prefer the smallest valid first slice
* sequence later slices explicitly

If a required task depends on unresolved questions:

* keep the task concrete
* mark it blocked or `after <decision>`
* do not hide the dependency

---

## Step 4 — Update Working Docs

Update:

* docs/working/backlog.md
* docs/working/current_focus.md
* docs/working/implementation_plan.md only if the phase deliverables or sequencing notes need clarification after task generation

Do not modify canonical docs.
Do not generate packets.

---

## Step 5 — Prepare Execution Entry

Identify:

* which task is first and ready now
* which tasks should wait
* which tasks are blocked by questions or proposals
* whether the phase is now ready for continuous `task.plan.next` / `task.execute` use

---

## Output

Return ONLY:

1. current phase identified
2. generated backlog slice
3. first ready task
4. tasks that should wait or remain blocked
5. working-doc files updated

No explanation.
