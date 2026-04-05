# CLI Specification

## 1. Purpose

This document defines the CLI contract for `Forge`.

It governs:
- command groups
- command responsibilities
- command input/output expectations
- CLI behavior rules
- error handling conventions
- exit code conventions
- output format expectations for v1

It controls decisions about:
- what commands exist in v1
- what each command is allowed to do
- what arguments and options each command accepts
- how command results are communicated to the user
- how CLI behavior remains stable across implementation changes

It does not cover:
- product scope
- internal package/module layout
- workflow stage semantics beyond command-facing behavior
- full file schemas for manifests and task packets
- model-provider implementation details

Those belong in product scope, architecture, workflow specification, and data contracts.

---

## 2. CLI Design Goals

The CLI must be:

1. **Practical**
   - useful for daily repository work

2. **Predictable**
   - commands should behave consistently across command groups

3. **Composable**
   - outputs should support scripting and handoff to external tools

4. **Minimal**
   - v1 should avoid excessive command surface area

5. **Transparent**
   - actions should be observable in filesystem changes and command output

6. **Safe**
   - commands should not silently alter canonical authority

---

## 3. CLI Operating Model

The CLI is the primary interface for interacting with the toolkit in v1.

The CLI should support these major use areas:

1. repository initialization
2. documentation validation and inspection
3. task packet creation and lifecycle management
4. context preparation/export
5. model routing inspection
6. review and handoff support

The CLI must orchestrate workflow state through files on disk, not hidden service state.

---

## 4. Global CLI Rules

### 4.1 General Command Shape

Recommended command form:

```text
forge <group> <command> [arguments] [options]
```

Where:

- `forge` is the executable name
- `<group>` is a command namespace
- `<command>` is an operation within that namespace

Example:

```text
forge task create --title "Add packet validator"
```

### 4.2 Path Resolution Rules

Unless explicitly overridden:

- commands operate relative to the current repository root
- repository root may be auto-detected or passed explicitly
- path arguments must support relative paths

Recommended global option:

```text
--repo <path>
```

### 4.3 Output Rules

Each command should produce one of the following output styles:

**Human-readable output** — default for interactive use.

**Structured output** — for automation or scripting.

Recommended global option:

```text
--format text|json
```

v1 minimum:

- default `text`
- optional `json` for key commands

### 4.4 Dry Run Rule

Commands that create, modify, or validate multiple files should support dry-run behavior where practical.

Recommended option:

```text
--dry-run
```

In dry-run mode:

- no files are changed
- intended actions are reported

### 4.5 Verbosity Rule

Recommended global options:

```text
--quiet
--verbose
```

Behavior:

- `--quiet`: minimal output, errors only where possible
- `--verbose`: include reasoning about file selection, validation checks, and state changes

### 4.6 Error Rule

Commands must fail clearly.

At minimum, an error should state:

- what failed
- where it failed
- what artifact or input caused failure when known

The CLI should not mask filesystem or contract failures.

---

## 5. Exit Code Conventions

Recommended v1 exit codes:

| Code | Meaning |
|------|---------|
| `0` | success |
| `1` | general command failure |
| `2` | invalid arguments or usage |
| `3` | validation failure |
| `4` | missing required file or path |
| `5` | state transition not allowed |
| `6` | configuration or manifest error |
| `7` | external adapter/integration error |

These codes should remain stable once implemented.

### 5.1 Placeholder Command Behavior

Unimplemented CLI commands must not silently succeed.

Before a command is fully implemented, it must either:
- be absent from the command surface entirely, or
- return an explicit not-implemented error with a non-zero exit code

Silent success (exit 0, no output) from a stub is not permitted. It creates false confidence during phased implementation and makes stubs indistinguishable from working commands during validation.

Recommended behavior for a registered but unimplemented command: print a clear not-implemented message to stderr and exit non-zero (exit code 1 is acceptable until a dedicated code is assigned).

This rule may be mirrored in `docs/runtime/PROJECT_RULES.md` once canonically approved.

