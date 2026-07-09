# Deliverable Spec: P35-T03 — Capability registry (code source of truth)

## Required Output

### New Files
- `tasks/P35-T03/task.md` — packet metadata/scope ✓
- `tasks/P35-T03/deliverable_spec.md` — this file ✓
- `src/grain/domain/capabilities.py` — `Capability` dataclass + `CAPABILITIES` seed.
- `tests/test_capabilities_registry.py` — tests (≥ 7).

### Modified Files
- none (registry data layer only; the file writer/service, CLI groups, MCP derivation, and
  `doctor` drift check are later P35 packets — engine_contract_spec.md §6.1, §6.3, §6.4,
  §5.3, §8).

## Module contract: `src/grain/domain/capabilities.py`

Carries the SPDX header (Grain was relicensed):

```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
```

### Constants / frozensets (engine_contract_spec.md §6.1)

```python
CAPABILITY_REGISTRY_API_VERSION = "grain.capabilities/v1"   # the FILE's apiVersion
GRAIN_CONTRACT_VERSION = "1.1"                              # bilateral schema (was 1.0)

VALID_CAP_KINDS: frozenset[str] = frozenset({"read", "write", "discovery"})
VALID_CAP_DRIVE: frozenset[str] = frozenset({"headless", "confirm", "interactive"})
VALID_CAP_STABILITY: frozenset[str] = frozenset({"stable", "experimental", "planned"})
VALID_CAP_SURFACES: frozenset[str] = frozenset({"cli", "mcp", "file"})
```

`CAPABILITY_REGISTRY_API_VERSION` and `GRAIN_CONTRACT_VERSION` are defined here (the
registry is the source of truth, §6.1) so the file writer (T08) can serialize them onto the
derived YAML (§6.3) without re-declaring them. This packet does **not** write them anywhere.

### Dataclass (frozen; mirror `workflow_loop.py` / `recipe_run.py`)

```python
@dataclass(frozen=True)
class Capability:
    id: str                                 # stable snake_case id, e.g. "workflow_state"
    since: str | None                       # semver introduced; None iff stability=="planned"
    kind: str                               # in VALID_CAP_KINDS
    drive: str = "headless"                 # in VALID_CAP_DRIVE — "is it headless-safe"
    stability: str = "stable"               # in VALID_CAP_STABILITY
    command: str | None = None              # canonical CLI invocation; None for planned/file-only
    description: str = ""
    surfaces: tuple[str, ...] = ("cli",)    # subset of VALID_CAP_SURFACES

    def __post_init__(self) -> None:
        # id non-empty;
        # kind in VALID_CAP_KINDS else raise naming the value;
        # drive in VALID_CAP_DRIVE else raise naming the value;
        # stability in VALID_CAP_STABILITY else raise naming the value;
        # surfaces non-empty and every member in VALID_CAP_SURFACES else raise naming
        #   the offending member;
        # since<->stability invariant (both directions):
        #   stability == "planned"  iff  since is None
        #   (planned with a since, or non-planned without a since, both raise).
```

Notes:
- The exception type may be a plain `ValueError` (consistent with the dataclass
  `__post_init__` idiom in `workflow_loop.py`); the message MUST name the offending value
  and the field. No new `ForgeError` subclass is introduced by this packet (the error
  taxonomy is owned by the errors/envelope packet, §4).
- Frozen: assigning to any field after construction raises `dataclasses.FrozenInstanceError`
  (mirrors the frozen-dataclass idiom; this gives familiars an immutable registry).
- `surfaces` is a tuple (hashable, frozen-friendly), not a list.

### The `CAPABILITIES` seed (engine_contract_spec.md §6.2)

`CAPABILITIES: tuple[Capability, ...]` with exactly these entries. Per §6.2 this is a
superset of the locked `toolkit_contract.md` example — a v1.0 reader keying on
`id`/`command`/`since` is unaffected (new fields ignored). Each row's `kind`/`drive`/
`surfaces`/`command`/`description` are filled to honor §6.1 and §6.2. The `surfaces` column
below is **PINNED, not implementer's choice**: T06's `tools/list` is a derived view that
filters `CAPABILITIES` by `surfaces ∋ "mcp"` (§5.3), so the `mcp` membership of every row is
a contract this packet locks (it is what makes `tools/list` deterministic). `command`
strings and `description` text remain the implementer's reasonable fill.

