# Grain Upstream Feedback Loop Spec

**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0198)

---

## 1. Purpose

This spec defines how Grain users can report friction back to Grain's maintainer without requiring server infrastructure, background processes, or automatic data collection.

The problem: every Grain user accumulates friction in `docs/working/tooling_notes.md`. That friction is currently trapped on their local machine. The only path back to the maintainer is the user manually finding the GitHub repo and filing an issue from scratch. Most don't. Real bugs and usability gaps never get reported.

Grain already seeds `tooling_notes.md` in every workspace as a structured table. That structure is the raw material. The missing piece is a zero-friction path from that table to a GitHub issue.

Constraints this spec must meet:
- Opt-in at every step — nothing is sent without explicit user action
- Local-first — no server required; uses GitHub URLs or API directly from the CLI
- Privacy-preserving — no project file content, no user data, no repo paths leave the machine
- Transparent — the user sees exactly what will be sent before it goes

---

## 2. `grain report` Command

### 2.1 What it does

Scans `docs/working/tooling_notes.md` for rows where:
- `Status` is `open`
- `Command` or `Observation` references a Grain CLI command (heuristic: column value starts with `grain`, mentions a known command name, or `Type` is `bug`/`ux`/`friction`/`missing-command`)

Presents a numbered list of matching items. User selects which to report. For each selected item, Grain constructs a pre-filled GitHub issue URL with:
- Title: `[type] command — brief observation` (derived from the table row)
- Body: structured template with Observation, Severity, Grain version, OS, and a "Steps to reproduce" section
- Labels: `bug`, `ux`, or `enhancement` based on `Type`

Opens the URL in the default browser (or prints it if `--no-browser`). After the user confirms, marks the row's Status as `reported` in `tooling_notes.md`.

### 2.2 Command interface

```
grain report                    Show open Grain-related tooling notes; select items to report
grain report --all              Show all open items, including low-severity and non-Grain items
grain report --no-browser       Print the URL instead of opening it
grain report --format json      Output selected items as JSON without opening browser
```

### 2.3 What is never sent

- File contents from the user's project
- Absolute file paths or repo names
- Any working doc content beyond the tooling_notes row itself
- Any personal identifying information
- Stack traces (unless the user explicitly includes them in the "Steps to reproduce" field)

### 2.4 GitHub issue URL construction

Target: `https://github.com/Diwata-Domains/grain/issues/new`

Parameters:
- `title` — `[{type}] {command} — {observation_summary}` (observation truncated at 80 chars)
- `body` — multi-line template (URL-encoded):
  ```
  **Observation:** {full_observation}
  **Severity:** {severity}
  **Grain version:** {grain_version}
  **OS:** {os_platform}
  **Install mode:** {install_mode}  ← from grain --version

  **Steps to reproduce:**
  (please fill in if applicable)

  **Expected behavior:**
  (please fill in)

  ---
  Reported via: grain report
  ```
- `labels` — `bug`, `ux`, or `enhancement` based on row Type

No Grain network call is made. The URL is opened in the browser; GitHub handles the form.

---

## 3. Opt-in Internal Error Telemetry

### 3.1 Opt-in mechanism

```
grain config set telemetry true      Enable error telemetry
grain config set telemetry false     Disable (default)
grain config get telemetry           Show current setting
```

Config stored at `~/.grain/config.toml` (user-level, not project-level). Never committed to a repo.

Default: `false`. Grain never sends anything without explicit opt-in.

### 3.2 What is captured on error

When telemetry is enabled and Grain throws an unhandled exception:

| Field | Value |
|-------|-------|
| `grain_version` | e.g. `0.4.0` |
| `os` | Platform string (e.g. `darwin`, `linux`) |
| `python_version` | e.g. `3.12.4` |
| `command` | The grain command that failed (e.g. `grain workflow next`) |
| `exception_class` | e.g. `KeyError`, `FileNotFoundError` |
| `exception_message` | The exception message (not the stack trace) |
| `workspace_fingerprint` | Phase number, task count, task status distribution — no content |
| `session_id` | Random UUID, regenerated per invocation, not stored |

