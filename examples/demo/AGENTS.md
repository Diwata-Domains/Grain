<!-- grain:workflow-instructions:start -->
## Grain Workflow — HARD CONSTRAINT

You MUST NOT create or modify implementation files without an open task packet.

See the session start protocol at: `prompts/workflow.resume.md`

---

This repo uses [Grain](https://pypi.org/project/grain-kit/) for structured
task lifecycle management. All code changes must go through the workflow.

**Session start — run this first, before reading any user message or touching files:**

```
grain --format json workflow next
```

This returns the current workflow state and next legal action. If the result
shows `stop_reason: packet_required`, create a packet before proceeding:

```
grain task create --id <TASK-ID>
```

Never work from chat context alone when no packet exists on disk. The packet
files on disk are the authority, not the conversation history.

**Key commands:**

| Command | Purpose |
|---------|---------|
| `grain --format json workflow next` | Current state + next action |
| `grain workflow guard` | Point-in-time enforcement check |
| `grain task create --id TASK-####` | Create a task packet |
| `grain task close --id TASK-#### --quick --summary "..."` | Close a completed task |
| `grain workflow reconcile --fix` | Repair drift across working docs |
| `grain phase close` | Seal a completed phase before advancing |

**`--format` is a global flag** — place it before the subcommand:
`grain --format json workflow next` ✓ (not `grain workflow next --format json`)
<!-- grain:workflow-instructions:end -->