| id | since | kind | drive | stability | surfaces (incl.) | command |
|---|---|---|---|---|---|---|
| `workflow_state` | `0.2.0` | read | headless | stable | cli, mcp | `workflow next` |
| `workflow_explain` | `0.4.0` | read | headless | stable | cli, mcp | `workflow explain` |
| `task_create` | `0.1.0` | write | headless | stable | cli, mcp | `task create` |
| `task_results_write` | `0.1.0` | write | headless | stable | cli, file | (file-backed) |
| `verify_submit` | `0.3.0` | write | headless | stable | cli | `verify submit` |
| `verify_ingest` | `0.3.0` | write | headless | stable | cli | `verify ingest` |
| `review_summary` | `0.3.0` | read | headless | stable | cli, mcp | `review summary` |
| `context_link` | `0.4.0` | write | headless | stable | cli | `context link` |
| `suggest_approve` | `0.4.0` | write | **confirm** | stable | cli | `suggest accept` |
| `recipe_run` | `0.5.0` | write | headless | **experimental** | cli, mcp | `recipe run` |
| `recipe_state` | `0.5.0` | read | headless | **experimental** | cli, mcp | `recipe status` |
| `version_check` | `0.5.0` | read | headless | stable | cli, mcp | `version --check` |
| `capabilities_list` | `0.5.0` | **discovery** | headless | stable | cli, mcp | `capabilities` |
| `workspace_list` | `0.5.0` | **discovery** | headless | stable | cli | `workspace list` |
| `workflow_drive` | **None** | write | headless | **planned** | cli, mcp | **None** |

