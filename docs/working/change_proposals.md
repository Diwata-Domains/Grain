# Change Proposals

## 1. Purpose

This document is the working-layer location for proposed changes to canonical documents.

Use this file when:
- implementation reveals a canonical gap
- a canonical rule appears ambiguous
- a canonical document needs revision after review

Do not use this file to:
- make direct canonical changes
- record ordinary implementation notes
- bypass human approval

---

## 2. Proposal Template

## Proposal Title
`<short descriptive title>`

### Affected Canonical Docs
- `docs/canonical/<doc-name>.md`

### Reason
Describe the implementation issue, ambiguity, or gap that triggered the proposal.

### Proposed Change Summary
Describe the proposed canonical update at a summary level.
Focus on the rule, structure, or clarification being requested.

### Impact
Describe expected impact on:
- implementation work
- existing docs
- task packets
- validation behavior
- workflow behavior

### Urgency
Choose one:
- low
- medium
- high

### Suggested Follow-Up
List any follow-up steps needed if the proposal is accepted.

---

## Decision

### Status
Choose one:
- draft
- needs_review
- approved
- rejected
- deferred
- applied

---

### Decision By
`<name or identifier>`

### Decision Date
`<YYYY-MM-DD>`

### Decision Notes
Explain why the proposal was approved, rejected, or deferred.

---

## Application

### Applied By
`<name or identifier>`

### Applied Date
`<YYYY-MM-DD>`

### Notes
- what was updated
- which docs changed
- any follow-up required

---

## CP-008 — Align architecture.md §7.4 ModelProfile fields with v1 implementation

### Affected Canonical Docs
- `docs/canonical/architecture.md`

### Reason
`architecture.md §7.4` specifies `ModelProfile` minimum fields as: `class`, `capabilities`, `cost_class`, `latency_class`, `preferred_stages`, `escalation_targets`. The P4-T08 implementation (`src/forge/domain/routing.py`) derives its schema from the actual `docs/runtime/agent_profiles.md` content and uses different fields: `model_class`, `use_for`, `avoid_for`, `preferred_models`, `escalation_targets`. Fields `cost_class`, `latency_class`, `capabilities`, and `preferred_stages` are absent from `agent_profiles.md` and from the implementation. Raised from TASK-0039 review.

### Proposed Change Summary
Update `architecture.md §7.4` to either: (a) reflect the v1 implemented field names and defer `cost_class`/`latency_class`/`capabilities`/`preferred_stages` explicitly to a later phase, or (b) clarify that the architecture's minimum fields are aspirational and that v1 uses the `agent_profiles.md`-derived schema as an approved simplification.

### Impact
- implementation: no code change required — the implementation is already correct; only the canonical doc needs updating
- existing docs: aligns architecture with implemented domain model
- task packets: downstream routing tasks (P4-T09+) can reference a consistent field contract
- validation behavior: no validator change required
- workflow behavior: reduces confusion when future phases extend the routing domain

### Urgency
low

### Suggested Follow-Up
- Decide whether `cost_class` / `latency_class` should be added to `agent_profiles.md` in a future phase or permanently dropped from the architecture spec.

---

## Decision

### Status
applied

---

### Decision By
`Shaznay`

### Decision Date
`2026-04-05`

### Decision Notes
Apply option (a): reflect v1 implemented field names and explicitly defer the aspirational fields. Implementation is already correct; only the canonical doc needed updating.

---

## Application

### Applied By
`Claude`

### Applied Date
`2026-04-05`

### Notes
- Updated `docs/canonical/architecture.md` §7.4 to list v1 implemented fields (`model_class`, `use_for`, `avoid_for`, `preferred_models`, `escalation_targets`) and explicitly defer `capabilities`, `cost_class`, `latency_class`, `preferred_stages` to a later phase.

---

## CP-003 — Rename `ai-build-toolkit` to `Forge`