---

## 6. Command Groups

### 6.1 `init`

#### Purpose

Initialize repository structure and baseline toolkit artifacts.

#### v1 Commands

**`forge init`** — create the base repository structure for toolkit usage.

#### Responsibilities

- create required directories
- write seed files from templates where missing
- initialize docs/task structure needed for workflow usage

#### Must not

- overwrite existing canonical docs silently
- invent project-specific scope
- create hidden runtime state

#### Recommended options

- `--repo <path>`
- `--force`
- `--dry-run`
- `--format text|json`

#### Expected behavior

If the repository is already initialized:

- report existing state
- do not overwrite protected files without explicit force behavior

---

### 6.2 `docs`

#### Purpose

Inspect and validate repository documentation state.

#### v1 Commands

**`forge docs validate`** — validate required documentation structure and contracts.

**`forge docs index`** — generate or refresh documentation index artifacts if supported in v1.

**`forge docs show`** — display doc metadata or path information for a known document.

#### Responsibilities

- validate docs against manifest/contracts
- identify missing or malformed docs
- expose doc registry information

#### Must not

- rewrite canonical semantics
- invent missing canonical content automatically unless explicitly scaffolded

#### Recommended options

- `--doc <id>`
- `--strict`
- `--format text|json`

---

### 6.3 `task`

#### Purpose

Create and manage task packets.

#### v1 Commands

**`forge task create`** — create a new task packet.

**`forge task list`** — list task packets.

**`forge task show`** — show packet metadata and status.

**`forge task status`** — update packet status.

**`forge task validate`** — validate one packet or all packets.

**`forge task close`** — attempt closure validation for a packet.

#### Responsibilities

- allocate task IDs
- create packet directories/files
- manage lifecycle state transitions
- validate packet completeness

#### Must not

- skip required packet files
- allow invalid transitions silently
- mark incomplete work as done

#### Recommended options

- `--title <text>`
- `--id <task-id>`
- `--status <value>`
- `--all`
- `--phase <name>`
- `--format text|json`

---

### 6.4 `context`

#### Purpose

Prepare minimal execution context for one task packet.

#### v1 Commands

**`forge context build`** — assemble context for a packet.

**`forge context show`** — display selected docs and packet materials for a packet.

**`forge context export`** — export context bundle for external tool usage.

#### Responsibilities

- read packet metadata and references
- select relevant docs
- produce inspectable context bundles
- support external coding-agent workflows

#### Must not

- load the full repo by default
- include unrelated docs without explicit request
- hide selected sources from the user

#### Recommended options

- `--id <task-id>`
- `--output <path>`
- `--include-working`
- `--tag <name>`
- `--format text|json`

#### Default tag behavior

- if no `--tag` flags are provided, context commands must default canonical doc selection to the `running_tasks` tag set
- explicit `--tag` values replace the default tag set for that invocation
- working docs remain opt-in through `--include-working`

#### Output behavior

- `forge context export` text mode writes a single markdown file
- if `forge context export` is run without `--output`, it writes `context_export.md` inside the packet directory

#### Structured output behavior

- `forge context build --format json` returns a `bundle` object for bundle inspection:
  - packet files
  - selected canonical docs as full document records
  - selected working docs as full document records
  - export metadata
- `forge context show --format json` returns a `bundle` object for context inspection:
  - packet files
  - selected canonical docs as summary records containing `id` and `path`
  - selected working docs as summary records containing `id` and `path`
  - export metadata
- `forge context export --format json` returns an `export` object for external-tool export metadata:
  - `task_id`
  - `generated_at`
  - `sources[]` entries containing `path`, `kind`, and `exists`
  - no full content bodies
- these command-specific JSON shapes are distinct by design and must not drift silently

---

### 6.5 `model`

#### Purpose

Inspect model class routing and routing decisions.

#### v1 Commands

**`forge model show`** — show configured model classes and profiles.

**`forge model select`** — resolve which model class should be used for a workflow stage or task.

