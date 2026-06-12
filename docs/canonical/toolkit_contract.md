# Grain Toolkit Contract

**Version:** 1.0
**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0191)

---

## 1. Purpose

The toolkit contract defines how sibling tools (Assay, Conclave, DAEMON, and any future tool in the Diwata workspace) interoperate with Grain without relying on chat memory as the integration layer.

Prior to this contract, inter-tool coordination happened through CLI commands called ad-hoc in agent prompts. This works for one session but breaks silently when:
- The agent loses context and doesn't know which Grain workspace is active
- A sibling tool needs to write a result that must land in the right task packet
- A recipe needs to call multiple tools in sequence and track the overall flow

The contract provides an explicit, versioned, local-first interface that any tool can implement without knowing Grain's internals.

---

## 2. Scope and Principles

**In scope:**
- What Grain exposes to sibling tools (capabilities, current state, packet write surface)
- What sibling tools expose to Grain (events, verification results, capture receipts)
- Transport model and discovery convention
- Versioning model for forward-compatible extension

**Out of scope:**
- Network transport — all contract exchange is local file artifacts + structured stdout
- Server or daemon — no running process required
- Authentication between tools — all tools run as the same OS user in the same workspace

**Principles:**
1. File-backed: contract artifacts live on disk, readable by any tool without calling Grain's CLI
2. Pull-first: sibling tools read Grain state by calling `grain` CLI commands or reading state files; Grain does not push events to them
3. Versioned: the contract schema is semver-versioned; a future Grain can extend it without breaking existing integrations
4. Additive: new sibling tools extend the contract by declaring new `provides:` entries; they don't modify Grain's core schema

---

## 3. Contract Schema

Every tool that interoperates with Grain declares a `toolkit_contract.yaml` in its workspace root (or at the path registered in its `docs_manifest.yaml`). This is a bilateral declaration — it says what the tool requires from Grain and what it provides back.

### 3.1 Schema definition

```yaml
# toolkit_contract.yaml
grain_contract_version: "1.0"

tool:
  name: <string>                   # e.g. "assay", "conclave", "daemon"
  version: <semver-string>         # the tool's own version
  workspace: <relative-path>       # path to this tool's Grain workspace root, if different from CWD

requires:
  grain_version: "<semver-range>"  # e.g. ">=0.4.0"
  capabilities:                    # list of Grain capabilities this tool depends on
    - <capability-id>

provides:
  events:                          # events this tool emits that Grain can consume
    - id: <string>
      description: <string>
      artifact_path_template: <string>  # where the event artifact lands; may use {task_id}, {timestamp}
  artifacts:                       # persistent artifacts this tool writes that Grain may reference
    - id: <string>
      description: <string>
      path_template: <string>
```

### 3.2 Grain's own capability declaration

Grain publishes its own capability list at `docs/runtime/grain_capabilities.yaml`, written by `grain init` and updated by `grain upgrade`. Sibling tools read this to discover what the installed Grain version supports before calling any command.

```yaml
# docs/runtime/grain_capabilities.yaml — written by Grain, read by sibling tools
grain_version: "0.4.0"
capabilities:
  - id: verify_submit
    command: "grain verify submit"
    since: "0.3.0"
  - id: verify_ingest
    command: "grain verify ingest"
    since: "0.3.0"
  - id: workflow_state
    command: "grain --format json workflow next"
    since: "0.2.0"
  - id: task_results_write
    description: "Write to tasks/<id>/results.md via grain task close"
    since: "0.1.0"
  - id: suggest_approve
    command: "grain suggest accept"
    since: "0.4.0"
  - id: context_link
    command: "grain context link"
    since: "0.4.0"
```

---

## 4. Transport Model

All inter-tool data exchange uses one of two mechanisms:

### 4.1 Structured stdout (request/response)
A sibling tool calls a Grain CLI command with `--format json` and reads the JSON from stdout. This is the primary mechanism for reading state. No file artifact is left on disk.

```
grain --format json workflow next          → current workflow state
grain --format json task prepare           → assembled context bundle
grain verify status --task <id> --format json → verification state
```

### 4.2 File artifact drop (async results)
A sibling tool writes a JSON artifact to an agreed path, then signals Grain by calling a Grain CLI command that ingests it. This is the primary mechanism for writing results into a Grain packet.

Assay example:
1. Assay captures a screenshot and writes `docs/working/captures/assay-2026-06-11-001.json`
2. Assay calls `grain verify ingest --artifact docs/working/captures/assay-2026-06-11-001.json`
3. Grain reads the artifact, validates it against the active packet, and appends to the packet's verification log

