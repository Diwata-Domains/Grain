# Task: Envelope CLI wiring + opt-in flag

## Metadata
- **ID:** P37-T04
- **Status:** draft
- **Phase:** Phase 37 — Grain-as-Engine Headless Contract
- **Backlog:** P37-T04
- **Packet Path:** tasks/P37-T04/
- **Dependencies:** P37-T01, P37-T02
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** envelope wiring layer — consumes `domain/envelope.py` (P37-T01)
  and `grain/version.py::get_version()` (P37-T02), and threads the `grain.engine/v1`
  frame (engine_contract_spec.md §3) through the CLI emit path; opt-in/negotiated per
  §3.5; no MCP, no new commands, no network.

## Objective
Wire the `grain.engine/v1` envelope into the CLI emit path. Build the **single emit
helper** that prints a payload either bare (legacy) or wrapped in an `EngineEnvelope`
(engine_contract_spec.md §3.1) based on `ctx.obj["envelope"]`; add the `--envelope`
global flag plus the `GRAIN_ENGINE_ENVELOPE` env var with the high→low precedence of
§3.5 (default bare for the pre-existing legacy JSON sites); thread `ctx.obj["kind"]`
so error envelopes can carry the emitting command's `kind` (§3.4); and convert the
`workflow` and `recipe` `--format json` emit sites to route their existing `data` dict
through the helper, proving the verbatim-`data` wrap end to end (§8 MVP). The helper
maps each emit site to its closed-vocabulary `kind` per the §3.2 registry.

