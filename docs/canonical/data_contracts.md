# Data Contracts

## 1. Purpose

This document defines the filesystem-level data contracts for `Grain`.

It governs:
- required document identifiers and structural metadata
- manifest structure
- task packet structure
- task packet metadata expectations
- lifecycle status value contracts
- context bundle contract
- stable naming conventions for v1

It controls decisions about:
- what files and fields are required
- how packet and doc metadata are represented
- what values are valid for packet status
- how structured repository artifacts are named and organized
- what minimum schemas validators must enforce

It does not cover:
- product scope
- architecture component boundaries
- CLI command behavior
- detailed workflow semantics beyond the data that workflow depends on
- provider-specific external integration payloads

Those belong in product scope, architecture, workflow specification, and CLI specification.

---

## 2. Contract Design Principles

1. **Filesystem-readable**
   - all primary artifacts should be understandable in plain files

2. **Minimal but explicit**
   - required structure should be sufficient for validation without overloading v1 with metadata

3. **Stable identifiers**
   - doc IDs, packet IDs, and status values should remain predictable

4. **Separation by artifact type**
   - canonical docs, working docs, runtime docs, and task packets must not collapse into one schema

5. **Validator-friendly**
   - contracts should be easy to check deterministically

---

## 3. Repository Artifact Classes

The repository contains four artifact classes relevant to this document:

1. **documentation artifacts**
2. **task packet artifacts**
3. **template artifacts**
4. **export artifacts**

This document defines required contracts for the first two and minimal expectations for export artifacts.

---

## 4. Canonical Document Contract

Canonical docs are stable markdown documents in:

```text
docs/canonical/
```

#### Required v1 canonical docs

- `product_scope.md`
- `architecture.md`
- `workflow_spec.md`
- `cli_spec.md`
- `data_contracts.md`

#### Contract rules

- filenames are stable
- files must be markdown
- files are considered canonical by path, not by frontmatter
- canonical docs are individually addressable by manifest ID

#### Required doc-level metadata source

Doc metadata should be stored in the manifest, not duplicated in document frontmatter in v1.

---

## 5. Manifest Contract

The manifest is the machine-readable registry of documentation and packet conventions.

#### Required path

```text
docs/runtime/docs_manifest.yaml
```

#### Required top-level sections

- `version:`
- `project:`
- `canonical:`
- `working:`
- `runtime:`
- `tasks:`
- `rules:`

Each top-level section is required in v1.

---

## 6. Manifest Schema

### 6.1 Root Schema

```yaml
version: <integer>

project:
  name: <string>
  type: <string>
  mode: <string>
  storage: <string>
  authority_model: <string>

canonical: <list>
working: <list>
runtime: <list>

tasks:
  root: <string>
  packet_files: <list>
  patch_dir: <string>
  status_values: <list>
  id_format: <string>

rules:
  authority_order: <list>
  canonical_change_policy: <mapping>
  context_policy: <mapping>
  execution_policy: <mapping>
  completion_policy: <mapping>
```

### 6.2 Document Entry Schema

Each entry in `canonical`, `working`, or `runtime` must have:

```yaml
- id: <string>
  path: <string>
  purpose: <string>
  authority: <string>
  editable_by_agents: <boolean>
  read_when: <list[string]>
```

#### Field rules

**`id`**
- unique within the manifest
- lowercase snake_case recommended

**`path`**
- repository-relative path
- must point to a file or directory expected by the layer

**`purpose`**
- one concise sentence

**`authority`**

Allowed descriptive values in v1:
- `highest`
- `high`
- `highest_runtime`
- `high_runtime`
- `secondary`
- `informational`
- `advisory`

The validator may treat these as descriptive labels and rely on `rules.authority_order` for final precedence.

**`editable_by_agents`**
- boolean only

**`read_when`**
- list of scenario strings
- at least one required

### 6.3 Tasks Section Schema