Contract-locked specifics this packet MUST encode (asserted in tests, from §6.2):
- `suggest_approve.drive == "confirm"` (the one non-`headless` MVP drive value).
- `workflow_drive`: `stability == "planned"`, `since is None`, `command is None`
  (the locked doc's forward-declared capability; no `since`/`command`, §6.2 / §0). It still
  carries `surfaces ∋ "mcp"` (it is the drive-loop/recipe-tool MCP capability, §5.4).
- `recipe_run` and `recipe_state`: `stability == "experimental"`, `since == "0.5.0"`.
- `capabilities_list`, `version_check`, `workspace_list`: `since == "0.5.0"`.
- `capabilities_list` and `workspace_list`: `kind == "discovery"`.
- `task_results_write`, `verify_*`, `context_link`: pre-0.5.0 `since` per the table.
- **`version_check` is seeded and OWNED here** (`since == "0.5.0"`, `kind == "read"`,
  `surfaces == ("cli", "mcp")`). T10 (the `grain version` command and the `version_check`
  MCP tool) CONSUMES this entry; it MUST NOT re-add or re-declare the capability.
- **`surfaces ∋ "mcp"` for exactly the mcp-exposed set** — `{workflow_state,
  workflow_explain, task_create, review_summary, recipe_run, recipe_state, capabilities_list,
  version_check, workflow_drive}` — and **not** for the CLI/file-only set —
  `{task_results_write, verify_submit, verify_ingest, context_link, suggest_approve,
  workspace_list}`. This is the contract T06 filters on (§5.3). (`task_status`/`task_close`
  MCP tools map to `task_create`; `review_check` maps to `review_summary` — those capability
  rows already carry `mcp`.)

`since`/`kind`/`drive`/`stability` and the `mcp` membership of `surfaces` above are the
contract this packet locks. `command` strings and `description` text are the implementer's
reasonable fill (any value within the `VALID_*` sets is acceptable for those, beyond passing
`__post_init__`).

## Out of scope for this packet (do NOT build here)
- `services/capabilities_service.py`, `write_capabilities_file(root)`, `load`,
  `check_drift` — the YAML writer/loader/drift checker (§6.1, §6.3) is **T08**, not here.
- Any serialization of `CAPABILITIES` to `docs/runtime/grain_capabilities.yaml` or any
  other file; no file I/O at all.
- The `grain capabilities` (list/show/`--check`) CLI group and `grain workspace
  list/resolve` group (§6.4).
- `McpTool.capability` wiring and `tools/list` derivation (`surfaces ∋ "mcp"`) (§5.3) —
  T06 (the MCP packet) consumes this registry and filters on the pinned `surfaces`; this
  packet only pins/exposes them.
- `doctor` drift check (§6.3).
- `capabilities reconcile --contract` / any verdict type (§6.5, deferred — reserve name
  only).
- Workspace resolution / multi-workspace link enumeration (§6.4, §8 deferred).
- Importing `domain/envelope.py` (T01) or `version.py` (T02) — this module stands alone.

## Acceptance Checklist
- [ ] `Capability` is a frozen dataclass; mutating a field raises `FrozenInstanceError`.
- [ ] `kind`/`drive`/`stability`/`surfaces`-member out of its `VALID_*` set each raise in
      `__post_init__`, message naming the offending value.
- [ ] `since`↔`stability` invariant enforced both directions (planned-with-since raises;
      non-planned-without-since raises); `workflow_drive` and `workflow_state` construct.
- [ ] `CAPABILITIES` contains exactly the §6.2 ids (15 entries) and ids are unique.
- [ ] `suggest_approve.drive == "confirm"`; `workflow_drive` is planned/`since=None`/
      `command=None`; `recipe_run`/`recipe_state` experimental @ `0.5.0`;
      `capabilities_list`/`workspace_list` `kind == "discovery"`.
- [ ] `version_check` is present @ `0.5.0`, `kind == "read"`, `surfaces == ("cli", "mcp")`
      (seeded + owned here; consumed by T10, not re-added).
- [ ] `surfaces ∋ "mcp"` for exactly `{workflow_state, workflow_explain, task_create,
      review_summary, recipe_run, recipe_state, capabilities_list, version_check,
      workflow_drive}` and NOT for `{task_results_write, verify_submit, verify_ingest,
      context_link, suggest_approve, workspace_list}` (makes T06 `tools/list` deterministic).
- [ ] Every `CAPABILITIES` entry passes its `__post_init__` invariants (re-asserted in a
      loop test).
- [ ] `uv run pytest tests/test_capabilities_registry.py` ≥ 7 tests pass; full suite no
      regressions.

## Test cases to include (`tests/test_capabilities_registry.py`)
1. Happy path: a minimal valid `Capability` constructs; fields round-trip; instance is
   frozen (assigning raises `FrozenInstanceError`).
2. Each enumerated field rejects an out-of-set value: bad `kind`, bad `drive`, bad
   `stability`, and a `surfaces` tuple containing a non-`VALID_CAP_SURFACES` member each
   raise, message naming the value.
3. `since`↔`stability` invariant: `stability="planned"` with `since="0.5.0"` raises;
   `stability="stable"` with `since=None` raises; `planned`+`None` and `stable`+`"0.2.0"`
   both succeed.
4. `CAPABILITIES` has the exact §6.2 id set (compare to the literal expected set) and
   `len(CAPABILITIES) == len({c.id for c in CAPABILITIES})` (unique ids).
5. Seed specifics: `suggest_approve.drive == "confirm"`; `workflow_drive`
   planned/`since is None`/`command is None`; `recipe_run`/`recipe_state`
   experimental + `since == "0.5.0"`; `capabilities_list`/`workspace_list`/`version_check`
   `since == "0.5.0"`; `capabilities_list`/`workspace_list` `kind == "discovery"`.
6. Every entry validates: loop over `CAPABILITIES`, assert each `kind ∈ VALID_CAP_KINDS`,
   `drive ∈ VALID_CAP_DRIVE`, `stability ∈ VALID_CAP_STABILITY`, every surface ∈
   `VALID_CAP_SURFACES`, and the `since`↔`stability` invariant holds.
7. Module constants: `CAPABILITY_REGISTRY_API_VERSION == "grain.capabilities/v1"` and
   `GRAIN_CONTRACT_VERSION == "1.1"`.
8. `surfaces ∋ "mcp"` partition: build `{c.id for c in CAPABILITIES if "mcp" in c.surfaces}`
   and assert it equals exactly `{workflow_state, workflow_explain, task_create,
   review_summary, recipe_run, recipe_state, capabilities_list, version_check,
   workflow_drive}` (so T06's `tools/list` derivation, §5.3, is deterministic); also assert
   `version_check` is `kind == "read"`, `since == "0.5.0"`, `surfaces == ("cli", "mcp")`.
