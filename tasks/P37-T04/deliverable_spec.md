# Deliverable Spec: P37-T04 — Envelope CLI wiring + opt-in flag

## Required Output

### New Files
- `tasks/P37-T04/task.md` — packet metadata/scope ✓
- `tasks/P37-T04/deliverable_spec.md` — this file ✓
- `src/grain/cli/emit.py` — the single emit helper + §3.2 kind mapping (SPDX header).
- `tests/test_engine_envelope_cli.py` — CLI wiring/precedence/kind tests (≥ 7).

### Modified Files
- `src/grain/cli/__init__.py` — `--envelope` flag, `GRAIN_ENGINE_ENVELOPE` env,
  `ctx.obj["envelope"]` (bool) + `ctx.obj["kind"]` (str | None) seam.
- `src/grain/cli/workflow.py` — JSON emit sites routed through `emit(...)`; `kind` set.
- `src/grain/cli/recipe.py` — JSON emit sites routed through `emit(...)`; `recipe list`
  bare-array→`{"recipes": [...]}` under the wrap; `kind` set.

### Consumed (do NOT modify)
- `src/grain/domain/envelope.py` (P37-T01) — `EngineEnvelope`, `VALID_ENGINE_KINDS`.
  Note: `to_envelope`/`envelope_to_dict` are T01's **error**-object construct/serialize path
  (§4.2); this packet does NOT call `envelope_to_dict` on the `EngineEnvelope` frame — it
  builds the frame dict inline (§3.1).
- `src/grain/version.py` (P37-T02) — `get_version()`, the single source for the frame's
  `grain_version` (§5.2/§10).

## Module contract: `src/grain/cli/emit.py`

<!-- REUSE-IgnoreStart -->
Header: `# SPDX-License-Identifier: Apache-2.0` (+ FileCopyrightText line as in
<!-- REUSE-IgnoreEnd -->
`domain/workflow_loop.py`).

```python
import dataclasses
from grain.domain.envelope import EngineEnvelope   # from P37-T01 (frame only; NOT envelope_to_dict)
from grain.version import get_version              # from P37-T02 — §5.2/§10 single source; never hardcode

def emit(
    ctx,
    kind: str,                       # ∈ VALID_ENGINE_KINDS (P37-T01)
    data: dict,                      # the existing per-command shape, VERBATIM (§3.1)
    *,
    command: str = "",               # optional annotation, e.g. "workflow next" (§3.1)
    warnings: list | tuple = (),     # promoted per-command warnings (§3.1)
) -> None:
    """Print `data` bare or wrapped per ctx.obj['envelope'] (§3.5).

    envelope False  -> click.echo(json.dumps(data, indent=2))      # legacy, byte-identical
    envelope True   -> build EngineEnvelope(status='ok', ...) and echo the frame dict built
                       INLINE via dataclasses.asdict(env) (NOT envelope_to_dict, which is the
                       error-object serializer)
    """
```

Behavior:
- `enveloped = bool(ctx.obj.get("envelope", False))`.
- **Bare path** (`enveloped is False`): `click.echo(json.dumps(data, indent=2))` — must be
  byte-for-byte what the site emitted before this packet (§3.5 default-bare back-compat).
- **Wrapped path** (`enveloped is True`): construct
  ```python
  EngineEnvelope(
      apiVersion="grain.engine/v1",   # constant from P37-T01, NOT grain-kit version (§3.1)
      kind=kind,                       # validated in __post_init__ against VALID_ENGINE_KINDS
      status="ok",                     # this helper only emits success; gate/error elsewhere
      grain_version=get_version(),     # §5.2 — never hardcoded
      command=command or None,
      data=data,                       # verbatim, no field renaming (§3.1)
      gate=None,
      error=None,
      warnings=list(warnings),
  )
  ```
  then build the serializable dict **INLINE** and echo it:
  ```python
  click.echo(json.dumps(dataclasses.asdict(env), indent=2))   # or a hand-ordered dict
  ```
  Do **NOT** call `envelope_to_dict(env)` on the frame — `envelope_to_dict` is T01's
  serializer for the §4.2 **error object only** (§4.2/§10). The frame's top-level key order
  follows §3.1 (`apiVersion, kind, status, grain_version, command, data, gate, error,
  warnings`); achieve it via the dataclass field order (`dataclasses.asdict`) or an explicit
  ordered dict in the helper.
- `emit` does not set `ctx.obj["kind"]` itself; the command sets it at entry (§3.4). `emit`
  MAY mirror `kind` onto `ctx.obj["kind"]` as a convenience, but the command-entry set is
  authoritative.

