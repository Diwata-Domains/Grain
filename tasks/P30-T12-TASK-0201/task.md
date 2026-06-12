# Task: Spec CLI output ergonomics improvements

## Metadata
- **ID:** TASK-0201
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T12
- **Packet Path:** tasks/P30-T12-TASK-0201/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design improvements to the Grain CLI output surface that serve two distinct audiences: agents reading structured output (machine-readable contract) and humans using the terminal directly (visual quality, glanceability). The spec must cover both without trading one off against the other — they are different output modes, not competing designs.

## Why This Task Exists
Grain's CLI has grown across 30 phases, and output quality is inconsistent:
- Some commands have `--format json`; others don't
- Stop reasons from `grain workflow next` are not documented as a canonical vocabulary
- Text output varies in style: some commands use emoji, others use plain text, some use tables, others use bullets
- There is no single command that shows "where is this project right now?" — operators must call 3-4 commands to build that picture
- Agents parsing `grain workflow next` text output when `--format json` is unavailable get inconsistent results

This matters for both usage patterns:
- **Agent use:** The agent calls `grain workflow next --format json` and must parse the stop reason, the task reference, and the recommended action. If the JSON shape varies across Grain versions, agent integrations break silently.
- **Human terminal use:** The human operator runs `grain workflow next` and should immediately see what the project state is, what action is recommended, and what command to run next — without decoding a dense wall of text.

## Scope

### Part 1 — JSON output contract hardening

Every command that is automation-relevant must have a stable `--format json` surface. "Stable" means: the top-level keys do not change without a semver minor bump; new keys may be added; no key is removed without a major bump.

Commands that currently lack `--format json` and must get it:
- `grain docs audit`
- `grain suggest`
- `grain archive list`
- `grain doctor`
- `grain workspace list`
- `grain recipe list`

Commands that have `--format json` but need schema documentation in `docs/canonical/cli_spec.md`:
- `grain workflow next`
- `grain workflow guard`
- `grain task prepare`
- `grain verify status`

Each schema must be documented with: top-level keys, value types, example output, and which fields are guaranteed stable.

### Part 2 — Stop reason vocabulary

`grain workflow next` uses stop reasons to tell agents and operators what state the workflow is in. The current stop reasons are not documented as a canonical vocabulary. Define and document all stop reasons:

| Stop Reason | Meaning | Recommended Action |
|-------------|---------|-------------------|
| `task_execute` | Open in_progress task ready for execution | Run the task |
| `task_review` | Execution artifacts exist; review gate | Review the task |
| `task_close` | Review passed; ready to close | Close the task |
| `packet_required` | No in_progress packet; ready tasks exist | `grain task create` or `grain suggest` |
| `phase_boundary` | All tasks done; phase needs closing | `grain phase close` |
| `phase_complete` | Phase closed; next phase has ready tasks | Advance to next phase |
| `project_complete` | All phases done | Archive workspace |
| `workspace_archived` | Workspace marked archived | No action; workspace is done |
| `blocked` | No actionable path; human decision needed | Review blockers |
| `no_phases` | No phases defined yet | Run `grain init` and set up backlog |

Stop reasons must appear verbatim in `--format json` output under a `stop_reason` key and must never be free-form strings.

### Part 3 — Text output visual consistency

Define a style guide for Grain's text output:

**Symbols (no emoji):**
- `✓` — pass / done / ok
- `✗` — fail / error / violation
- `⚠` — warning
- `→` — recommended next action
- `+` — new / added
- `~` — changed / stale

**Structure:**
- Section headers: plain text followed by a blank line
- Key-value pairs: left-aligned key, right-padded to column 20, then value
- Tables: use `tabulate`-style formatting (pipe-separated), not raw spaces
- Command hints: always on a `→` line, always include the full command with flags

**Progress indicators:**
- For operations that take >0.5s: print a single "Checking..." line before output, clear it (or leave it) when done
- Never emit progress indicators to stdout when `--format json` is active — they go to stderr only

### Part 4 — `grain status`

A new top-level command that shows the complete workspace state in one shot. Replaces the need to call `grain workflow next` + `grain task prepare` + `grain docs audit` to build a picture.

```
grain status
grain status --format json
grain status --verbose
```

Output:
```
Grain Status — 2026-06-11

Phase:     Phase 30 — v0.4.0 Planning (in_progress)
Tasks:     10 total / 7 done / 3 ready / 0 in_progress / 0 blocked

Current:   no active task (run: grain workflow next)
Workflow:  packet_required — 3 ready tasks in Phase 30

Docs:      ⚠ 2 high-severity audit findings (run: grain docs audit)
Upgrade:   ✓ no pending upgrades

→ grain workflow next
```

`--verbose` includes all audit findings inline, linked workspace list, recent git summary.

## Deliverable
`docs/working/cli_ergonomics_spec.md` — covering: JSON output contract hardening list, stop reason vocabulary table, text output style guide, `grain status` command spec.

## Constraints
- JSON schema changes must respect existing integrations — additive only within a minor version
- Text output style changes are non-breaking (no automation depends on text format)
- `grain status` must complete in <1 second — it reads cached state files, it does not re-run all checks
- Stop reason vocabulary is canonical once published — no stop reason may be renamed without a major version bump
