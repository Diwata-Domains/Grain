# Task: Capability file writer + capabilities/workspace CLI

## Metadata
- **ID:** P35-T08
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T08
- **Packet Path:** tasks/P35-T08/
- **Dependencies:** P35-T01, P35-T02, P35-T03
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** capability discovery layer — implements the on-disk
  `docs/runtime/grain_capabilities.yaml` writer/loader/drift-check (spec §6.3) and the
  `grain capabilities` + `grain workspace` CLI groups (spec §6.4). The registry itself
  (`domain/capabilities.py::CAPABILITIES`) and the version resolver (`grain/version.py`)
  are upstream foundation packets (P35-T03, P35-T02); this packet consumes them, it does
  NOT define them. All new surfaces are always-enveloped (`grain.engine/v1`, §3.5).

## Objective
Build the capability **discovery and reconciliation surface** on top of the in-code
registry: a new `services/capabilities_service.py` that serializes the live
`CAPABILITIES` tuple plus `get_version()` to the canonical
`docs/runtime/grain_capabilities.yaml` file (`write_capabilities_file`), loads it back
(`load`), and detects drift between the file and the live registry (`check_drift`); wire
`grain init` and `grain upgrade` to call the writer; add a `grain capabilities` CLI group
(`list`, `show <id>`, `--check`) that reads **live** from `CAPABILITIES` (never the file)
and exits `6` (`ConfigError`) on drift under `--check`; add a `grain workspace` CLI group
(`list`, `resolve`) that resolves the active workspace via the canonical-marker resolver
(env → walk-up) and emits a payload carrying `link_enumeration: "unsupported"`; and add a
drift check to `grain doctor`. This is the headless half of v0.5.0 contract deliverable
#7 (capability declarations / workspace resolution) and builds the locked
`toolkit_contract.md`'s forward-declared `grain_capabilities.yaml` + `grain workspace
list` artifacts.

## Why This Task Exists
The locked `toolkit_contract.md` v1.0 forward-declares three doc-only artifacts —
`docs/runtime/grain_capabilities.yaml` (with `since:`), `grain workspace list`, and the
`workflow_drive` capability — and Phase 35 **builds** them (spec §0). A familiar (agent)
must be able to discover what Grain can drive headlessly (filter `drive == "headless"`)
and resolve which workspace it is operating in, with **no human and no browser** (spec
§2 principle 1). The registry is generated-from-code and the YAML is a **verifiable
cache, not a rottable source** (spec §6.1, §6.3): `capabilities` reads live from the
binary so a familiar negotiates against the installed engine, never a stale file, and
the drift check guarantees the on-disk cache cannot silently diverge. This packet is the
consumer half of the §6 foundation (P35-T03 owns the registry, P35-T02 owns
`get_version()`); it turns that registry into the contract-conformant discovery surface.

## Scope
- **New `src/grain/services/capabilities_service.py`** (spec §6.3, §10):
  - `write_capabilities_file(root) -> Path` — serialize `CAPABILITIES` (from
    `domain/capabilities.py`, P35-T03) + `get_version()` (from `grain/version.py`,
    P35-T02) to `<root>/docs/runtime/grain_capabilities.yaml` at the **exact locked
    path**. Top-level keys `apiVersion: grain.capabilities/v1`, `grain_contract_version:
    "1.1"`, `grain_version: <get_version()>`, and `capabilities:` (a list, one mapping
    per `Capability` with `id/since/kind/drive/stability/command/description/surfaces`).
  - `load(root) -> dict` — read + YAML-parse the file (raise `ConfigError` /
    `grain.config` on missing/unreadable/malformed file).
  - `check_drift(root) -> list[str]` — compare the file's `(id, since)` set per
    capability **and** top-level `grain_version` against the live registry +
    `get_version()`; return a list of human-readable drift descriptions (empty ⇔ no
    drift). Drift = any added/removed `id`, any changed `since` for an id, or a
    `grain_version` mismatch.
- **`grain init` / `grain upgrade` call the writer** (spec §6.3): both write/refresh
  `grain_capabilities.yaml` via `write_capabilities_file(root)` as part of their normal
  flow. Additive — does not alter other init/upgrade behavior.
- **New `src/grain/cli/capabilities.py`** — `grain capabilities` group (spec §6.4),
  always-enveloped:
  - `grain capabilities list` (alias: bare `grain capabilities`) — `kind:
    CapabilityList`; **LIVE from `CAPABILITIES`**, not the file.
  - `grain capabilities show <id>` — `kind: Capability`; unknown id →
    `UsageError` (`grain.usage`, exit 2) per the §4.3 precedent ("unknown tool →
    `UsageError`") — a bad/unknown capability id is a usage error, not a missing path.
  - `grain capabilities --check` — drift check via `check_drift`; clean → exit 0
    (`status: ok`); drift → `ConfigError` (`grain.config`, **exit 6**).
- **New `src/grain/cli/workspace.py`** — `grain workspace` group (spec §6.4), always-
  enveloped:
  - `grain workspace list` — `kind: WorkspaceList`; resolves via env → walk-up using the
    **canonical-marker resolver** (decision #5 / §6.4 — consume the resolver decided in
    the `grain.toml`-as-marker migration; **MUST NOT hardwire
    `docs/runtime/PROJECT_RULES.md`**). Payload carries
    `link_enumeration: "unsupported"` (spec §6.4, resolves C3).
  - `grain workspace resolve` — echo the single resolved workspace + the reason it was
    chosen (env var vs walk-up marker).
- **`grain doctor` drift check** (spec §6.3) — add a check that calls `check_drift`;
  drift is a doctor **warning** (not a hard failure — the hard-fail path is
  `capabilities --check`).
- **Register `capabilities` + `workspace` groups in `cli/__init__.py`.**
- **New `tests/test_capabilities_service.py` + `tests/test_cli_capabilities_workspace.py`**
  covering the acceptance criteria.
- Reuse Grain idioms: new `.py` files carry the SPDX Apache-2.0 header (Grain was
  relicensed; match the existing header block in `domain/recipe_run.py`); the
  `Capability` dataclass + `VALID_*` frozensets it depends on are owned by P35-T03 and
  imported, not redefined.

## Constraints
- **MVP only (spec §8).** Defer: `grain capabilities reconcile --contract` (reserve the
  verb name only — §6.5); multi-workspace / link enumeration in `workspace list` (hence
  the explicit `link_enumeration: "unsupported"` field — §6.4, C3). Do not build the
  reconcile diff or any "drivable verdict" logic.
- **CLI is canonical, file is derived (spec §5, §6.1).** `capabilities list/show` read
  **live from `CAPABILITIES`**, never from the YAML file. The YAML is a verifiable cache
  produced only by `write_capabilities_file`; **the file is never hand-edited** and the
  CLI never treats it as a source of truth.
- **Marker resolution is NOT hardwired (decision #5, §6.4).** `workspace list/resolve`
  MUST call the canonical-marker resolver from the `grain.toml`-as-marker migration. If
  that migration has not landed, `workspace list` ships **behind it** (gated/no-op) rather
  than hardwiring `PROJECT_RULES.md` — escalate, do not improvise a fragile marker.
- **Drift is the only failure axis here.** `capabilities --check` drift → `ConfigError`
  exit 6; `doctor` drift → warning. No other new exit codes; the §4 taxonomy /
  exit-code mapping is owned by P35-T01 and must not change.
- **Always-enveloped surfaces (§3.5).** `capabilities` and `workspace` are new commands;
  in `--format json` they always emit the `grain.engine/v1` envelope (no `--envelope`
  opt-out) with the correct `kind`. They never call `click.confirm`/`click.prompt`.
- **No network, no daemon, file-backed (spec §2 principle 4).** This packet touches only
  the local filesystem and the in-code registry. No PyPI / version-check work (that is
  P35-T02's `version` packet).
- Exact on-disk path is `docs/runtime/grain_capabilities.yaml` (locked §3.2 path,
  spec §6.3) — do not relocate or rename it.

## Deliverable
- `src/grain/services/capabilities_service.py` with `write_capabilities_file`, `load`,
  `check_drift` as specified in `deliverable_spec.md`.
- `src/grain/cli/capabilities.py` (`list`/`show`/`--check`) and
  `src/grain/cli/workspace.py` (`list`/`resolve`), registered in `cli/__init__.py`.
- `grain init`, `grain upgrade` writing the file; `grain doctor` drift warning.
- `tests/test_capabilities_service.py` + `tests/test_cli_capabilities_workspace.py`.

## Acceptance Criteria
- `write_capabilities_file(root)` writes `<root>/docs/runtime/grain_capabilities.yaml`
  whose parsed content has `apiVersion == "grain.capabilities/v1"`,
  `grain_contract_version == "1.1"`, `grain_version == get_version()`, and a
  `capabilities` list whose `(id, since)` pairs equal those of the live `CAPABILITIES`
  tuple (asserted in a test).
- Immediately after `write_capabilities_file(root)`, `check_drift(root)` returns an empty
  list; after the test mutates the file (drop/rename one capability id, change a `since`,
  or change `grain_version`), `check_drift(root)` returns a non-empty list naming the
  drifted id/field (one assertion per drift kind).
- `grain --format json capabilities` emits a `grain.engine/v1` envelope with
  `kind == "CapabilityList"`, `status == "ok"`, and `data` listing every live
  `CAPABILITIES` entry; `grain --format json capabilities show <known-id>` emits
  `kind == "Capability"` for that id; `grain capabilities show <unknown-id>` exits `2`
  with an `error.code == "grain.usage"` envelope (§4.3 "unknown tool → `UsageError`").
- `grain capabilities --check` exits `0` when the file matches the registry and exits `6`
  with `error.code == "grain.config"` after the file is made to drift (asserted via the
  process exit code and the JSON error envelope).
- `grain --format json workspace list` emits `kind == "WorkspaceList"` with
  `data["link_enumeration"] == "unsupported"`; `grain --format json workspace resolve`
  emits a single resolved workspace plus the reason (`env` vs `walk-up`); both resolve via
  the canonical-marker resolver and neither hardwires `docs/runtime/PROJECT_RULES.md`
  (asserted by pointing the env var / marker and observing the resolved path).
- `grain init` (or `upgrade`) on a fresh workspace produces a
  `docs/runtime/grain_capabilities.yaml` for which `grain capabilities --check` then exits
  `0`; `grain doctor` reports a drift **warning** (not a failure) when the file is stale.
- `uv run pytest tests/test_capabilities_service.py tests/test_cli_capabilities_workspace.py`
  passes with ≥ 8 tests and the full suite shows no regressions.

## Dependencies
- **P35-T01** — `domain/envelope.py::EngineEnvelope` (+ serializer) and the §4 error
  taxonomy / `error_handler` (the `grain.engine/v1` frame and the `UsageError` /
  `ConfigError` / `MissingPathError` classes + exit-code mapping this packet's CLI emits
  and consumes). Spec §3, §4. Consume only — do not redefine.
- **P35-T02** — `grain/version.py::get_version()` (the single version resolver; supplies
  the file's `grain_version` and the drift comparison). Spec §5.2, §10.
- **P35-T03** — `domain/capabilities.py::CAPABILITIES` + the `Capability` dataclass and
  `VALID_CAP_*` frozensets (the one registry this packet serializes/reads). Spec §6.1,
  §6.2.

## Relevant Files
- `src/grain/services/capabilities_service.py` (new) — writer/loader/drift-check.
- `src/grain/cli/capabilities.py` (new) — `capabilities list/show/--check`.
- `src/grain/cli/workspace.py` (new) — `workspace list/resolve`.
- `src/grain/cli/__init__.py` (edit) — register the two groups.
- `src/grain/cli/init.py`, `src/grain/cli/upgrade.py` (edit) — call
  `write_capabilities_file`.
- `src/grain/cli/doctor.py` / `src/grain/services/doctor_service.py` (edit) — drift
  warning check.
- `src/grain/domain/capabilities.py` (reference, from P35-T03) — `CAPABILITIES` +
  `Capability` shape this packet serializes.
- `src/grain/version.py` (reference, from P35-T02) — `get_version()`.
- `src/grain/services/recipe_store.py` / `cli/recipe.py` (reference) — existing
  workspace/path resolution + YAML write idioms to mirror.
- `src/grain/domain/recipe_run.py` (reference) — SPDX header block + frozen-dataclass
  idiom to mirror.
- `docs/working/engine_contract_spec.md` §6.1–§6.4, §3, §8, §9 (contract).

## Escalation Conditions
- If the **canonical-marker resolver** (the `grain.toml`-as-marker migration, decision
  #5) has not landed, ship `grain workspace list/resolve` gated behind it (no-op /
  feature-flagged) and **log a blocker** — do NOT hardwire `docs/runtime/PROJECT_RULES.md`
  as the marker (spec §6.4).
- If the `Capability` dataclass shape from P35-T03 lacks a field this writer must
  serialize (e.g. `drive`/`stability`/`surfaces`), stop and record a change proposal
  against P35-T03 rather than re-defining the registry here (the registry is owned there,
  spec §6.1).
- If implementing the drift check appears to require the file to become a source of truth
  (e.g. CLI reads it for `list`), stop — that violates "CLI is canonical, file is a
  verifiable cache" (§5, §6.1, §6.3); the file is read **only** by `load`/`check_drift`.
- If `multi-workspace` / link enumeration is requested to satisfy a downstream consumer,
  log a change proposal — it is deferred (§6.4, §8), and the
  `link_enumeration: "unsupported"` field exists precisely to flag that boundary.

## Model Recommendation
Sonnet-class is sufficient: the writer/loader/drift-check and two thin CLI groups are
mechanical given the registry (P35-T03) and version resolver (P35-T02) are already
landed, provided the deliverable_spec shapes and the decision-#5 marker constraint are
followed literally. Use an Opus-class model only if the canonical-marker resolver
integration (decision #5) turns out to be unlanded and the gating/escalation path needs
judgment.
