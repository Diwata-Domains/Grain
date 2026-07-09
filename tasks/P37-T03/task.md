# Task: Capability registry (code source of truth)

## Metadata
- **ID:** P37-T03
- **Status:** draft
- **Phase:** Phase 37 — Grain-as-Engine Headless Contract
- **Backlog:** P37-T03
- **Packet Path:** tasks/P37-T03/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** capability registry layer — the single in-code source of truth
  (`domain/capabilities.py::CAPABILITIES`) that MCP `tools/list`, the on-disk
  `grain_capabilities.yaml`, and the `grain capabilities` CLI all derive from
  (engine_contract_spec.md §6.1). This packet delivers the **registry only** — NO file
  writer, NO CLI, NO MCP wiring (those are later P35 packets; the file writer is T08).

## Objective
Implement the in-code capability registry: a frozen `Capability` dataclass with
`__post_init__` `VALID_*` validation and the seed `CAPABILITIES` tuple, in a new
`src/grain/domain/capabilities.py`. This is the **single** registry the rest of Phase 35
references (engine_contract_spec.md §6.1, §5.3): MCP references capability ids, the YAML
file and `tools/list` become derived views, and `grain capabilities` reads it live. This
packet owns the **shape and the seed data**; it does NOT serialize, write, or expose them.

## Why This Task Exists
The headless contract requires familiars (agents) to discover what Grain can drive without
shelling out or trusting a stale cache (engine_contract_spec.md §6.1). The spec mandates a
**single** registry generated from code and never hand-maintained, resolving the critique's
"two competing registries" defect (§5.3, X4): `McpTool` must *reference* a capability id
rather than carry its own `since`/registry, and the YAML + `tools/list` are derived views.
That single source of truth is `domain/capabilities.py::CAPABILITIES`. This packet is part
of the Phase 35 **foundation** (build order T01 envelope+errors → T02 version → **T03
capabilities**, §8) that the MCP, capabilities-service/CLI, and version packets layer on.