### Affected Canonical Docs
- `docs/canonical/product_scope.md`
- `docs/canonical/architecture.md`
- `docs/canonical/cli_spec.md`
- `docs/canonical/workflow_spec.md`
- `docs/canonical/data_contracts.md`

### Reason
The product has evolved from the implementation-name label `ai-build-toolkit` to the brand/product identity `Forge`, aligned with the future Sentinel verification system that will be built using Forge. The current docs and generated metadata should reflect the new identity consistently.

### Proposed Change Summary
Rename the product identity in canonical docs from `ai-build-toolkit` to `Forge`, align the console script to `forge`, and rename the internal Python import package to `forge`.

### Impact
- implementation: clarifies the product identity used in docs, prompts, and roadmap language
- existing docs: canonical docs and working docs stay consistent with the brand rename
- task packets: prompts and task materials should use the new product name
- codebase: import paths and console script now match the new package name
- validation behavior: no functional validator change required, but doc consistency checks should remain aligned
- workflow behavior: reduces ambiguity between the product name and the repository/import package name

### Urgency
medium

### Suggested Follow-Up
- None remaining.

---

## Decision

### Status
applied

---

### Decision By
`codex`

### Decision Date
`2026-04-03`

### Decision Notes
This proposal records the product rename and has been applied to the canonical, working, runtime, and prompt docs, the console script metadata, and the internal Python package rename.

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-03`

### Notes
- Canonical, working, runtime, and prompt docs were updated to use `Forge`.
- The console script metadata was updated to `forge`.
- The internal Python package was renamed to `forge`.

---

## CP-004 — Clarify prompt authority and standardize prompt metadata

### Affected Canonical Docs
- `docs/canonical/workflow_spec.md`

### Reason
The workflow now relies on a growing prompt library for execution, review, and closure. Without an explicit authority rule, future users could incorrectly treat prompts as canonical workflow truth rather than derived workflow assets. The prompt set also needs a minimal metadata convention so future users can select models or surfaces per prompt without embedding vendor-specific assumptions into prompt text.

### Proposed Change Summary
Clarify in the canonical workflow spec that prompts are execution aids, not source-of-truth workflow documents. Standardize a minimal prompt metadata convention in the runtime/template layer covering workflow scope, stage, and recommended model class.

### Impact
- implementation: keeps prompt behavior subordinate to canonical and runtime rules
- existing docs: clarifies where workflow truth lives and where prompt ergonomics may evolve
- task packets: no packet contract change required
- validation behavior: prompt drift becomes easier to identify explicitly
- workflow behavior: supports stable prompt entrypoints and future per-prompt model selection without hardcoding vendor names

### Urgency
medium

### Suggested Follow-Up
- If prompt execution becomes a CLI feature later, formalize machine-readable prompt metadata in a dedicated runtime contract.

---

## Decision

### Status
applied

---

### Decision By
`codex`

### Decision Date
`2026-04-04`

### Decision Notes
The workflow now depends on reusable prompts across executor, reviewer, and closer roles. This clarification was applied to keep prompts clearly below canonical and runtime authority while establishing a minimal metadata pattern for future model-selection support.

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-04`

### Notes
- Added prompt authority language to `docs/canonical/workflow_spec.md`.
- Added prompt authority and naming rules to `docs/runtime/PROJECT_RULES.md`.
- Standardized stable task-level prompt entrypoints under `prompts/task.*.md`.
- Marked short aliases under `prompts/*.md` as deprecated convenience wrappers.
- Added minimal metadata fields to prompt templates for future model-role routing.
- Reduced `templates/prompts/` to authoring scaffolds only and removed role-specific starter duplicates.

---

## CP-005 — Define placeholder CLI stub behavior

### Affected Canonical Docs
- `docs/canonical/cli_spec.md`

### Reason
Phase 4 review of `TASK-0036` found that placeholder CLI subcommands can exist on the command surface before their implementation tasks are complete. Without an explicit rule, unimplemented commands may silently succeed, which is misleading for users and fragile for workflow validation.