### 3.3 What is never captured

- File contents
- Task titles, descriptions, or any doc content
- Repo names, paths, or user identity
- Stack traces (by default; future: opt-in with separate `telemetry.include_traces` setting)

### 3.4 Delivery mechanism

Errors queue locally in `.grain/telemetry_queue.jsonl`. The file is not committed to version control (added to Grain's default `.gitignore`).

On the next `grain` invocation (any command), if the queue has items:
```
1 error report queued from last session. Details:
  Command: grain workflow next
  Error: KeyError: 'task_id'
Send to grain maintainer? [y/N]
```

User confirms → Grain creates a GitHub issue via the GitHub Issues API on `Diwata-Domains/grain` (or constructs a pre-filled URL if the API is unavailable or user prefers browser).

User declines → queue is cleared, nothing sent.

The user always sees the payload before confirming. `grain config get telemetry.last-payload` shows the last queued payload.

---

## 4. `grain notes` Command Group

A lightweight CLI for working with `tooling_notes.md` without opening the file. This is the agent-callable interface — any agent running `grain notes add` produces a correctly-formatted row regardless of which AI system is driving.

### 4.1 `grain notes list`

```
grain notes list
grain notes list --status open|resolved|reported
grain notes list --severity low|medium|high
grain notes list --format json
```

Filtered tabular view of `tooling_notes.md` entries.

### 4.2 `grain notes add`

```
grain notes add \
  --type <bug|ux|friction|missing-command|workflow_friction|root_cause|tool_bug> \
  --command "<grain command or context>" \
  --observation "<what happened and what would be better>" \
  --severity <low|medium|high>
```

Appends a correctly-formatted row to `tooling_notes.md`. The row format matches the seeded table structure exactly — no special markers. Agents use this instead of editing the file directly.

If `tooling_notes.md` does not exist, `grain notes add` creates it with the standard header.

### 4.3 `grain notes resolve <row-id>`

Marks a row as `resolved` with a timestamp. Row ID is derived from the date and command slug (e.g., `2026-04-27-grain-workflow-next`). `grain notes list --format json` includes the `row_id` field for each entry.

### 4.4 `grain notes resolve --all`

Marks all `open` entries as `resolved`. Intended for use after a Grain upgrade that addressed multiple outstanding friction items.

---

## 5. Standing Rule in Bundled `PROJECT_RULES.md`

The mandatory tooling notes rule added to every `grain init`-seeded `PROJECT_RULES.md`:

```markdown
## Tooling Notes Rule (Mandatory)

Whenever you encounter friction with the Grain CLI — an unexpected error, a missing
flag, confusing output, or a workaround you used instead of the expected command —
you MUST log it before continuing:

    grain notes add --type <bug|ux|friction|missing-command> \
                    --command "<grain command>" \
                    --observation "<what happened and what would be better>" \
                    --severity <low|medium|high>

Do not skip this step. Do not log it "later". Log it now, then continue.
This applies to all agents — there are no exceptions for planning mode,
inline execution, or session continuations.
```

Using `grain notes add` (not raw file editing) means:
- The rule is the same regardless of which agent is executing
- The format is always correct
- The log is always in the right file
- No Grain-managed file is modified directly by an agent

---

## 6. GitHub Endpoint Decision

**Primary target: GitHub Issues on `Diwata-Domains/grain`**

Rationale:
- Issues are indexed and searchable by the maintainer
- `grain report` constructs the URL; no Grain API key required for URL-mode
- Telemetry uses the GitHub Issues API with a project-level token; if unavailable, falls back to URL mode
- Discussions are not used — issues provide better tracking for bugs and UX reports

A dedicated feedback repo (separate from the Grain source repo) is not used in v0.4.0. If issue volume grows, the maintainer can triage to a separate repo manually without changing the `grain report` target URL.