### §3.2 kind mapping (the registry this packet wires)

Each wired emit site passes the literal `kind` from engine_contract_spec.md §3.2:

| Command (this packet) | `kind` | `command` annotation |
|---|---|---|
| `workflow next` | `WorkflowState` | `"workflow next"` |
| `workflow run` | `WorkflowStep` | `"workflow run"` |
| `workflow loop` | `WorkflowLoop` | `"workflow loop"` |
| `workflow explain` | `WorkflowDiagnostic` | `"workflow explain"` |
| `recipe list` | `RecipeList` | `"recipe list"` |
| `recipe show` | `RecipeDefinition` | `"recipe show"` |
| `recipe run` / `next` / `status` / `resume` / `gate` | `RecipeRun` | `"recipe <verb>"` |
| `recipe scaffold` | `RecipeScaffold` | `"recipe scaffold"` |

**DEFERRED (NOT wired in this packet — §8 Deferred):** `workflow reconcile`
(`ReconcileReport`) and `workflow guard` (`GuardReport`). Their kinds remain reserved in
T01's `VALID_ENGINE_KINDS` but no emit site is wired here.

All wired kinds MUST already be members of `VALID_ENGINE_KINDS` in P37-T01. If any is
missing, escalate (do not add it here).

## `cli/__init__.py` changes

### `--envelope` flag + env resolution (§3.5)
On the root group, add a boolean flag and resolve precedence **high→low**:

```python
@click.option("--envelope/--no-envelope", "envelope_flag", default=None,
              help="Wrap --format json output in the grain.engine/v1 envelope.")
# ...
def _resolve_envelope(envelope_flag: bool | None) -> bool:
    if envelope_flag is not None:          # 1. explicit --envelope / --no-envelope wins
        return envelope_flag
    env = os.environ.get("GRAIN_ENGINE_ENVELOPE", "")  # 2. env
    if env == "1":
        return True
    if env == "0":
        return False
    return False                            # 3. default bare for legacy sites (§3.5)

ctx.obj["envelope"] = _resolve_envelope(envelope_flag)
ctx.obj["kind"] = None                      # §3.4 seam, set per-command at entry
```

- `default=None` for the flag is required so "flag absent" is distinguishable from
  `--no-envelope` (which must beat `GRAIN_ENGINE_ENVELOPE=1`).
- Precedence table (asserted in tests):

  | `--envelope` flag | `GRAIN_ENGINE_ENVELOPE` | result |
  |---|---|---|
  | `--envelope` | (any) | enveloped |
  | `--no-envelope` | (any) | bare |
  | absent | `1` | enveloped |
  | absent | `0` | bare |
  | absent | unset | bare |

### `ctx.obj["kind"]` seam (§3.4)
- Initialized to `None` on the root group.
- Each wired command sets `ctx.obj["kind"] = "<its kind>"` at the top of its body (before
  any work that could raise), so a downstream format-aware `handle_error` (P37-T02) can read
  the emitting command's kind for the error envelope. Unset/`None` is permitted (§3.4).

## `cli/workflow.py` / `cli/recipe.py` changes

For each `if fmt == "json":` site listed in §3.2:
1. Build the `data` dict **exactly as today** (no field renaming — §3.1 verbatim).
2. Set `ctx.obj["kind"]` to the site's kind at command entry.
3. Replace `click.echo(json.dumps(data, indent=2))` with
   `emit(ctx, kind="<Kind>", data=data, command="<cmd>")`.
4. Text (`fmt == "text"`) paths are unchanged.

**MVP wired sites:** `workflow next`/`run`/`loop`/`explain` + the `recipe` sites only.
`workflow guard` and `workflow reconcile` are DEFERRED (§8) and must NOT be wired here.

