# Results — TASK-0196

## Status
done — 2026-06-11

## Deliverable
`docs/canonical/suggest_spec.md` — full `grain suggest` command group spec.

## Key Decisions

**Two types:** `pick-up` (existing ready task) and `new-task` (net-new, derived from signals). Type-specific quality bars applied before surfacing to operator.

**Signal priority:** (1) Ready tasks in active phase, (2) blocking OQs, (3) high-severity tooling notes, (4) git history (avoid suggesting done work), (5) phase boundary (all tasks done → suggest phase close).

**Proposal persistence:** `docs/working/proposals/SUG-YYYYMMDD-NNN.md` — file-backed, committable, inspectable. Lifecycle: pending → accepted | dismissed | expired.

**Deterministic engine:** No LLM inference in suggestion generation — all signal reads and quality bar checks are pure string/structure operations. `grain suggest` works without an agent present.

**`new-task` accept always prompts:** Even with `--no-confirm`, new-task acceptance shows the proposed task.md and requires confirmation before writing. Silent task creation is a workflow violation.

**`grain suggest --from-audit`:** Convenience command combining `grain docs audit` findings with `grain suggest` new-task generation.

## Files Changed
- `docs/canonical/suggest_spec.md` — created
- `tasks/P30-T07-TASK-0196/task.md` — status set to done