```yaml
tasks:
  root: tasks/
  packet_files:
    - name: <string>
      filename: <string>
      required: <boolean>
  patch_dir: patches/
  status_values:
    - draft
    - ready
    - in_progress
    - blocked
    - review
    - needs_fix
    - done
  id_format: "P<N>-T<NN>-TASK-####"
```

#### Required rules

- `root` must be a repository-relative directory path
- `packet_files` must define packet file expectations
- `patch_dir` must be relative to a packet directory
- `status_values` must include the workflow-approved set
- `id_format` must define packet ID style

### 6.4 Rules Section Schema

**`authority_order`**
- ordered list of path patterns or doc groups from highest to lowest authority

**`canonical_change_policy`**

Required fields:
- `direct_agent_edits_allowed`
- `require_human_approval`
- `proposal_location`

**`context_policy`**

Required fields:
- `load_minimum_required_docs`
- `prefer_task_packet_context`
- `avoid_full_repo_context`

**`execution_policy`**

Required fields:
- `use_task_packets`
- `one_task_one_packet`
- `patch_over_rewrite`
- `preserve_doc_separation`

**`completion_policy`**

Required fields:
- `require_defined_deliverable`
- `require_results_recorded`
- `require_rule_check`
- `require_user_approval`
- `require_verification_pass`
- `allow_close_when_verification_not_run`

---

## 7. Task Packet Contract

Task packets live under:

```text
tasks/P<N>-T<NN>-TASK-####/
```

Each packet directory represents one coherent unit of work.

#### Packet directory naming rule

- must match `P<N>-T<NN>-TASK-####`
- `P<N>` is the phase number (e.g. `P1`, `P2`)
- `T<NN>` is the task number within the phase (e.g. `T01`, `T09`)
- `TASK-####` is the zero-padded four-digit unique packet ID
- The `TASK-####` segment remains the authoritative packet ID for cross-references

Examples:
- `P1-T01-TASK-0001`
- `P2-T07-TASK-0016`

Note: Phase 1 packets (`TASK-0001` through `TASK-0009`) predate this convention
and retain their original names.

---

## 8. Required Packet File Contract

Each packet must define the following files:

- `task.md`
- `context.md`
- `plan.md`
- `deliverable_spec.md`

Optional at creation time but required before closure when applicable:

- `results.md`
- `handoff.md`

Optional directory:

- `patches/`

---

## 9. Packet Metadata Contract

The toolkit may store packet metadata in one or both of the following ways in v1:

- infer from directory + file presence
- store minimal structured metadata within `task.md`

Preferred v1 rule:

- keep packet metadata minimal
- do not require a separate packet JSON/YAML file unless later phases justify it

#### Recommended minimum metadata fields in `task.md`

```markdown
# Task: <title>

## Metadata
- ID: TASK-0001
- Status: draft
- Phase: phase-1
- Dependencies: none
```

Validators should tolerate absent optional metadata fields, but must enforce:

- packet ID
- packet status

---

## 10. Packet Status Contract

Allowed v1 status values:

