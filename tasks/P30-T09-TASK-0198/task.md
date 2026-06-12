# Task: Spec upstream feedback loop — `grain report` and opt-in telemetry

## Metadata
- **ID:** TASK-0198
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T09
- **Packet Path:** tasks/P30-T09-TASK-0198/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a feedback loop that lets Grain users (people who install Grain as a tool in their own projects) report friction back to Grain's maintainer without requiring server infrastructure, background processes, or automatic data collection. Two complementary surfaces: a `grain report` command that converts local tooling_notes entries into pre-filled GitHub issues, and an opt-in telemetry layer that captures Grain's own internal errors and queues them for reporting.

## Why This Task Exists
Every Grain user accumulates friction in their `docs/working/tooling_notes.md`. That friction is currently trapped on their local machine — the only path back to the maintainer is the user manually finding the GitHub repo and filing an issue from scratch. Most don't. The result: real bugs and usability gaps never get reported, and the maintainer has no signal from actual usage.

Grain already seeds `tooling_notes.md` in every workspace as a structured table (Date | Type | Command | Observation | Severity | Status). That structure is the raw material. The missing piece is a zero-friction path from that table to a GitHub issue.

This must be:
- **Opt-in at every step** — nothing is sent without explicit user action
- **Local-first** — no server required; uses GitHub's API directly from the CLI
- **Privacy-preserving** — no project file content, no user data, no repo paths leave the machine
- **Transparent** — the user sees exactly what will be sent before it goes

## Scope

### Part 1 — `grain report` command

`grain report`
- Scans `docs/working/tooling_notes.md` for rows where:
  - `Status` is `open`
  - `Command` or `Observation` references a Grain CLI command (heuristic: starts with `grain`, mentions a known command name, or Type is `bug`/`ux`/`friction`/`missing-command`)
- Presents a numbered list of matching items to the user
- User selects which item(s) to report
- For each selected item, Grain constructs a pre-filled GitHub issue URL:
  - Title: `[type] command — brief observation` (derived from the table row)
  - Body: structured template with Observation, Severity, Grain version, OS, and a "Steps to reproduce" section pre-filled where possible
  - Labels pre-applied: `bug`, `ux`, or `enhancement` based on `Type` column
- Opens the URL in the default browser (or prints it if `--no-browser` is passed)
- Marks the row's Status as `reported` in tooling_notes.md after the user confirms

`grain report --all`
- Shows all open Grain-related items without filtering, including low-severity ones

`grain report --format json`
- Outputs the selected items as structured JSON without opening a browser — for piping into custom workflows

**What is never sent:**
- File contents from the user's project
- Absolute file paths or repo names
- Any working doc content other than the tooling_notes row itself
- Any personal identifying information

### Part 2 — Opt-in internal error telemetry

This layer captures errors that Grain itself throws — Python exceptions, unexpected state, command failures — not errors the agent writes to tooling_notes. It only activates if the user explicitly opts in.

**Opt-in:**
```
grain config set telemetry true
grain config set telemetry false   # opt out at any time
```
Default is `false`. Grain never sends anything without explicit opt-in.

**What is captured on error:**
- Grain version
- OS and Python version
- Command that failed (e.g. `grain workflow next`)
- Exception class and message (not stack trace by default)
- Grain workspace state fingerprint: phase number, task count, task statuses — no content
- A session ID (random UUID, regenerated per invocation, not stored or linked to user)

**What is never captured:**
- File contents
- Task titles, descriptions, or any doc content
- Repo names, paths, or user identity

**Delivery mechanism:**
- Errors are queued locally in `.grain/telemetry_queue.jsonl` — never sent in-band
- On the next `grain` invocation, if the queue has items, Grain asks: "1 error report queued from last session. Send to grain-kit maintainer? [y/N]"
- User confirms → Grain sends via GitHub Issues API (creates an issue on `Diwata-Domains/grain`) or appends to a GitHub Discussion thread if Issues API is rate-limited
- User declines → queue is cleared, nothing sent
- The user always sees exactly what will be sent before confirming

**Rationale for ask-per-invocation rather than background send:**
- No background process or daemon required — fits Grain's local-first model
- User retains full control; declining is the default path
- The ask appears only when there is something queued — not on every invocation

### Part 3 — `grain notes` command group

A lightweight command group for working with tooling_notes.md without opening the file:

`grain notes list [--status open|resolved|reported] [--severity low|medium|high]`
- Filtered tabular view of tooling_notes entries

`grain notes add --type <type> --command <cmd> --observation "..." --severity <sev>`
- Appends a row to tooling_notes.md from the CLI — so agents can log friction without editing the file directly
- This is the agent-callable interface: any agent running `grain notes add` produces a correctly-formatted row regardless of which AI system is doing it

`grain notes resolve <row-id>`
- Marks a row resolved with a timestamp
- Row ID is derived from date + command slug (e.g. `2026-04-27-grain-workflow-next`)

### Part 4 — Standing rule in PROJECT_RULES.md

Add to the bundled `PROJECT_RULES.md` template a mandatory tooling notes rule:

```
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

Using `grain notes add` (not raw file editing) means: the rule is the same regardless of which agent is executing, the format is always correct, and the log is always in the right file.

## Deliverable
`docs/canonical/feedback_spec.md` — spec covering:
- `grain report` command interface, filtering logic, GitHub issue URL construction, privacy boundaries
- Opt-in telemetry: opt-in mechanism, captured fields, delivery mechanism, privacy boundaries
- `grain notes` command group interface
- The mandatory tooling notes rule for PROJECT_RULES.md
- Decision: which GitHub endpoint to target (Issues vs Discussions vs a dedicated feedback repo)

## Constraints
- Nothing is sent without explicit user action at every step — no background sends, no auto-reporting
- Default for telemetry is `false` — it must be explicitly enabled
- `grain report` must work with no network access except the GitHub issue URL construction (the URL can be opened in a browser without a Grain network call)
- `grain notes add` must produce a row identical in format to a manually-written row — no special markers
- The telemetry payload must be reviewable by the user before sending — `grain config get telemetry.last-payload` shows the last queued payload
- Telemetry opt-in status must be stored in user-level config (`~/.grain/config.toml`), not in the project workspace — so it applies across all projects and doesn't get committed to repos
