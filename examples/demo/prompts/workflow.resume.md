# Grain Session Resume Protocol

This file defines how to start or resume a work session in a Grain-managed
repository. It is agent-agnostic — follow these steps regardless of which AI
system is reading this.

---

## Step 1 — Read current workflow state

Run:

```
grain --format json workflow next
```

This returns the current workflow state and the next legal action. Feed the
full JSON output into your working context before reading any user message or
touching any file.

**Fast path:** if `.grain/last_workflow_state.json` exists and is less than
5 minutes old, you may read it directly instead of running `grain workflow next`.
If it is stale or absent, always run the command.

---

## Step 2 — Verify an open packet exists

Check the `evaluation.active_task_id` field in the output.

- If it is a TASK-XXXX value: the packet is open. Read `current_task.md` and
  verify the packet directory exists under `tasks/`.
- If it is `"none"` or the `stop_reason` is `"packet_required"`: no packet is
  open. Go to Step 3.
- If the `stop_reason` is `"stale_task_pointer"`: `current_task.md` points to a
  completed packet. Set `Task ID:` to `none` in `docs/working/current_task.md`
  before proceeding.

---

## Step 3 — If no packet is open, create one before proceeding

Do not implement anything without an open packet. If the workflow returned
`packet_required`:

1. Identify the ready task from `evaluation.blocking_reasons` or
   `evaluation.candidate_tasks`.
2. Run `grain task create --id <TASK-ID>` to create the packet.
3. Set the packet's `task.md` status to `in_progress`.
4. Update `docs/working/current_task.md` to point to this packet.
5. Run `grain --format json workflow next` again to confirm the state is correct.

For small or conversational tasks, `grain task create --simple` creates a
lightweight packet (task.md + results.md only).

---

## Step 4 — Proceed with the next action

Use `evaluation.next_action` and `evaluation.recommended_prompt` to determine
what to do next:

| next_action | What to do |
|---|---|
| `task_execute` | Implement the work described in the active packet |
| `task_review` | Review and close the active packet |
| `task_close` | Close the active packet via `grain task close --id <TASK-ID>` |
| `task_planning` | Plan the next task before execution |
| `phase_review_close` | Review and seal the current phase |

---

## Degraded path

If `grain workflow next` fails for any reason:

1. Read `docs/working/current_task.md` directly.
2. If `Task ID:` is a TASK-XXXX value, read that packet's `task.md`.
3. Continue based on the packet's `Status:` field.
4. Log the failure to `docs/working/tooling_notes.md` so it can be investigated.

Never continue from chat context alone when there is uncertainty about which
task is active or what the current state is. The packet files on disk are the
authority.