## Why This Task Exists
The engine contract's linchpin is "one frame on every surface" (engine_contract_spec.md
§2 principle 2, §3). P37-T01 lands the `EngineEnvelope` dataclass + serializers in
`domain/envelope.py`; this packet is the CLI half of the MVP that **proves the frame
wraps real command output verbatim** (§8: "the one emit helper consumed by all
`workflow` and `recipe` JSON sites — proves verbatim-`data` wrap end to end"). Without
the negotiated opt-in flag (§3.5) and the `ctx.obj["kind"]` thread (§3.4), neither the
format-aware error path (P37-T02/handle_error) nor the always-enveloped new commands can
share one consistent CLI emit surface. This packet establishes that shared surface for
the legacy sites while keeping default output bare (§3.5: 0.5.0 is opt-in, default flip
is deferred to 0.6.0, §8 Deferred).

## Scope
- **The single emit helper** (new, e.g. `cli/emit.py::emit(ctx, kind, data, *, warnings=())`):
  - Reads `ctx.obj["envelope"]` (bool). If `False`: `click.echo(json.dumps(data, indent=2))`
    — byte-for-byte the legacy bare output. If `True`: build an `EngineEnvelope`
    (`status="ok"`, `apiVersion="grain.engine/v1"`, given `kind`, `grain_version` from
    `get_version()` (P37-T02), `command` annotation, `data`, `warnings`), then build the
    serializable frame dict **INLINE** in the §3.1 top-level key order (e.g.
    `dataclasses.asdict(env)` or a hand-ordered dict) and echo it. Do **NOT** call
    `envelope_to_dict()` on the frame — T01 scopes `envelope_to_dict` to the §4.2
    **error** object only (§3.1, §4.2, §10).
  - `kind` must be a member of `VALID_ENGINE_KINDS` (T01); passing an unregistered kind
    is a programming error surfaced by the dataclass `__post_init__` (§3.2).
- **`--envelope` global flag + `GRAIN_ENGINE_ENVELOPE` env** on the root group in
  `cli/__init__.py`, resolved once to a bool on `ctx.obj["envelope"]` with precedence
  **`--envelope` flag → `GRAIN_ENGINE_ENVELOPE=1` env → default bare** (§3.5). `=0`/unset
  env and absent flag → bare.
- **The kind registry mapping (§3.2):** each wired emit site declares its `kind` from the
  §3.2 table (`workflow next`→`WorkflowState`, `workflow run`→`WorkflowStep`,
  `workflow loop`→`WorkflowLoop`, `workflow explain`→`WorkflowDiagnostic`,
  `recipe list`→`RecipeList`, `recipe show`→`RecipeDefinition`,
  `recipe run/next/status/resume/gate`→`RecipeRun`, `recipe scaffold`→`RecipeScaffold`).
  **`workflow reconcile` (`ReconcileReport`) and `workflow guard` (`GuardReport`) are
  DEFERRED — they are NOT wired in this packet** (§8 Deferred lists `guard`/`reconcile`).
- **Wire the `workflow` + `recipe` JSON emit sites** (`cli/workflow.py`, `cli/recipe.py`)
  through the helper: build `data` exactly as today, then call `emit(...)` instead of
  hand-rolled `click.echo(json.dumps(...))`. **MVP wires `workflow next`/`run`/`loop`/
  `explain` + the `recipe` sites ONLY** — `workflow guard`/`reconcile` are deferred (§8).
  **`recipe list`** moves its bare top-level array under `data: {"recipes": [...]}` when
  enveloped (§3.2 "Top-level arrays" note); bare path stays the bare array.
- **`workflow next` has TWO `--format json` emit points** — the empty/failed branch and
  the normal-result branch. **BOTH** must route through the single `emit(...)` helper under
  `kind="WorkflowState"`; neither may keep a hand-rolled `click.echo(json.dumps(...))`
  (§3.1 "one frame on every surface" — no emit site bypasses the helper).
- **Thread `ctx.obj["kind"]`** — each wired command stores its `kind` on `ctx.obj["kind"]`
  at entry (next to `ctx.obj["fmt"]`/`["repo"]`) so the format-aware error path can read it
  for the error envelope's `kind` (§3.4). Unset → `null` is permitted (§3.4).
- New `tests/test_engine_envelope_cli.py` covering the acceptance criteria.

## Constraints
- **MVP only.** Wire **only** the `workflow next`/`run`/`loop`/`explain` JSON sites and the
  `recipe` JSON sites (§8 MVP). `workflow guard` and `workflow reconcile` are **deferred**
  (§8 Deferred explicitly lists `guard`/`reconcile`) — do NOT wire them here. Migrating the
  remaining legacy sites (`task *`, `review *`, `suggest *`, `docs audit`, `status`) is also
  **deferred** (§8 Deferred) — do not touch them.
- **Default stays bare** for these legacy sites in 0.5.0 (§3.5). Do NOT flip the default,
  do NOT emit the stderr deprecation notice (that is 0.6.0, §3.5/§8 Deferred), and do NOT
  build the multi-version `--api grain.engine/vN` negotiator (§3.5, §8 Deferred).
- **No new commands here.** `capabilities`/`workspace`/`version` (always-enveloped, §3.5)
  are other packets; this packet only adds the flag/env and helper they will reuse.
- **No MCP, no HTTP, no network** — CLI-only (§4 file-backed/no-network principle).
- Consume `EngineEnvelope`/serializers/`VALID_ENGINE_KINDS` from `domain/envelope.py`
  (P37-T01); do NOT redefine the frame or the kind set here (§2 principle 2, §10 "none
  re-defines a frame").
- `get_version()` is the only source for `grain_version` (§5.2/§10), provided by
  `grain/version.py` (P37-T02). Import it; never hardcode a version string (§5.2).
<!-- REUSE-IgnoreStart -->
- New `.py` files carry the SPDX Apache-2.0 header (`SPDX-License-Identifier: Apache-2.0`),
<!-- REUSE-IgnoreEnd -->
  matching `src/grain/domain/workflow_loop.py`.
- Grain idioms: CLI is canonical (§2 principle 5); the helper is the single print path —
  no command re-rolls `json.dumps` of an envelope.

## Deliverable
- New `src/grain/cli/emit.py` with the `emit(...)` helper and the §3.2 kind mapping.
- Modified `src/grain/cli/__init__.py`: `--envelope` flag, `GRAIN_ENGINE_ENVELOPE`
  resolution to `ctx.obj["envelope"]`, and `ctx.obj["kind"]` seam.
- Modified `src/grain/cli/workflow.py` + `src/grain/cli/recipe.py`: JSON emit sites
  routed through `emit(...)`, `kind` set on `ctx.obj`, `recipe list` array→`{"recipes":...}`
  under the wrap.
- New `tests/test_engine_envelope_cli.py` per the acceptance criteria.
- Full detail in `deliverable_spec.md`.

## Acceptance Criteria
- With no flag and no env, `grain --format json workflow next` (and `recipe show`/
  `recipe list`) emit the **exact same bare JSON** as before this packet (byte-identical
  `data` dict, no `apiVersion`/`kind`/`status` keys) — proving default-bare back-compat
  (§3.5).
- With `--envelope` (or `GRAIN_ENGINE_ENVELOPE=1`), the same command emits an object with
  top-level keys `{apiVersion:"grain.engine/v1", kind, status:"ok", grain_version, command,
  data, gate:null, error:null, warnings}` where `data` equals the previously-bare dict
  verbatim (§3.1) and `grain_version == get_version()` (no hardcoded string, §5.2). The
  frame dict is built **inline** (e.g. `dataclasses.asdict`), NOT via `envelope_to_dict()`
  (which T01 scopes to the error object only) — asserted by `emit.py` containing no
  `envelope_to_dict(` call on the `EngineEnvelope` frame.
- **Both `workflow next` `--format json` emit points route through `emit()`:** with
  `--envelope`, `workflow next` on an empty/failed workflow (no actionable next step) AND
  `workflow next` on a normal result BOTH emit a `kind:"WorkflowState"` envelope (no bare
  `json.dumps` survives on either branch) — asserted by two distinct tests exercising each
  branch.
- Precedence is asserted: `--envelope` wins over `GRAIN_ENGINE_ENVELOPE=0`; env `=1` with
  no flag envelopes; neither set → bare (§3.5).
- Each wired command emits its §3.2 `kind` (e.g. `workflow next`→`WorkflowState`,
  `recipe show`→`RecipeDefinition`, `recipe list`→`RecipeList`), and `recipe list`'s
  enveloped `data` is `{"recipes": [...]}` while its bare output stays the top-level array
  (§3.2).
- After a wired command runs, `ctx.obj["kind"]` holds that command's kind (asserted via a
  test harness/CliRunner), so the error path can read it (§3.4).
- `uv run pytest tests/test_engine_envelope_cli.py` passes with ≥ 7 tests and the full
  suite shows no regressions.

## Dependencies
- **P37-T01** (envelope + errors foundation) — provides `domain/envelope.py`:
  `EngineEnvelope`, `VALID_ENGINE_KINDS`, `__post_init__`. This packet does not start until
  T01's frame is importable. (Note: `envelope_to_dict` is T01's **error**-object serializer;
  this packet does NOT call it on the frame — it builds the frame dict inline, §3.1/§4.2.)