## Scope
- New `src/grain/domain/capabilities.py` (carries the SPDX Apache-2.0 header, Grain was
  relicensed):
  - Module constants (engine_contract_spec.md §6.1):
    - `CAPABILITY_REGISTRY_API_VERSION = "grain.capabilities/v1"` (the file's apiVersion).
    - `GRAIN_CONTRACT_VERSION = "1.1"` (bilateral schema version; was 1.0).
    - `VALID_CAP_KINDS = frozenset({"read", "write", "discovery"})`.
    - `VALID_CAP_DRIVE = frozenset({"headless", "confirm", "interactive"})`.
    - `VALID_CAP_STABILITY = frozenset({"stable", "experimental", "planned"})`.
    - `VALID_CAP_SURFACES = frozenset({"cli", "mcp", "file"})`.
  - `Capability` frozen dataclass with `__post_init__`. Reuse the
    `__post_init__` + `VALID_*` frozenset validation idiom from
    `workflow_loop.py` / `recipe_run.py` (those are plain `@dataclass`); for the
    `@dataclass(frozen=True)` precedent specifically, mirror
    `src/grain/domain/office_writes.py` (the frozen dataclass already in
    `domain/`). `Capability` is `frozen=True` per §6.1:
    - Fields per §6.1: `id`, `since: str | None`, `kind`, `drive="headless"`,
      `stability="stable"`, `command: str | None = None`, `description=""`,
      `surfaces: tuple[str, ...] = ("cli",)`.
    - `__post_init__` validates each enumerated field against its `VALID_*` set and
      enforces the `since`↔`stability` invariant from §6.1 (`since is None` iff
      `stability == "planned"`).
  - `CAPABILITIES: tuple[Capability, ...]` — the seed registry per §6.2.
- **Per-capability `surfaces` are PINNED here (not implementer's choice).** Every
  capability that is exposed by an MCP tool MUST carry `surfaces ∋ "mcp"`, because T06's
  `tools/list` is a derived view that filters `CAPABILITIES` by `surfaces ∋ "mcp"` (§5.3)
  and is only deterministic if T03 pins these. The mcp-exposed capabilities are exactly:
  `workflow_state`, `workflow_explain`, `task_create`, `review_summary`, `recipe_run`,
  `recipe_state`, `capabilities_list`, `version_check`, `workflow_drive` (the last is the
  drive-loop/recipe-tool capability, §5.4; it carries `mcp` even though it is `planned`).
  The MCP tools `task_status`/`task_close` map to the `task_create` capability and
  `review_check` maps to `review_summary`, so those capabilities carry `mcp` too.
- **`version_check` is SEEDED and OWNED by this packet** (`0.5.0`, `read`,
  `surfaces` = `cli, mcp`). T10 (the `grain version` command + the `version_check` MCP
  tool) CONSUMES this seed entry — it does NOT re-add or re-declare the capability. Keep
  the entry exactly as specified in `deliverable_spec.md`.
- New `tests/test_capabilities_registry.py` covering the criteria below.
- Reuse Grain idioms: frozen dataclass + `__post_init__` + `VALID_*` frozensets. Mirror the
  `__post_init__` + `VALID_*` validation pattern from `src/grain/domain/workflow_loop.py`
  (plain `@dataclass`), and the `@dataclass(frozen=True)` precedent from
  `src/grain/domain/office_writes.py`.

## Constraints
- **MVP only (§8).** This packet is the registry data structure and seed **only**. Do NOT
  build: `services/capabilities_service.py` / `write_capabilities_file` (that is the file
  writer — explicitly out of this packet, lands in T08); the `grain capabilities`
  list/show/`--check` CLI group; the `grain workspace list/resolve` group; the `doctor`
  drift check; any MCP `tools/list` derivation or `McpTool.capability` wiring; any YAML
  serialization. No file I/O of any kind.
- **`capabilities reconcile` is deferred (§6.5).** Do NOT model a reconcile/verdict type
  or a `requires:` diff. Reserve the name only — nothing in this packet implements it.
- **Multi-workspace / link enumeration deferred (§6.4, §8).** `workspace_list` appears in
  the seed as a capability entry; do NOT model workspace resolution here.
- The registry is the source of truth — the YAML file is a derived view written elsewhere
  (§6.1, §6.3). Do NOT read or write `docs/runtime/grain_capabilities.yaml` here.
- New `.py` files carry the SPDX header
  (`# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison` /
<!-- REUSE-IgnoreStart -->
  `# SPDX-License-Identifier: Apache-2.0`).
<!-- REUSE-IgnoreEnd -->
- stdio-only / no-network / file-backed contract: this module has no network, no daemon,
  no HTTP, and no on-disk side effects (engine_contract_spec.md §2 principle 4).

## Deliverable
- `src/grain/domain/capabilities.py` with `CAPABILITY_REGISTRY_API_VERSION`,
  `GRAIN_CONTRACT_VERSION`, the four `VALID_CAP_*` frozensets, the `Capability` frozen
  dataclass with validating `__post_init__`, and the `CAPABILITIES` seed tuple, exactly as
  specified in `deliverable_spec.md`.
- `tests/test_capabilities_registry.py` with the cases enumerated in the acceptance
  criteria.

## Acceptance Criteria
- Constructing a `Capability` with `kind` ∉ `VALID_CAP_KINDS`, `drive` ∉
  `VALID_CAP_DRIVE`, `stability` ∉ `VALID_CAP_STABILITY`, or any `surfaces` member ∉
  `VALID_CAP_SURFACES` each raises in `__post_init__`, and the error message names the
  offending value; a valid `Capability` constructs successfully and is immutable (assigning
  to a field raises `FrozenInstanceError`).
- The `since`↔`stability` invariant is enforced both ways: `stability == "planned"` with a
  non-`None` `since` raises, and `stability != "planned"` with `since is None` raises;
  `workflow_drive` (planned, `since=None`) and `workflow_state` (stable, `since="0.2.0"`)
  both construct.
- `CAPABILITIES` contains exactly the §6.2 seed ids: `workflow_state`, `workflow_explain`,
  `task_create`, `task_results_write`, `verify_submit`, `verify_ingest`, `review_summary`,
  `context_link`, `suggest_approve`, `recipe_run`, `recipe_state`, `version_check`,
  `capabilities_list`, `workspace_list`, `workflow_drive`; ids are unique (a test asserts
  `len(CAPABILITIES) == len({c.id for c in CAPABILITIES})`).
- The seed encodes the §6.2 specifics: `suggest_approve.drive == "confirm"`;
  `workflow_drive.stability == "planned"` with `since is None` and `command is None`;
  `recipe_run`/`recipe_state` are `stability == "experimental"` with `since == "0.5.0"`;
  `capabilities_list`, `workspace_list`, `version_check` are `since == "0.5.0"`;
  `capabilities_list` and `workspace_list` are `kind == "discovery"`.
- **Every mcp-exposed capability carries `surfaces ∋ "mcp"`** (makes T06 `tools/list`
  deterministic, §5.3). A test asserts `"mcp" in c.surfaces` for each id in the exact set
  `{workflow_state, workflow_explain, task_create, review_summary, recipe_run, recipe_state,
  capabilities_list, version_check, workflow_drive}`, and conversely asserts the
  CLI-only/file-only capabilities (`task_results_write`, `verify_submit`, `verify_ingest`,
  `context_link`, `suggest_approve`, `workspace_list`) do NOT carry `"mcp"`.
- `version_check` is present with `since == "0.5.0"`, `kind == "read"`, and
  `surfaces == ("cli", "mcp")` (seeded + owned here; consumed by T10, not re-added).
- Every entry in `CAPABILITIES` round-trips its own `__post_init__` (constructed in the
  tuple, so import-time validation already holds) — a test re-asserts each entry's
  enumerated fields are members of their `VALID_*` set and the `since`↔`stability`
  invariant holds for all entries.
- `uv run pytest tests/test_capabilities_registry.py` passes with ≥ 7 tests (including the
  `surfaces ∋ "mcp"` assertion above) and the full suite shows no regressions.

## Dependencies
- none (foundation packet; T01 envelope and T02 version land in parallel — this module
  imports neither).

## Relevant Files
- `src/grain/domain/capabilities.py` (new) — `Capability` dataclass + `CAPABILITIES` seed.
- `tests/test_capabilities_registry.py` (new) — dataclass validation + seed tests.
- `src/grain/domain/workflow_loop.py` (reference) — `__post_init__` + `VALID_*` frozenset
  validation idiom to mirror (plain `@dataclass`); also the SPDX header to copy.
- `src/grain/domain/recipe_run.py` (reference) — same idiom, additional `__post_init__`
  cross-field validation pattern (also plain `@dataclass`).
- `src/grain/domain/office_writes.py` (reference) — the `@dataclass(frozen=True)` precedent
  in `domain/` to mirror for `Capability`'s frozen-ness.
- `docs/working/engine_contract_spec.md` §6.1 (dataclass shape + invariants), §6.2 (seed),
  §5.3 (MCP references the id, not a second registry), §8 (build order / MVP), §6.5
  (reconcile deferred).

## Escalation Conditions
- If a seed capability in §6.2 cannot be expressed without a field the §6.1 dataclass does
  not define, stop and log a change proposal rather than adding a field — the dataclass
  shape is a contract surface other packets (MCP, file writer) bind to.
- If the §6.1 `since`↔`stability` invariant conflicts with any seed entry in §6.2 (it
  should not), record a blocker rather than relaxing the invariant.
- If a downstream packet (file writer T08, MCP, CLI) appears to need a writer/serializer or
  CLI surface from this module, stop — those are out of scope by design; do not pull them
  forward into this packet.

## Model Recommendation
Sonnet-class is sufficient: the dataclass + `__post_init__` validation is mechanical and
the seed is enumerated literally in `deliverable_spec.md`. Opus-class is warranted only if
the `since`↔`stability` invariant edge cases or the seed field-by-field encoding need
careful cross-checking against §6.2.