### Proposed Change Summary
Clarify that unimplemented CLI commands must not silently succeed. Before a command is implemented, it should either be absent from the surface or return an explicit not-implemented error with a non-zero exit.

### Impact
- implementation: placeholder commands will need a consistent failure behavior
- existing docs: clarifies expected CLI behavior before full feature completion
- task packets: future CLI tasks can follow a stable placeholder policy
- validation behavior: reviewers can treat silent-success stubs as drift instead of a style issue
- workflow behavior: reduces false-positive confidence during phased implementation

### Urgency
medium

### Suggested Follow-Up
- Decide whether the rule should also be mirrored in `docs/runtime/PROJECT_RULES.md` after canonical approval.

---

## Decision

### Status
applied

---

### Decision By
`Shaznay`

### Decision Date
`2026-04-05`

### Decision Notes
Confirmed: unimplemented commands must not silently succeed. Registered stubs must return a not-implemented error with non-zero exit. Rule also to be mirrored in PROJECT_RULES.md.

---

## Application

### Applied By
`Claude`

### Applied Date
`2026-04-05`

### Notes
- Added §5.1 Placeholder Command Behavior to `docs/canonical/cli_spec.md` defining the not-implemented error requirement for registered stubs.

---

## CP-002 — Align packet folder naming contract with implemented compound IDs

### Affected Canonical Docs
- `docs/canonical/data_contracts.md`

### Reason
The current canonical data contract still describes packet directory IDs as `TASK-####`, but the active implementation and runtime manifest use the compound folder naming convention `P<N>-T<NN>-TASK-####`. This creates a canonical/runtime mismatch and makes the packet naming rule ambiguous for future work.

### Proposed Change Summary
Update the canonical packet naming section to explicitly describe the compound folder name as the authoritative on-disk packet directory format, while preserving `TASK-####` as the embedded packet identifier used in metadata and references.

### Impact
- implementation: removes ambiguity for packet creation and lookup
- existing docs: aligns canonical naming text with the runtime manifest and current code
- task packets: folder naming becomes unambiguous for future packet creation
- validation behavior: keeps validators aligned with the implemented naming scheme
- workflow behavior: reduces drift when reading packet paths across phases

### Urgency
medium

### Suggested Follow-Up
- None remaining.

---

## Decision

### Status
applied

---

### Decision By
`codex`

### Decision Date
`2026-04-03`

### Decision Notes
This proposal captures an observed canonical/runtime mismatch and has now been applied.

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-03`

### Notes
- Applied by updating `docs/canonical/data_contracts.md` to use `P<N>-T<NN>-TASK-####` for `tasks.id_format`.

## CP-001 — Task Packet Folder Naming Convention

### Affected Canonical Docs
- `docs/canonical/data_contracts.md`
- `docs/runtime/docs_manifest.yaml` — `tasks.id_format`

### Reason
During Phase 2 execution the folder names `TASK-0010` through `TASK-0015` are
opaque — you cannot tell the phase or backlog position without opening the file.
Human requested that folder names reflect phase and task position for faster
navigation.

### Proposed Change Summary
Change the packet directory naming rule from `TASK-####` to `P<N>-T<NN>-TASK-####`.

Examples:
- `P1-T01-TASK-0001`
- `P2-T07-TASK-0016`

The canonical `TASK-####` ID remains embedded so existing references stay valid.
Validators should accept the full compound name while still treating the `TASK-####`
segment as the authoritative packet ID.

### Impact
- implementation: new packets use new convention; existing Phase 1 packets remain as-is
- docs: `data_contracts.md` Section 7 and 13.3 need updated pattern
- task packets: `task.md` metadata ID field stays `TASK-####`; only folder name changes
- validation: packet ID regex in validators must be updated to match new prefix
- workflow: `current_task.md` `Task Path` field reflects the new folder name

### Urgency
low — applied going forward from Phase 2; existing packets not renamed

