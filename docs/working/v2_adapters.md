# V2 Adapters

## 1. Purpose

This document plans the v2 adapter layer for Forge.

Adapters are the translation layer between the stable Forge workflow and a specific execution domain.

The workflow itself should remain unchanged.
Adapters should affect:
- execution hints
- validation expectations
- file relevance
- test/build tool awareness

Adapters must not redefine:
- task packet lifecycle
- review/close semantics
- canonical authority order

---

## 2. Design Goal

Forge should be able to operate across multiple project types without becoming implicitly Python- or backend-specific.

Adapter design should make that possible while preserving:
- one-task-one-packet workflow
- minimal context loading
- model-agnostic routing
- local filesystem simplicity

---

## 3. Proposed Adapter Contract

Each adapter profile should eventually define these fields:

- `adapter_id`
  - stable identifier such as `code_adapter` or `frontend_adapter`
- `domain_type`
  - broad class such as `code`, `frontend`, `docs`, `spreadsheet`
- `applies_to`
  - languages, frameworks, or project types the adapter is intended for
- `relevant_file_patterns`
  - file and path patterns that should matter more during packet generation and context assembly
- `ignore_file_patterns`
  - file and path patterns that should usually be deprioritized
- `build_or_run_hints`
  - common execution commands or workflow hints, not executable truth
- `test_or_validation_hints`
  - what validation surfaces are usually relevant for this domain
- `review_focus_hints`
  - what reviewers should inspect first for this adapter type
- `context_priority_rules`
  - which files or docs should be preferred when context must stay small
- `default_model_bias`
  - optional hint for model-class preference when the task packet does not override it

The adapter contract should be descriptive, not imperative.
It should guide packet generation, context assembly, execution, and review without changing higher-authority workflow rules.

### Proposed Runtime Location

Recommended location in v2:

- `docs/runtime/adapter_profiles.md` for the human-readable source of truth
- optional future machine-readable derived file only if parsing pressure becomes too high

Reason:
- keeps adapter behavior inspectable and editable like current model-routing configuration
- fits the existing runtime-doc pattern
- avoids introducing a new config format before it is clearly needed

### Minimal Schema Rules

The first v2 contract should enforce only:

- required `adapter_id`
- required `domain_type`
- at least one `applies_to` signal
- at least one context or validation hint section

Do not overdesign the initial schema.
It needs to be specific enough to drive task generation and review, not complete enough to encode every toolchain behavior.

---

## 4. Likely Integration Points

Adapters will likely influence:

- task packet metadata
- context assembly
- model selection guidance
- onboarding flows
- review focus defaults
- future `forge init` / onboarding scaffolds

Adapters should not be required for every v1 packet.
They become useful when Forge is applied across multiple domains or project types.

### Packet-Level Contract Draft

Recommended packet-level shape in v2:

- one `primary_adapter`
- optional `secondary_adapters`

Reason:
- most tasks have one dominant execution domain
- some tasks legitimately cross domains
- this keeps packet inspection simple while still supporting mixed projects

Do not use a flat unbounded adapter list as the primary shape unless real tasks prove the primary/secondary split insufficient.

---

## 5. Initial Adapter Set

Recommended first set:

1. `code_adapter`
   - Python, Rust, backend, CLI tooling
2. `frontend_adapter`
   - TypeScript, JavaScript, React, Storybook, Tauri UI
3. `docs_adapter`
   - Markdown/documentation systems
4. `spreadsheet_adapter`
   - Excel/spreadsheet workflows

These should share one contract shape even if some fields are unused in early versions.

---

## 6. Design Constraints

- adapter behavior must not require a different build loop
- adapter selection must not explode prompt context size by default
- multi-adapter projects must be possible
- adapter data should live in runtime-configurable docs, not hardcoded logic alone
- adapter decisions should stay inspectable in task artifacts
- adapters should narrow execution and review focus, not broaden it
- adapter logic must degrade safely when no adapter is set

## 7. Boundary Rules

Adapters may influence:
- packet drafting guidance
- context prioritization
- review emphasis
- model-class bias
- onboarding recommendations

Adapters must not directly control:
- canonical authority
- task lifecycle transitions
- closeout semantics
- whether canonical changes need proposals
- whether a task may bypass review

If an adapter seems to require changing those rules, the adapter boundary is wrong.

## 8. Default Decision Direction

Current recommended direction:

1. packet shape should be `primary_adapter` plus optional `secondary_adapters`
2. adapter selection should happen at onboarding and remain overrideable per task
3. adapter definitions should live primarily in runtime docs, with code consuming those definitions
4. adapters should bias model routing, not dictate it absolutely

These directions are still working-layer planning guidance until promoted into active work.

---

## 9. Planning Decisions (Resolved in P6-T01)

1. Smallest useful `adapter_profiles` schema:
   - required: `adapter_id`, `domain_type`, `applies_to`
   - required: at least one hint section from `context_priority_rules` or `test_or_validation_hints`
   - other sections optional and may remain empty in early profiles

2. Multi-adapter context selection default:
   - apply `primary_adapter` hints by default
   - include `secondary_adapters` only when explicitly needed by task context or future CLI flags
   - avoid loading both domains into every prompt by default

3. Adapter-aware onboarding profile-file structure:
   - use one shared runtime profile file: `docs/runtime/adapter_profiles.md`
   - represent active adapters as sections within that single file

4. No-adapter fallback behavior:
   - remain adapter-neutral by default
   - do not infer an adapter during execution
   - onboarding may recommend adapters, but packet metadata remains explicit

5. Provider command mapping (`cli_cmd`) decision:
   - do not add `cli_cmd` fields to `agent_profiles.md` in Phase 6
   - keep provider-command selection in a separate future runtime config
   - defer that config design until after adapter contract proving is complete

---

## 10. Recommended First V2 Slice

Recommended first slice:

- add `adapter_profiles.md`
- implement parser/loader
- allow `primary_adapter` in packet metadata
- wire adapter hints into packet generation and review only

Do not begin with:
- full execution branching by adapter
- provider-specific tool automation
- complex adapter inheritance

This keeps the first slice narrow and testable.

---

## 11. Recommended Next Planning Step

When v2 implementation is ready to start:
- convert this into a concrete adapter-contract proposal
- define the runtime location and schema for adapter profiles
- pick one adapter path as the proving ground

Recommended proving ground:
- `code_adapter` first, then `frontend_adapter`
