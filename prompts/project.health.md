# Project Health Review

Review the current health of the Forge-managed project as a system.

Metadata:
- scope: project
- stage: health
- recommended_model_class: reviewer_model

## Objective

Assess project health across execution, planning, docs, and workflow quality without changing project state.

Use this when you want a higher-level health check than a task review or a single phase review.

---

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/context_loading.md
* docs/runtime/agent_profiles.md
* docs/working/current_focus.md
* docs/working/implementation_plan.md
* docs/working/backlog.md
* docs/working/open_questions.md
* docs/working/change_proposals.md
* docs/working/workflow_metrics.md if present
* docs/working/future_roadmap.md if present
* docs/canonical/product_scope.md
* docs/canonical/architecture.md
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that materially affect project health

Read only the recent task packets needed to understand current execution health.

At minimum, if present, read:

* current active task packet
* the most recently closed task packet
* any task packet explicitly referenced by `current_focus.md`

---

## Step 2 — Evaluate Health Areas

Assess these areas:

### Execution Health

Check:
- whether the current phase/task loop is moving cleanly
- blocker rate
- rework rate
- review/close reliability

### Planning Health

Check:
- whether phases, backlog, and current focus align
- whether the next ready work is clear
- whether roadmap, planning docs, and active work are in sync

### Documentation Health

Check:
- authority separation
- working-doc drift
- open questions and proposal hygiene
- whether docs still reflect implementation reality

### Workflow Efficiency Health

Check:
- token-efficiency tracking quality
- prompt/restart overhead
- repeated artifact correction
- unnecessary context or planning churn

### Automation Readiness

Check:
- whether the project is ready for more automation
- whether legal-next-step automation would be safe
- whether state is explicit enough for runners or TUIs

---

## Step 3 — Classify Findings

Classify findings into:

* `healthy`
  - areas operating cleanly
* `watch`
  - areas with non-blocking risk or accumulating debt
* `needs_attention`
  - areas that should be corrected soon
* `blocking`
  - areas that should stop further execution or promotion until resolved

Do not modify files.
Do not invent backlog tasks unless the follow-up is already concrete and obvious.

---

## Output

Return ONLY:

1. overall health status
2. execution health
3. planning health
4. documentation health
5. workflow efficiency health
6. automation readiness
7. top risks
8. recommended next actions

No explanation.