- `draft`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`

These values must be treated as exact strings.

#### Status normalization rule

- lowercase only
- underscore-separated where applicable

#### Invalid examples

- `in progress`
- `Done`
- `READY`

---

## 11. Packet State Transition Contract

The workflow specification defines the semantics of state transitions. This contract defines the machine-checkable allowed transitions for v1:

```text
draft       -> ready
ready       -> in_progress
in_progress -> blocked
in_progress -> review
blocked     -> draft
blocked     -> ready
review      -> in_progress
review      -> done
```

A validator should treat all other transitions as invalid unless future config explicitly extends them.

---

## 12. Context Bundle Contract

A context bundle is the structured output produced when assembling packet execution context.

A context bundle may be represented as:

- one markdown export
- one directory of copied/referenced materials
- structured JSON metadata plus markdown body

v1 minimum requirement:

- context assembly must identify exactly which sources were selected

#### Required logical sections

- packet reference
- selected packet files
- selected canonical docs
- selected working docs, if any
- selection metadata or rationale summary

#### Minimum metadata fields

- `task_id`
- `generated_at` or equivalent timestamp
- `sources`

---

## 13. File Naming Contracts

### 13.1 Markdown documents

```text
.md
```

### 13.2 Manifest/config documents

```text
.yaml
```

### 13.3 Packet IDs and Directory Names

Packet ID (used in `task.md` metadata and cross-references):

```text
TASK-####
```

Packet directory name (folder under `tasks/`):

```text
P<N>-T<NN>-TASK-####
```

### 13.4 Directory paths

Use repository-relative paths in manifests and generated metadata.

---

## 14. Template Contract

Templates are source artifacts used to generate repository files.

Minimum expected template areas:

- `templates/docs/`
- `templates/tasks/`
- `templates/prompts/` (if prompt templating is included in v1)

#### Contract rule

- templates must not be treated as live project state
- validators should distinguish template presence from generated artifact presence

---

## 15. Validation Minimums

A contract validator in v1 must be able to check:

- required canonical docs exist
- manifest exists and has required top-level sections
- manifest entries contain required fields
- packet directories match required naming format
- required packet files exist
- packet status values are valid
- packet status transitions are valid when change is attempted
- contract-required paths reference existing artifacts where applicable

---

## 16. Forward-Compatibility Rules

To keep v1 practical while allowing evolution:

- new optional fields may be added without breaking old valid artifacts
- required fields must not be renamed casually
- packet ID pattern should remain stable once adopted
- validators should distinguish:
  - missing required field
  - unknown optional field
  - invalid field value

#### Versioning rule

`docs_manifest.yaml` must contain an integer `version`. Future migrations should use this field rather than inferring by file shape.

---

## 17. Adapter Profile Contract

Adapter profiles are declarative, filesystem-visible domain bridges. They live in runtime docs — not in canonical docs or task packets — and are loaded by the adapter system at execution time.

### 17.1 Standard Location

```text
docs/runtime/adapter_profiles.md
```

One file may contain multiple adapter profiles as distinct sections. Custom adapters must be declared in the manifest alongside official ones if they are to be discovered by the adapter loader.

### 17.2 Adapter Profile Schema

Each adapter profile must define:

```yaml
adapter_id: <string>          # stable identifier, e.g. code_adapter, devops_adapter
domain_type: <string>         # broad class, e.g. code, frontend, devops, docs, local_ops
applies_to: <list[string]>    # languages, frameworks, or domain signals, at least one required
```

At least one of the following hint sections must be present:

```yaml
context_priority_rules: <list[string]>
test_or_validation_hints: <list[string]>
```

Optional hint fields:

```yaml
relevant_file_patterns: <list[string]>
ignore_file_patterns: <list[string]>
build_or_run_hints: <list[string]>
review_focus_hints: <list[string]>
default_model_bias: <string | mapping>
```

### 17.3 Official vs Community vs Local Adapters

**Official adapters** are maintained by the Grain project and distributed in the core adapter profiles file. They are subject to the same canonical change process as other runtime docs.

**Community adapters** are maintained outside the core Grain repo but distributed through one dedicated reviewed registry repository. They must conform to the same schema as official adapters. Community adapters are installable only through explicit install flows bounded by the reviewed registry contract; they do not become Official automatically.

**Local/private adapters** are defined locally by users for repo-specific or private domain needs. They must conform to the same schema as official adapters. Local/private adapters may be added to `docs/runtime/adapter_profiles.md` alongside official adapters, or declared in a separate file referenced by the manifest.

Community and local/private adapter `adapter_id` values must not shadow official adapter IDs.

### 17.4 Packet-Level Adapter Fields

Task packets may declare adapters in `task.md` metadata:

```markdown
- Primary Adapter: <adapter_id>
- Secondary Adapters: <adapter_id>, <adapter_id>   # optional
```

Field rules:
- `primary_adapter` is optional; absence means adapter-neutral behavior
- `secondary_adapters` is optional; may be a comma-separated list
- declared adapter IDs must resolve to a known profile at validation time

### 17.5 Adapter Contract Validation Minimums

A contract validator must be able to check:
- `adapter_id` is present and non-empty
- `domain_type` is present and non-empty
- `applies_to` contains at least one entry
- at least one of `context_priority_rules` or `test_or_validation_hints` is present
- packet-level adapter fields reference known `adapter_id` values when declared

### 17.6 Adapter Contract Invariants

Adapters must not define fields that attempt to override:
- packet lifecycle status values
- state transition rules
- closure requirements
- authority hierarchy
- canonical change policy

A validator may reject or warn on adapter profiles that contain unrecognized fields that could be interpreted as overriding these invariants.

---

## 18. OrchestratorPlan Contract

An `OrchestratorPlan` is a structured planning proposal produced by the orchestration service. It lives in the working or working-proposals layer — never in canonical docs or task packets directly. It is a first-class proposal artifact and must pass through the Review/Gate Layer before any accepted candidates are converted to task packets.

### 18.1 Standard Location

OrchestratorPlan artifacts may live in:

```text
docs/working/proposals/
```

or be co-located with a relevant task packet when scoped to a single planning event.

### 18.2 OrchestratorPlan Schema

Minimum fields:

```yaml
plan_id: <string>           # stable identifier, e.g. OP-001
scope_summary: <string>     # human-readable description of the work being planned
produced_by: <string>       # which service, agent, or operator produced this plan
status: <string>            # one of: draft, under_review, accepted, rejected, deferred
active_adapters: <list[string]>  # adapter IDs queried during planning (may be empty)
packet_candidates: <list>   # ordered proposed packet items (see below)
dependency_links: <list>    # dependencies between packet candidates (may be empty)
cross_domain_flags: <list[string]>  # adapter domains that span this plan
split_recommendations: <list[string]>  # candidate packet IDs flagged for decomposition
```

Each `packet_candidates` entry should include:
```yaml
- candidate_id: <string>
  title: <string>
  scope_summary: <string>
  primary_adapter: <string|null>
  depends_on: <list[string]>    # other candidate_ids this depends on