### Human Approval
Approved by human instruction during Phase 2 execution (2026-04-02).
Applied from TASK-0016 onward in runtime/docs; canonical doc update was completed by CP-002.

### Suggested Follow-Up
- None remaining.

---

## Decision

### Status
applied

---

### Decision By
Shaznay

### Decision Date
2026-04-02

### Decision Notes
Clarifies ambiguity in task numbers. 

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-03`

### Notes
- Runtime code, manifest, and canonical docs now align on the compound folder format.
- CP-002 was the canonical follow-up and has now been applied.

---

## CP-007 — Define default context tag behavior for no-tag invocation

### Affected Canonical Docs
- `docs/canonical/cli_spec.md`
- `docs/canonical/workflow_spec.md`

### Reason
Phase 4 context commands shared an implemented but undocumented default: when no `--tag` flags were provided, canonical doc selection fell back to the `running_tasks` tag set. That behavior affected `context build`, `context show`, and `context export`, so leaving it implicit created workflow ambiguity.

### Proposed Change Summary
Document that context commands default canonical doc selection to `running_tasks` when no `--tag` flags are supplied. Explicit `--tag` values replace that default for the invocation. Working docs remain opt-in through `--include-working`.

### Impact
- implementation: current code path remains valid and documented
- existing docs: clarifies context-command default behavior
- task packets: later context-dependent tasks can assume the same default explicitly
- validation behavior: review can treat no-tag behavior as documented contract rather than accidental policy
- workflow behavior: reduces ambiguity before downstream automation consumes context commands

### Urgency
medium

### Suggested Follow-Up
- None remaining.

---

## Decision

### Status
applied

### Decision By
`Shaznay`

### Decision Date
`2026-04-05`

### Decision Notes
The implemented default is consistent across all three context commands and matches the intended “running task” context-loading behavior. It is now made explicit in canonical docs.

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-05`

### Notes
- Updated `docs/canonical/cli_spec.md` to document the no-tag default and related context command behavior.
- Updated `docs/canonical/workflow_spec.md` to document default context tag behavior at the workflow level.

---

## CP-006 — Unify context command JSON doc record shapes

### Affected Canonical Docs
- `docs/canonical/cli_spec.md`
- `docs/canonical/workflow_spec.md`

### Reason
`TASK-0037` review found that `forge context build` and `forge context show` emit different JSON shapes for selected document records. `TASK-0038` extended that divergence to `forge context export`. The workflow surface now exposes three shapes and needs a canonical decision before Phase 5 consumers rely on them.

### Proposed Change Summary
Explicitly define distinct, documented JSON shapes per context command:
- `context build` exposes a full bundle-inspection shape with full selected doc records
- `context show` exposes an inspection-oriented summary shape with selected doc identifiers and paths
- `context export` exposes export-source metadata only and must not embed full content bodies in JSON mode

These command-specific shapes are intentional and must remain stable unless canonically revised.

### Impact
- implementation: downstream context commands can serialize against one stable schema
- existing docs: clarifies command output contracts for context commands
- task packets: P4-T07 already implemented; later workflow tasks can target a fixed schema instead of inferring one
- validation behavior: review can detect shape drift as contract drift
- workflow behavior: reduces ambiguity when external tools consume context JSON

### Urgency
medium

### Suggested Follow-Up
- None remaining.

---

## Decision

### Status
applied

### Decision By
`Shaznay`

### Decision Date
`2026-04-05`

### Decision Notes
Raised from `TASK-0037` and extended by `TASK-0038` review. The command purposes differ enough that one forced JSON schema would add unnecessary coupling. The canonical fix is to document distinct JSON surfaces explicitly.

---

## Application

### Applied By
`codex`

### Applied Date
`2026-04-05`

### Notes
- Updated `docs/canonical/cli_spec.md` to define command-specific JSON surfaces for `context build`, `context show`, and `context export`.
- Updated `docs/canonical/workflow_spec.md` to allow distinct documented context representations by workflow purpose.
