# Results — TASK-0197

## Status
done — 2026-06-11

## Deliverable
`docs/canonical/enforcement_spec.md` — 6-layer enforcement model spec.

## Key Decisions

**Layer priority:** Layers 1–3 (state machine, guard, hooks) are primary and agent-agnostic. Layers 4–6 (resume prompt, PROJECT_RULES, AGENTS.md) are supplementary.

**`packet_required` stop reason:** New stop reason when no open packet + ready tasks exist. Agent receives task list and create command. No path to `task_execute` without a packet.

**Done-task stale pointer fix:** `grain workflow next` with a done task in `current_task.md` routes to `phase_boundary` or `packet_required`, never `task_execute`.

**`task_execute` always includes packet path:** Agents hold the packet reference from the routing output, not after the fact.

**Pre-commit hook:** Blocks implementation commits without open packet; skips metadata-only commits (docs/working/ and tasks/ only). `GRAIN_SKIP_GUARD=1` escape hatch auto-logs to tooling_notes.

**Post-checkout hook:** Writes `.grain/last_workflow_state.json` — agents read this at session start for fast state recovery without CLI call.

**`prompts/workflow.resume.md`:** Agent-agnostic session resume protocol seeded in every workspace. AGENTS.md and CLAUDE.md reference by path, don't duplicate content.

## Files Changed
- `docs/canonical/enforcement_spec.md` — created
- `tasks/P30-T08-TASK-0197/task.md` — status set to done
