# CLI Specification

## 1. Purpose

This document defines the CLI contract for `Grain`.

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
grain <group> <command> [arguments] [options]
```

Where:

- `grain` is the executable name
- `<group>` is a command namespace
- `<command>` is an operation within that namespace

Example:

```text
grain task create --title "Add packet validator"
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

**`grain init`** — create the base repository structure for toolkit usage.

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

**`grain docs validate`** — validate required documentation structure and contracts.

**`grain docs index`** — generate or refresh documentation index artifacts if supported in v1.

**`grain docs show`** — display doc metadata or path information for a known document.

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

**`grain task create`** — create a new task packet.

**`grain task list`** — list task packets.

**`grain task show`** — show packet metadata and status.

**`grain task status`** — update packet status.

**`grain task validate`** — validate one packet or all packets.

**`grain task close`** — attempt closure validation for a packet.

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

**`grain context build`** — assemble context for a packet.

**`grain context show`** — display selected docs and packet materials for a packet.

**`grain context export`** — export context bundle for external tool usage.

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

- `grain context export` text mode writes a single markdown file
- if `grain context export` is run without `--output`, it writes `context_export.md` inside the packet directory

#### Structured output behavior

- `grain context build --format json` returns a `bundle` object for bundle inspection:
  - packet files
  - selected canonical docs as full document records
  - selected working docs as full document records
  - export metadata
- `grain context show --format json` returns a `bundle` object for context inspection:
  - packet files
  - selected canonical docs as summary records containing `id` and `path`
  - selected working docs as summary records containing `id` and `path`
  - export metadata
- `grain context export --format json` returns an `export` object for external-tool export metadata:
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

**`grain model show`** — show configured model classes and profiles.

**`grain model select`** — resolve which model class should be used for a workflow stage or task.

**`grain model escalate`** — promote a task or stage from one model class to another according to rules.

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

**`grain review check`** — run review-oriented validation on a packet.

**`grain review handoff`** — generate or validate handoff artifacts.

**`grain review summary`** — produce a structured summary of packet state for final inspection.

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

### 6.7 `adapter`

#### Purpose

Inspect the available adapter profiles and their configured domain contracts.

#### v1/v2 Commands

**`grain adapter list`** — list all available adapter profiles (official and custom).

**`grain adapter show`** — display the full contract for one adapter profile.

#### Responsibilities

- load and display adapter profiles from `docs/runtime/adapter_profiles.md` (or manifest-declared path)
- surface adapter fields: `adapter_id`, `domain_type`, `applies_to`, hint sections
- distinguish official from custom adapters where that information is available in the profile

#### Must not

- modify adapter profiles
- alter packet state
- load adapter contract data into a packet without explicit task creation or context command

#### Recommended options

- `--id <adapter-id>`
- `--format text|json`

#### Deferral note

`grain adapter list` and `grain adapter show` are defined here as the stable command surface for adapter inspection. Full implementation is deferred to the phase where adapter validation is automated. The command surface should be registered early so it appears in `grain --help` output and validates cleanly.

### 6.8 `orchestrate`

#### Purpose

Invoke the orchestration service to produce structured planning proposals for multi-domain or multi-packet work.

#### v2 Commands

**`grain orchestrate scope`** — analyze a described work item and identify relevant adapters, domains, and likely cross-domain dependencies.

**`grain orchestrate plan`** — produce a draft `OrchestratorPlan` containing packet candidates, dependency links, and split recommendations for a described phase or work scope.

#### Responsibilities

- query active adapters for scope and impact signals
- produce `OrchestratorPlan` proposal objects
- surface split recommendations and cross-domain dependency maps
- surface results for operator review — do not auto-accept or auto-create packets

#### Must not

- create task packets directly
- mutate the backlog or phase plan without operator action
- bypass the Review/Gate Layer
- alter canonical docs or workflow authority rules

#### Recommended options

- `--scope <text>` — describe the work item or phase to be planned
- `--adapter <adapter-id>` — restrict scope analysis to one or more adapters (repeatable)
- `--format text|json`

#### Deferral note

`grain orchestrate` commands are defined here as the stable CLI surface for orchestration. Implementation is deferred until the orchestration service is built in a future phase. The command group should be registered early so it appears in `grain --help` with a not-implemented message.

### 6.9 `verify`

#### Purpose

Bridge command surface for Sentinel verification integration. Allows operators and agents to submit task artifacts for external verification, poll for verification status, and ingest completed Sentinel results into Grain workflow state. The verification gate in the workflow runner stops execution until a pending verification is resolved.

#### v2/deferred Commands

**`grain verify submit`** — submit a set of task artifacts to Sentinel for verification; returns a `verification_id` for subsequent status checks.

**`grain verify status`** — check the status of a pending verification by `verification_id`; returns current state (`pending`, `complete`, `failed`) and any available outcome fields.

**`grain verify ingest`** — ingest a completed Sentinel result payload into Grain workflow state; triggers resolution of the verification gate stop condition in the runner.

#### Responsibilities

- accept verification requests referencing a specific task packet and its artifacts
- track the returned `verification_id` so status checks and ingestion can reference it
- surface the verification gate stop signal to the workflow runner when a result is pending
- upon ingestion, record the verification outcome in the packet's working artifacts
- surface `followup_candidates` from the result payload for operator review — do not auto-create packets

#### Must not

- implement Sentinel internals or verification logic
- auto-close, auto-approve, or auto-create work based on verification outcomes
- bypass the Review/Gate Layer when surfacing verification findings
- treat a Sentinel result payload as a canonical-level mutation without operator action
- silently succeed when a `verification_id` is unknown or a result is malformed

#### Recommended options

- `--id <task-id>` — task packet to submit for verification (for `submit`)
- `--verification-id <id>` — reference to a pending verification (for `status` and `ingest`)
- `--payload <path>` — path to a Sentinel result payload JSON file (for `ingest`)
- `--format text|json`

#### Deferral note

`grain verify` commands are defined here as the stable CLI surface for Sentinel integration. Implementation is deferred until the Sentinel Integration Layer (FR-006) is built. The command group should be registered as deferred stubs per §5.1 — returning a not-implemented error with a non-zero exit code — so it appears in `grain --help` and fails explicitly before implementation.

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
- adapter authoring or publishing commands (the contract is declarative and file-based; no CLI scaffolding is required to create one)

---

## 12. v1 Command Coverage Summary

v1 should support the following minimum command set:

```text
grain init
grain docs validate
grain docs show
grain task create
grain task list
grain task show
grain task status
grain task validate
grain task close
grain context build
grain context show
grain context export
grain model show
grain model select
grain model escalate
grain review check
grain review handoff
grain review summary
grain adapter list
grain adapter show
grain orchestrate scope
grain orchestrate plan
grain verify submit
grain verify status
grain verify ingest
```

`grain orchestrate` commands are defined but deferred. They must be registered with a not-implemented message until the orchestration service is implemented.

`grain verify` commands are defined but deferred. They must be registered with a not-implemented message until the Sentinel Integration Layer (FR-006) is implemented.

Additional commands may be added later, but the surface should remain disciplined.

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