**`workflow next` has TWO `--format json` emit points** — the empty/failed branch (no
actionable next step) and the normal-result branch. **BOTH** must be replaced with a single
`emit(ctx, kind="WorkflowState", data=data, command="workflow next")` call; neither branch
may retain a hand-rolled `click.echo(json.dumps(...))`. Route both through the one helper so
the frame wraps regardless of which branch produced `data` (§3.1 "one frame on every
surface").

**`recipe list` special case (§3.2 "Top-level arrays"):** today emits a bare JSON array.
- Bare path: keep emitting the top-level array unchanged.
- Wrapped path: `data = {"recipes": [...]}`.
Implement by having the `recipe list` site pass the wrapping-aware `data` to `emit` only
when enveloped, or branch inside the site:
```python
if ctx.obj.get("envelope"):
    emit(ctx, kind="RecipeList", data={"recipes": recipes}, command="recipe list")
else:
    click.echo(json.dumps(recipes, indent=2))   # legacy bare array, byte-identical
```
(This is the one site where bare `data` ≠ wrapped `data`; all others pass the same dict to
both paths.)

## Out of scope for this packet (do NOT build here — §8 Deferred)
- Migrating `task *`, `review *`, `suggest *`, `docs audit`, `status` JSON sites to `emit`.
- The 0.6.0 default flip to enveloped; the stderr deprecation notice; the 0.7.0 legacy
  removal (§3.5).
- The multi-version `--api grain.engine/vN` negotiator (§3.5).
- Always-enveloped new commands `capabilities`/`workspace`/`version` (other packets; they
  reuse this flag/env + `emit`, §3.5).
- The format-aware `handle_error` error envelope itself (P37-T02) — this packet only
  provides the `ctx.obj["kind"]` it reads (§3.4).
- Any MCP / HTTP / network code; `status:"gate"` and `status:"error"` emission (gate is
  §7/other packet; error is the error path).

## Acceptance Checklist
- [ ] Default (no flag/env): `workflow next`, `recipe show`, `recipe list` `--format json`
      output is byte-identical to pre-packet bare JSON (no `apiVersion`/`kind`/`status`).
- [ ] `--envelope`: output has `{apiVersion:"grain.engine/v1", kind, status:"ok",
      grain_version, command, data, gate:null, error:null, warnings}`; `data` == the bare
      dict verbatim; `grain_version == get_version()`.
- [ ] `GRAIN_ENGINE_ENVELOPE=1` (no flag) envelopes; `=0` is bare; `--envelope` beats
      `GRAIN_ENGINE_ENVELOPE=0`; `--no-envelope` beats `=1`.
- [ ] `workflow next`→`WorkflowState`, `workflow explain`→`WorkflowDiagnostic`,
      `recipe show`→`RecipeDefinition`, `recipe list`→`RecipeList` kinds present when
      enveloped.
- [ ] Enveloped `recipe list` `data == {"recipes":[...]}`; bare `recipe list` is the
      top-level array.
- [ ] After a wired command runs (CliRunner), `ctx.obj["kind"]` equals that command's kind.
- [ ] Passing an unregistered kind to `emit` raises (via `EngineEnvelope.__post_init__`).
- [ ] The frame dict is built inline (`dataclasses.asdict`/ordered dict): `emit.py` contains
      NO `envelope_to_dict(` call applied to the `EngineEnvelope` frame (grep-asserted).
- [ ] Both `workflow next` `--format json` branches (empty/failed AND normal) emit a
      `WorkflowState` envelope under `--envelope` — neither retains a bare `json.dumps`.
- [ ] `workflow guard` / `workflow reconcile` are NOT wired (no `emit(...)` call for them).
- [ ] `uv run pytest tests/test_engine_envelope_cli.py` ≥ 7 tests pass; full suite no
      regressions.

## Test cases to include (`tests/test_engine_envelope_cli.py`)
1. Bare back-compat: capture `workflow next --format json` with no flag/env; assert parsed
   JSON has no `apiVersion`/`kind`/`status` keys and equals the known bare shape.
2. Enveloped shape: with `--envelope`, assert all top-level frame keys present,
   `apiVersion == "grain.engine/v1"`, `status == "ok"`, `grain_version == get_version()`,
   and `data` equals the bare dict from case 1 verbatim.
3. Precedence matrix: parametrized over the §3.5 table (flag vs env) → enveloped/bare.
4. Kind per site: `workflow next`/`workflow explain`/`recipe show` emit their §3.2 kind
   when enveloped.
5. `recipe list`: enveloped `data == {"recipes": [...]}`; bare path is the top-level array.
6. `ctx.obj["kind"]` is set after a wired command (assert via a CliRunner invoking through
   the root group, or a unit test on the command's entry).
7. (defensive) `emit(ctx, kind="NotARealKind", data={})` with `envelope=True` raises from
   `EngineEnvelope.__post_init__`.
8. Dual emit point: with `--envelope`, `workflow next` on an empty/failed workflow (no
   actionable next step) AND on a normal result both emit a `kind:"WorkflowState"` envelope
   (two assertions / params), proving both branches route through `emit()`.
9. Inline frame dict: assert (e.g. via source grep or by patching) that the enveloped path
   does not call `envelope_to_dict` on the frame — the frame dict is `dataclasses.asdict`
   (or an ordered dict) with §3.1 key order.