The path convention and ingestion command are declared in the tool's `toolkit_contract.yaml` under `provides.events[*].artifact_path_template`.

### 4.3 What is never used
- Named pipes or Unix sockets
- HTTP or any network transport
- Shared memory
- Environment variable injection across process boundaries

---

## 5. Grain ↔ Assay Contract (Reference Implementation)

The Assay integration (landed in Phase 28 via `grain verify`) is the first concrete instance of the toolkit contract. It is documented here as the reference implementation.

### What Grain provides to Assay
- `grain --format json workflow next` — Assay reads this to know which task is active before capturing
- `grain verify submit --task <id> --type <type> --artifact <path>` — Assay calls this to open a verification request
- `grain verify ingest --artifact <path>` — Assay calls this to deliver a capture result
- `grain verify status --task <id> --format json` — Assay reads this to check if verification is complete

### What Assay provides to Grain
- `capture_submitted` event: a JSON artifact at `docs/working/captures/<id>.json` with fields: `task_id`, `timestamp`, `capture_type`, `asset_path`, `comment`
- `verification_result` event: a JSON artifact at `docs/working/verifications/<id>.json` with fields: `task_id`, `verifier`, `verdict` (`pass`/`fail`/`partial`), `notes`, `assets`

### Assay's toolkit_contract.yaml
```yaml
grain_contract_version: "1.0"

tool:
  name: assay
  version: "0.1.x"

requires:
  grain_version: ">=0.3.0"
  capabilities:
    - verify_submit
    - verify_ingest
    - workflow_state

provides:
  events:
    - id: capture_submitted
      description: "Screenshot or state capture submitted for an active task"
      artifact_path_template: "docs/working/captures/{task_id}-{timestamp}.json"
    - id: verification_result
      description: "Verification verdict for a submitted capture"
      artifact_path_template: "docs/working/verifications/{task_id}-{timestamp}.json"
  artifacts:
    - id: capture_asset
      description: "The raw captured asset (image, HAR, state dump)"
      path_template: "docs/working/captures/assets/{task_id}-{timestamp}.*"
```

---

## 6. Extension Points — Conclave and DAEMON

Future tools declare their own `toolkit_contract.yaml`. Grain does not need to be updated to support new tools unless they require a new Grain capability. New capabilities are added to `grain_capabilities.yaml` during the relevant implementation phase.

### Conclave integration shape (forward declaration)
Conclave (the familiar management interface) will need to:
- Read active task state to surface relevant context to familiars
- Write familiar interaction events as task artifacts

When this is designed, Conclave will declare:
```yaml
tool:
  name: conclave
requires:
  capabilities:
    - workflow_state
    - task_results_write
provides:
  events:
    - id: familiar_interaction
      description: "A familiar's response or action on a task"
      artifact_path_template: "docs/working/familiar-logs/{task_id}-{timestamp}.json"
```

### DAEMON integration shape (forward declaration)
DAEMON (the orchestration layer) will need to:
- Drive Grain workflow steps autonomously within supervision bounds
- Read and write packet state
- Pause at gates and surface decisions to operators

DAEMON's contract will require `workflow_state`, `task_results_write`, and a future `workflow_drive` capability to be defined in its design phase.

---

## 7. Versioning

The contract schema version (`grain_contract_version`) follows semver. Grain guarantees:
- **Patch:** no breaking changes to existing capability IDs or artifact schemas
- **Minor:** additive new capabilities or artifact types; existing integrations unaffected
- **Major:** breaking schema changes; sibling tools must update their `requires.grain_version` to adopt

Grain validates `grain_contract_version` during `grain verify ingest` and `grain context link`. If a sibling tool presents a contract with a major version Grain doesn't recognise, it exits with a structured error, not a silent failure.

---

## 8. Discovery Protocol

When a sibling tool needs to locate the active Grain workspace:
1. Read `GRAIN_WORKSPACE` environment variable if set
2. Walk up from the tool's CWD looking for `docs/runtime/PROJECT_RULES.md`
3. If `grain workspace list --format json` is available, call it to enumerate all linked workspaces
4. Use the nearest workspace found; if ambiguous, exit with a structured error listing candidates

This is identical to Grain's own resolution order (see `workspace_model.md`). Sibling tools should not implement their own resolution logic — they should call `grain workspace list` and use its output.