**`forge model escalate`** — promote a task or stage from one model class to another according to rules.

#### Responsibilities

- expose model-class abstraction
- support workflow-stage routing
- make escalation explicit

#### Must not

- hardcode provider identity into the user-facing workflow
- mutate packet state without explicit action

#### Recommended options

- `--stage <name>`
- `--id <task-id>`
- `--format text|json`

---

### 6.6 `review`

#### Purpose

Support acceptance, handoff, and completion workflows.

#### v1 Commands

**`forge review check`** — run review-oriented validation on a packet.

**`forge review handoff`** — generate or validate handoff artifacts.

**`forge review summary`** — produce a structured summary of packet state for final inspection.

#### Responsibilities

- verify completion prerequisites
- prepare review artifacts
- support closure/handoff steps

#### Must not

- bypass packet completion rules
- silently approve missing deliverables
- alter canonical docs directly

#### Recommended options

- `--id <task-id>`
- `--format text|json`

---

## 7. Required Command Behaviors

### 7.1 Idempotence Expectations

Commands should be idempotent where practical.

Examples:

- `docs validate` should not alter state
- `docs show` should not alter state
- repeated `init` should not duplicate structure unnecessarily
- repeated `task validate` should yield stable results for stable inputs

### 7.2 File Modification Transparency

Any command that writes files should clearly report:

- files created
- files updated
- files skipped
- files blocked from modification

### 7.3 Canonical Protection Rule

No CLI command may directly alter canonical docs unless a future command is explicitly designed for approved canonical revision.

For v1:

- canonical docs are read-only from ordinary operational commands

### 7.4 Validation Before Destructive Action

Commands that depend on valid repository state should validate required prerequisites first.

Examples:

- `task close` should validate packet completeness
- `context build` should validate packet existence and required files
- `docs index` should validate manifest readability first

---

## 8. Argument Conventions

### 8.1 Task Identifier Convention

Task packet references should use:

```text
--id TASK-####
```

### 8.2 Document Identifier Convention

Documents may be referenced by:

- manifest `id`
- explicit path

Preferred option:

```text
--doc <id>
```

### 8.3 Output Path Convention

Commands that export data should support:

```text
--output <path>
```

### 8.4 Format Convention

Where structured output is supported:

```text
--format text|json
```

---

## 9. Human-Readable Output Expectations

Default output should emphasize:

- status
- relevant paths
- next action
- validation findings
- blocking issues

Example style:

- concise header
- artifact list
- status/result line
- errors grouped clearly

The CLI should optimize for terminal readability, not long narrative output.

---

## 10. Structured Output Expectations

Where JSON output is supported, command output should be stable enough for scripting.

Recommended result fields where relevant:

- `ok`
- `command`
- `repo`
- `task_id`
- `status`
- `files_created`
- `files_updated`
- `errors`
- `warnings`

Exact schemas may evolve, but result structure should remain predictable.

---

## 11. Deferred CLI Features

The following are explicitly deferred unless needed later:

- interactive TUI
- daemon/server mode
- live watch mode
- background job orchestration
- multi-user collaboration commands
- plugin marketplace commands

---

## 12. v1 Command Coverage Summary

v1 should support the following minimum command set:

```text
forge init
forge docs validate
forge docs show
forge task create
forge task list
forge task show
forge task status
forge task validate
forge task close
forge context build
forge context show
forge context export
forge model show
forge model select
forge model escalate
forge review check
forge review handoff
forge review summary
```

Additional commands may be added later, but v1 should keep the surface disciplined.

---

## 13. Decision Boundaries

### 13.1 Decisions This Document Controls

- command groups and responsibilities
- command-level behavior expectations
- CLI input/output conventions
- exit code conventions
- canonical protection at command surface
- minimum v1 CLI coverage

### 13.2 Decisions This Document Does Not Control

- product inclusion/exclusion decisions
- internal package boundaries
- workflow stage design
- manifest schema details
- packet file schemas
- provider-specific adapter internals

Those must align with this CLI contract but are governed elsewhere.
