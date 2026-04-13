# Prompt Index

This directory contains the runnable prompt surface for Grain.

Use these prompts from your agent CLI.
They are workflow entrypoints, not canonical source-of-truth documents.

Higher-authority rules still live in:
- [`docs/runtime/PROJECT_RULES.md`](/Users/barbaricum/ai-build-toolkit/docs/runtime/PROJECT_RULES.md)
- [`docs/runtime/docs_manifest.yaml`](/Users/barbaricum/ai-build-toolkit/docs/runtime/docs_manifest.yaml)
- canonical docs under [`docs/canonical/`](/Users/barbaricum/ai-build-toolkit/docs/canonical)

---

## Recommended Stable Prompt Surface

### Project Bootstrap

[`workflow.init.md`](/Users/barbaricum/ai-build-toolkit/prompts/workflow.init.md)
- compatibility alias that routes to the stable new-project onboarding prompt
- keep only for legacy command habits
- recommended model class: `frontier_model`

[`workflow.onboard.new.md`](/Users/barbaricum/ai-build-toolkit/prompts/workflow.onboard.new.md)
- use for stable new-project onboarding
- question-first intake with explicit adapter-selection inputs
- recommended model class: `frontier_model`

[`project.health.md`](/Users/barbaricum/ai-build-toolkit/prompts/project.health.md)
- use for periodic system/project health review
- checks execution, planning, docs, efficiency, and automation readiness
- recommended model class: `reviewer_model`

---

### Phase Planning

[`phase.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.plan.next.md)
- use when you need to define the next phase or transition slice
- output: next phase structure and candidate backlog slice
- recommended model class: `frontier_model`

[`phase.tasks.seed.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.tasks.seed.md)
- use right after a new phase is defined but before execution begins
- turns a phase definition into its first concrete backlog slice
- recommended model class: `frontier_model`

[`phase.replan.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.replan.md)
- use when the current or next phase shape is wrong
- replans sequencing without starting implementation
- recommended model class: `frontier_model`

[`phase.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review.md)
- use to assess whether the current phase is ready to close
- review only; does not rewrite working docs
- recommended model class: `reviewer_model`

[`phase.review_and_close.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review_and_close.md)
- use when a phase is closeable and you want review + close in one pass
- updates working docs as part of closeout
- recommended model class: `reviewer_model`

[`phase.close.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.close.md)
- use for phase close-only work after review readiness is already known
- recommended model class: `reviewer_model`

---

### Task Planning And Execution

[`task.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.plan.next.md)
- use continuously when you need to:
  - select the next task
  - split a too-broad backlog item
  - add one concrete follow-up task
- do not run it if a ready task already exists
- recommended model class: `frontier_model`

[`task.execute.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.execute.md)
- use to packetize and implement one scoped task
- stops at review; does not self-close
- recommended model class: `open_model`
- escalate to: `frontier_model`

[`task.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.review.md)
- use to review the active task packet and persist structured review intake
- recommended model class: `reviewer_model`

[`task.close.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.close.md)
- use to finalize one reviewed task packet
- updates working docs for explicit review-bundle items when needed
- recommended model class: `open_model`

---

## Typical Workflow

### New Phase

1. [`phase.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.plan.next.md)
2. [`phase.tasks.seed.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.tasks.seed.md)
3. [`task.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.plan.next.md) only when needed
4. [`task.execute.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.execute.md)
5. [`task.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.review.md)
6. [`task.close.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.close.md)

### Existing Active Phase

1. [`task.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.plan.next.md) only when needed
2. [`task.execute.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.execute.md)
3. [`task.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.review.md)
4. [`task.close.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.close.md)

### Health / Review

1. [`project.health.md`](/Users/barbaricum/ai-build-toolkit/prompts/project.health.md)
2. [`phase.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review.md) or [`phase.review_and_close.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review_and_close.md)

---

## Notes

- `prompts/task.*.md` and `prompts/phase.*.md` are the preferred stable names.
- Older `tasks.*` and short alias prompts remain for compatibility in some cases, but they are not the preferred human-facing surface.
- If prompt or workflow-contract docs change mid-conversation, restart the relevant agent conversation before continuing.

---

## Machine-Readable Prompt Surface

`grain prompt show` surfaces the recommended prompt entrypoint for the current repo state without making prompts the source of truth.

```bash
grain prompt show
grain --format json prompt show
```

Output includes: `recommended_prompt`, `model_class`, `scope`, `stage`, `next_action`, `stop_reason`, `blocking_reasons`. Prompts remain execution aids — canonical workflow rules live in the project's declared canonical and runtime docs, not in a single universal filename.