- **P37-T02** (version resolver) — provides `grain/version.py::get_version()`, the single
  source for the frame's `grain_version` (§5.2/§10). The wrapped frame cannot be built
  without it, so this packet depends on T02.

## Relevant Files
- `src/grain/cli/emit.py` (new) — the single emit helper + §3.2 kind mapping.
- `src/grain/cli/__init__.py` (modify) — `--envelope` flag, `GRAIN_ENGINE_ENVELOPE`,
  `ctx.obj["envelope"]`/`["kind"]`.
- `src/grain/cli/workflow.py` (modify) — route JSON sites through `emit`; set `kind`.
- `src/grain/cli/recipe.py` (modify) — route JSON sites through `emit`; `recipe list`
  array→`{"recipes":...}` under wrap; set `kind`.
- `src/grain/domain/envelope.py` (dependency, P37-T01) — `EngineEnvelope`,
  `VALID_ENGINE_KINDS` (import, do not modify); `envelope_to_dict` is the error-object
  serializer and is NOT called on the frame here.
- `src/grain/version.py` (dependency, P37-T02) — `get_version()` for `grain_version`
  (import, do not modify).
- `tests/test_engine_envelope_cli.py` (new) — CLI wiring + precedence tests.
- `docs/working/engine_contract_spec.md` §3 (frame/registry/migration), §8 (MVP/build
  order) — the contract.

## Escalation Conditions
- If a `workflow`/`recipe` emit site's current `data` shape is not in the §3.2 `kind`
  registry, stop and log a change proposal (add the kind to the spec + T01's
  `VALID_ENGINE_KINDS`) rather than inventing a kind here (§3.2: an unregistered kind is a
  programming error).
- If P37-T01's serializer signature or `EngineEnvelope` field set differs from §3.1, do
  not patch the frame here — record a blocker against T01 (the frame is owned there, §10).
- If wiring a site would require flipping the default to enveloped or emitting the
  deprecation notice to satisfy a test, stop — that is the deferred 0.6.0 behavior (§3.5).

## Model Recommendation
Sonnet-class is sufficient: the helper and flag/env precedence are mechanical against a
fully-resolved spec (§3.5 precedence and the §3.2 kind table are explicit). Reserve
Opus-class only if the `recipe list` bare-array vs wrapped-`{"recipes":...}` split or the
`ctx.obj["kind"]` seam interacts unexpectedly with the existing emit code.
