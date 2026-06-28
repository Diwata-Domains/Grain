# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""AGENTS.md management service.

Writes or updates the grain-managed workflow instructions block in AGENTS.md
at the repo root. The block is delimited by HTML comment markers so it can
be surgically updated without touching any user content outside it.

Idempotency rules:
  - No AGENTS.md        → create file containing only the grain block
  - AGENTS.md, no block → append grain block (user content above is preserved)
  - AGENTS.md, has block → replace only the grain block in-place
  - Content outside markers is NEVER read for logic, NEVER rewritten
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_MARKER_START = "<!-- grain:workflow-instructions:start -->"
_MARKER_END = "<!-- grain:workflow-instructions:end -->"

_AGENTS_MD_FILENAME = "AGENTS.md"
_CLAUDE_MD_FILENAME = "CLAUDE.md"


def _grain_block() -> str:
    return f"""{_MARKER_START}
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
{_MARKER_END}"""


@dataclass
class AgentsMdResult:
    action: str          # "created" | "updated" | "skipped" | "appended"
    path: str            # relative path written
    claude_md_exists: bool = False
    dry_run: bool = False


def write_agents_md(root: Path, dry_run: bool = False) -> AgentsMdResult:
    """Create or update AGENTS.md with the grain workflow block.

    Returns an AgentsMdResult describing what happened (or would happen in
    dry-run mode). Never touches content outside the grain markers.
    """
    agents_path = root / _AGENTS_MD_FILENAME
    claude_md_exists = (root / _CLAUDE_MD_FILENAME).exists()
    rel_path = _AGENTS_MD_FILENAME
    block = _grain_block()

    # ── Case 1: file does not exist ──────────────────────────────────────────
    if not agents_path.exists():
        if not dry_run:
            agents_path.write_text(block + "\n", encoding="utf-8")
        return AgentsMdResult(
            action="created",
            path=rel_path,
            claude_md_exists=claude_md_exists,
            dry_run=dry_run,
        )

    existing = agents_path.read_text(encoding="utf-8")

    # ── Case 2: file exists, grain block present → update block in-place ────
    if _MARKER_START in existing and _MARKER_END in existing:
        start_idx = existing.index(_MARKER_START)
        end_idx = existing.index(_MARKER_END) + len(_MARKER_END)
        new_content = existing[:start_idx] + block + existing[end_idx:]
        if new_content == existing:
            return AgentsMdResult(
                action="skipped",
                path=rel_path,
                claude_md_exists=claude_md_exists,
                dry_run=dry_run,
            )
        if not dry_run:
            agents_path.write_text(new_content, encoding="utf-8")
        return AgentsMdResult(
            action="updated",
            path=rel_path,
            claude_md_exists=claude_md_exists,
            dry_run=dry_run,
        )

    # ── Case 3: file exists, no grain block → append ─────────────────────────
    separator = "\n\n---\n\n" if existing.rstrip() else ""
    new_content = existing.rstrip() + separator + block + "\n"
    if not dry_run:
        agents_path.write_text(new_content, encoding="utf-8")
    return AgentsMdResult(
        action="appended",
        path=rel_path,
        claude_md_exists=claude_md_exists,
        dry_run=dry_run,
    )
