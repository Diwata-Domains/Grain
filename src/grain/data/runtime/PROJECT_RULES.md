# PROJECT_RULES

## 1. Purpose

These rules govern all agent and tool behavior in this repository.

The project is a CLI-first toolkit for structuring AI-assisted software development workflows. It is a workflow orchestrator, not a coding agent.

---

## 2. Core Operating Rules

1. Respect separation of concerns.
2. Do not merge canonical, working, runtime, and task responsibilities.
3. Load only the minimum context needed for the current task.
4. Execute one scoped task at a time.
5. Prefer patching over rewriting.
6. Do not make silent canonical changes.
7. Preserve model-agnostic behavior.
8. Optimize for clarity, speed, token efficiency, and local filesystem simplicity.
9. **Intelligence may generate proposals. Only validated proposals may affect system state.** Advisory outputs, agent suggestions, and intelligence layer outputs are proposals until explicitly validated and committed. This rule has no exceptions.

---

## 3. Documentation Authority Rules

### Authority order
1. `docs/runtime/PROJECT_RULES.md`
2. `docs/canonical/*`
3. `docs/runtime/docs_manifest.yaml`
4. `docs/runtime/docs_index.md`
5. `docs/working/*`
6. `tasks/*`

### Required behavior
- Higher-authority documents override lower-authority documents.
- Lower-level docs must not redefine higher-level docs.
- If a conflict is detected, stop using the conflicting lower-level statement.
- Record the conflict in the task results or open questions.

### Canonical change rule
- Agents must not directly edit canonical docs.
- Agents may propose canonical changes in:
  - `docs/working/change_proposals.md`
  - `tasks/<task-id>/patches/`
- Canonical changes require explicit human approval.

### Prompt status rule
- Files under `prompts/` and `templates/prompts/` are derived workflow assets, not canonical source-of-truth documents.
- Prompts must operationalize higher-authority docs rather than redefine them.
- If a prompt conflicts with `PROJECT_RULES.md`, canonical docs, runtime docs, working docs, or the active task packet, follow the higher-authority source and record the prompt drift.
- Prompt wording may change for usability without changing product, workflow, or contract truth.
- `prompts/` is the runnable prompt surface.
- `templates/prompts/` is for prompt authoring scaffolds only.

---

## 4. Context Loading Rules

### Default rule
Only load the documents required for the current task.

### Required order
1. Read `PROJECT_RULES.md`
2. Read the current task packet
3. Read only the canonical docs relevant to the task
4. Read working docs only if needed for sequencing, priorities, or blockers

### Prohibited behavior
- Do not load the full repo by default.
- Do not include broad historical context unless required.
- Do not pass unrelated documentation into execution prompts.

### Preferred behavior
- Use the docs manifest to determine relevant sources.
- Use task packets as the primary execution surface.
- Keep execution context narrow and explicit.
- Prefer the smallest valid file set for the current stage so repeated prompts do not pay unnecessary token cost.

### Context freshness rule
- Agents must not assume that prompt, runtime, or workflow-doc changes made mid-conversation are automatically reflected in the active context.
- If any of the following change during an executor, reviewer, closer, or phase-review conversation, restart that conversation before continuing:
  - `prompts/*`
  - `docs/runtime/*`
  - `docs/working/open_questions.md`
  - `docs/working/change_proposals.md`
  - task packet templates or workflow-contract templates
- Prefer starting a new conversation over broad rereads when contract files changed, to avoid stale-context drift.
- Same-conversation continuation is acceptable only when the agent explicitly rereads the changed files and confirms the refreshed contract before proceeding.

### Prompt naming rule
- Prefer `prompts/task.*.md` for task-level workflows.
- Prefer `prompts/phase.*.md` for phase-level workflows.
- Treat short aliases such as `prompts/execute.md`, `prompts/review.md`, and `prompts/close.md` as convenience wrappers, not the stable authority surface.

### Prompt metadata rule
- Stable prompt entrypoints should expose lightweight metadata when useful.
- Preferred metadata fields are:
  - `scope`
  - `stage`
  - `recommended_model_class`
  - `escalation_model_class` when escalation is expected
- Prompt metadata is advisory runtime guidance, not canonical workflow truth.

---

## 5. CLI Implementation Rules

### Placeholder command behavior
Unimplemented CLI commands must not silently succeed.

Before a command is fully implemented, it must either:
- be absent from the command surface entirely, or
- return an explicit not-implemented error with a non-zero exit code

Silent success (exit 0, no output) from a stub is not permitted.

This rule is defined canonically in `docs/canonical/cli_spec.md §5.1`.

---

## 6. Task Execution Rules

### Task unit
- Every implementation action must map to a specific task packet.
- One packet should represent one coherent task.

### Before execution
Confirm:
- scope is defined
- required context is selected
- deliverable is explicit
- dependencies are known
- canonical conflicts are absent or recorded
- if the next backlog item is too broad, split it during planning before packet generation rather than during review or closeout

### During execution
- Follow the packet plan
- Update results with meaningful progress
- Record blockers explicitly
- Do not expand scope without documenting it

### After execution
- Verify deliverable completion
- Record files changed
- Record unresolved issues
- Prepare handoff if review or follow-up is required
- Persist review and closeout intake into task artifacts before final closure
- Record token-efficiency data in task artifacts when the runtime exposes it, and record proxy efficiency data when exact token counts are unavailable
- Route task generation or backlog splitting back into the planning layer rather than doing it implicitly during review or closeout

---

## 8. Completion Requirements

A task is not complete unless all of the following are true:

1. The deliverable defined in `deliverable_spec.md` is satisfied.
2. Outputs conform to relevant canonical docs and contracts.
3. Results are recorded in `results.md`.
4. Any proposed canonical changes are captured as proposals, not direct edits.
5. Remaining blockers or follow-ups are documented.
6. The task can be reviewed without reconstructing hidden context.
7. Review-driven open questions or proposal candidates are either logged in working docs or explicitly recorded as `None` in task artifacts.

### Closeout boundary rule
- Task review and closeout may update task artifacts and working docs.
- They must not modify prompts, runtime workflow docs, or unrelated repository files unless the active task explicitly targets workflow infrastructure.

---

## 9. Patch-Over-Rewrite Policy

Default to targeted changes.

Prefer:
- small diffs
- additive updates
- localized edits
- explicit change reasoning

Avoid:
- unnecessary rewrites
- broad refactors without task scope
- document duplication
- replacing stable structures without justification

---

## 10. Human-in-the-Loop Rules

Human review is required for:
- canonical doc changes
- architecture shifts
- workflow changes
- schema/contract changes
- phase redefinition
- scope expansion

Agents may prepare proposals, not finalize them.

---

## 11. Non-Goals for v1

Do not introduce unless explicitly required:
- GUI interfaces
- database-backed state
- multi-user coordination
- autonomous coding execution
- complex plugin ecosystems
- deeply abstracted orchestration layers

---

## 12. Standard for Good Execution

Good execution is:
- scoped
- reversible
- well-documented
- minimally contextual
- compliant with authority rules
- ready for handoff or review
