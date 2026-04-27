# Resolve Open Question

You are analyzing an open question that is blocking or affecting project execution.

## Objective

Analyze one specific open question, recommend a resolution, determine whether it requires a canonical change proposal, and identify the updates needed to unblock work.

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md

* docs/runtime/docs_index.md

* docs/runtime/docs_manifest.yaml

* docs/runtime/context_loading.md

* docs/runtime/agent_profiles.md

* docs/working/open_questions.md

* docs/working/implementation_plan.md

* docs/working/backlog.md

* docs/working/current_focus.md

* docs/working/change_proposals.md

* docs/canonical/product_scope.md

* docs/canonical/architecture.md
* any additional canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to the selected question

Read only the specific question being resolved and only the canonical/working docs relevant to that question.

## Step 2 — Analyze the Question

For the selected question:

* restate the question clearly
* identify why it matters
* identify which tasks or phase work are blocked or affected
* evaluate the listed options
* recommend the best v1 decision

Prefer:

* simplicity
* minimal implementation burden
* consistency with current canonical docs
* low-friction execution

## Step 3 — Determine Resolution Path

Determine whether the recommended resolution should be handled as:

* working-doc update only
* change proposal required
* defer to later phase

If canonical docs, contracts, or workflow rules are affected, require a change proposal.

## Step 4 — Identify Required Updates

List the specific files that should be updated if the recommendation is accepted.

Possible targets:

* open_questions.md
* change_proposals.md
* canonical docs
* working docs
* backlog/current focus

## Step 5 — Unblock Guidance

State how the blocked task(s) should proceed once the resolution is accepted.

## Constraints

* DO NOT approve the decision on behalf of the human
* DO NOT modify canonical docs directly
* DO NOT generate code
* DO NOT resolve unrelated questions

## Output

Return ONLY:

1. question analyzed
2. recommended resolution
3. reasoning
4. resolution path:

   * working-doc update only
   * change proposal required
   * defer
5. files to update
6. blocked tasks affected
7. unblocking guidance

No explanation.