```

### 18.3 OrchestratorPlan Validation Minimums

A validator must be able to check:
- `plan_id` is present and non-empty
- `status` is one of the allowed values
- `packet_candidates` is a list (may be empty)
- each candidate entry contains `candidate_id` and `title`
- `active_adapters` entries resolve to known adapter IDs when populated

### 18.4 OrchestratorPlan Lifecycle Rules

- an OrchestratorPlan with status `draft` or `under_review` must not trigger task packet creation
- an OrchestratorPlan with status `accepted` indicates operator approval; packet creation follows through `grain task create`, not automatically
- an OrchestratorPlan with status `rejected` or `deferred` is retained for audit but has no effect on workflow state
- OrchestratorPlans must not modify canonical docs, the backlog, or the phase plan directly

---

## 19. Deferred Contract Complexity

The following are deferred:

- JSON schema generation
- deep typed frontmatter standards
- rich packet metadata registry files
- database-backed artifact indexing
- content hashing requirements
- advanced inheritance between templates and generated docs

v1 should prefer simple deterministic checks over heavy schema systems.

---

## 20. Decision Boundaries

### 20.1 Decisions This Document Controls

- required artifact names and structures
- manifest schema expectations
- packet directory and file requirements
- allowed status value strings
- machine-checkable transition contract
- minimum validator targets
- adapter profile schema and validation minimums
- OrchestratorPlan schema and validation minimums

### 20.2 Decisions This Document Does Not Control

- why the product exists
- component/module boundaries
- CLI command behavior
- workflow-stage rationale
- provider-specific export formats

Those must conform to these data contracts but are governed elsewhere.
