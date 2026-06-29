# Deliverable Spec: P35-T01 — Engine envelope + typed-error foundation

Grounded in `docs/working/engine_contract_spec.md` §3 (envelope), §4 (errors), §8
(MVP/build order), §9 (resolved decisions), §10 (implementation notes).

## Required Output

### New Files
- `tasks/P35-T01/task.md` — packet metadata/scope ✓
- `tasks/P35-T01/deliverable_spec.md` — this file ✓
- `src/grain/domain/envelope.py` — shared frame + error object + serializers
- `tests/test_engine_envelope.py` — tests (≥ 8)

### Modified Files
- `src/grain/domain/errors.py` — `code`/`exit_code` ClassVars on the 7 subclasses, plus
  the `ERROR_CODE_EXITS` registry + `VALID_ERROR_CODES` frozenset (owned here; §4.2 one-way)
- `src/grain/cli/error_handler.py` — derived `EXIT_CODES` + consistency assert +
  format-aware `handle_error(exc, fmt)`

Every new `.py` file starts with the repo SPDX header:
```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0
```

## Module contract: `src/grain/domain/envelope.py`

### Import preamble (§4.2 — one-way, no cycle)

```python
from __future__ import annotations          # ForgeError annotation resolves lazily

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from grain.domain.errors import ERROR_CODE_EXITS, VALID_ERROR_CODES   # runtime: registry only

if TYPE_CHECKING:                            # type-only — NO runtime import of the class
    from grain.domain.errors import ForgeError
```

`envelope.py` depends on `errors.py`, never the reverse. The only runtime import from
`errors.py` is the data (`ERROR_CODE_EXITS`, `VALID_ERROR_CODES`); the `ForgeError` symbol
is needed only as the `to_envelope` parameter annotation, which `from __future__ import
annotations` keeps as a string (resolved under `TYPE_CHECKING`). `to_envelope` reads
`exc.code`/`exc.exit_code` off the instance, so the class object is never required at
runtime — there is no import cycle. (`ERROR_CODE_EXITS`/`VALID_ERROR_CODES` are DEFINED in
`errors.py`; see the errors edit contract below.)

### Constants

```python
ENGINE_API_VERSION = "grain.engine/v1"     # frame apiVersion (§3.1) — NOT grain-kit version
ERROR_API_VERSION = "grain.error/v1"       # error-object apiVersion (§4.2)

# §3.2 — the registered kind vocabulary (the ~15 shapes). Unregistered kind ⇒ programming
# error caught in __post_init__. Tokens taken verbatim from the §3.2 table.
VALID_ENGINE_KINDS: frozenset[str] = frozenset({
    # --- foundational §3.2 named rows (REQUIRED) ---
    "WorkflowState", "WorkflowStep", "WorkflowLoop", "WorkflowDiagnostic",
    "ReconcileReport", "GuardReport",
    "RecipeList", "RecipeDefinition", "RecipeRun", "RecipeScaffold",
    "CapabilityList", "Capability",
    "WorkspaceList", "VersionInfo",
    # --- legacy-site kinds (§3.2 final row), PROVISIONAL per §3.6 (additive) ---
    # Seeded NOW so downstream packets that emit these do not hit a missing-kind
    # __post_init__ block before their own packet lands. In particular:
    #   T09 (non-interactive) emits "SuggestionList" (suggest accept gate+ok) and
    #        "DocsAuditReport" (docs audit gate+ok);
    #   "TaskState"  — task * sites;  "ReviewReport" — review * sites;
    #   "Status"     — the `status` command.
    # Provisional = the token is reserved/registered here but its `data` shape is owned by
    # the emitting packet; adding/refining stays grain.engine/v1 (§3.6, additive).
    "TaskState", "ReviewReport", "SuggestionList", "DocsAuditReport", "Status",
})

VALID_STATUSES: frozenset[str] = frozenset({"ok", "gate", "error"})
```

> Note: the legacy-site kinds (`TaskState`, `ReviewReport`, `SuggestionList`,
> `DocsAuditReport`, `Status`) are **kept, not trimmed** — they are enumerated here so T09
> and the other legacy-site packets can emit their `kind` against this frozenset without a
> missing-kind block (§3.6 makes registering a kind early purely additive). The foundational
> §3.2 named rows above them are mandatory; the frozenset MUST contain every named kind in
> the §3.2 table **and** these five provisional legacy tokens.
>
> `ERROR_CODE_EXITS` and `VALID_ERROR_CODES` are NOT defined here — they live in
> `errors.py` (§4.1 registry owner) and are imported above (see the errors edit contract).

### `ErrorEnvelope` (the one error shape — §4.2)

```python
@dataclass(frozen=True)
class ErrorEnvelope:
    code: str                              # ∈ VALID_ERROR_CODES (grain.-namespaced)
    message: str
    exit_code: int                         # the int the CLI exits with; portable class token
    detail: str = ""                       # "" ⇒ rendered, but omittable by callers
    apiVersion: str = ERROR_API_VERSION    # "grain.error/v1"

    def __post_init__(self) -> None:
        # raise ValueError/AssertionError if:
        #   code not in VALID_ERROR_CODES
        #   ERROR_CODE_EXITS[code] != exit_code   (code↔exit_code must match the registry)
        #   apiVersion != ERROR_API_VERSION
```

`apiVersion: grain.error/v1` is decoupled from the frame version and from `grain_version`
(§4.2) — the error contract evolves independently. It is the one field beyond the four
contract fields `{code, message, detail, exit_code}`.

### `EngineEnvelope` (the frame — §3.1)

```python
@dataclass(frozen=True)
class EngineEnvelope:
    kind: str | None                       # ∈ VALID_ENGINE_KINDS; None only on error (§3.4)
    status: str                            # ∈ VALID_STATUSES — "ok" | "gate" | "error"
    grain_version: str                     # from get_version(); NEVER hardcoded (caller passes)
    data: dict | list | None = None        # the existing command-specific shape, verbatim
    command: str | None = None             # optional annotation; on MCP carries the tool name
    gate: dict | None = None               # populated iff status == "gate" (§7 shape)
    error: dict | None = None              # populated iff status == "error" (§4.2 dict, verbatim)
    warnings: list = field(default_factory=list)
    apiVersion: str = ENGINE_API_VERSION   # "grain.engine/v1"

    def __post_init__(self) -> None:
        # enforce §3.3 tri-state invariants, ALL of:
        #   status in VALID_STATUSES
        #   (error is not None) iff (status == "error")
        #   (gate  is not None) iff (status == "gate")
        #   (data  is not None) iff (status in {"ok", "gate"})
        #   kind in VALID_ENGINE_KINDS, EXCEPT kind may be None when status == "error"
        #   apiVersion == ENGINE_API_VERSION
```

#### §3.3 tri-state truth table (the invariant `__post_init__` encodes)

| `status` | `data`   | `gate`   | `error`  | process exit |
|----------|----------|----------|----------|--------------|
| `ok`     | present  | null     | null     | 0            |
| `gate`   | present  | present  | null     | 0            |
| `error`  | null     | null     | present  | `exit_code` (1–7) |

This REPLACES the broken `error XOR data` XOR invariant (§3.3 X3): a `gate` is a
successful negative answer with data and exit 0, so the XOR shape would raise on valid
output. The tri-state is representable and never raises on a valid output.

### Serializers (§4.2 — the single construct/serialize path)

```python
def to_envelope(exc: ForgeError) -> ErrorEnvelope:   # ForgeError annotation is TYPE_CHECKING-only
    """Build the portable error object from a ForgeError using its ClassVar
    code/exit_code (read off the instance — no runtime dependency on the ForgeError
    class symbol, so envelope.py stays import-cycle-free). Non-ForgeError handling
    (wrap as GeneralError) is the caller's job in error_handler; this takes a ForgeError."""

def envelope_to_dict(env: ErrorEnvelope) -> dict:
    """Serialize with STABLE key order: apiVersion, code, message, detail, exit_code.
    detail is always emitted (as "" when empty) so consumers see a fixed key set."""
```

> A frame-level serializer for `EngineEnvelope` is NOT required by this packet (the emit
> helper that wraps `data` and the legacy negotiation are a follow-on, §8 deferred). The
> json branch of `handle_error` may build the frame dict inline from the `EngineEnvelope`
> fields. Keep `envelope_to_dict` scoped to the error object.

## Edit contract: `src/grain/domain/errors.py` (§4.2 — OWNS the code registry)

`errors.py` is the **owner** of the code↔exit registry and imports **nothing** from
`envelope.py` (the one-way rule, §4.2). Add `ClassVar`s to `ForgeError` and override per
subclass; the existing `__init__(message, detail)` stays. Then add the registry dict and
the derived frozenset so `envelope.py`/`error_handler.py` import them from here. 1:1 with
§4.1:

```python
from typing import ClassVar

class ForgeError(Exception):
    code: ClassVar[str] = "grain.general"
    exit_code: ClassVar[int] = 1
    # ... existing __init__ unchanged ...

class GeneralError(ForgeError):            code, exit_code = "grain.general", 1
class UsageError(ForgeError):              code, exit_code = "grain.usage", 2
class ValidationError(ForgeError):         code, exit_code = "grain.validation", 3
class MissingPathError(ForgeError):        code, exit_code = "grain.missing_path", 4
class InvalidTransitionError(ForgeError):  code, exit_code = "grain.invalid_transition", 5
class ConfigError(ForgeError):             code, exit_code = "grain.config", 6
class AdapterError(ForgeError):            code, exit_code = "grain.adapter", 7

# §4.1 — the canonical code↔exit_code registry, 1:1 with cli_spec.md §5. Single source,
# defined HERE (not in envelope.py) to keep the import one-way: envelope.py → errors.py.
ERROR_CODE_EXITS: dict[str, int] = {
    "grain.general": 1,
    "grain.usage": 2,
    "grain.validation": 3,
    "grain.missing_path": 4,
    "grain.invalid_transition": 5,
    "grain.config": 6,
    "grain.adapter": 7,
}
VALID_ERROR_CODES: frozenset[str] = frozenset(ERROR_CODE_EXITS)
```
(Shown compact; implement as real `ClassVar` annotations in each class body. The exit
integers are unchanged from today's `EXIT_CODES`. The registry MUST stay consistent with
the per-class ClassVars — the `error_handler.py` import-time assert enforces this.)

## Edit contract: `src/grain/cli/error_handler.py` (§4.3)

- Keep `EXIT_CODES: dict[type, int]` as the single audited table (it already exists).
- Import `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` from `grain.domain.errors` (their owner)
  and `to_envelope`/`envelope_to_dict`/`EngineEnvelope`/`ENGINE_API_VERSION` from
  `grain.domain.envelope`. (`error_handler.py` already imports the `ForgeError` classes.)
- **Consistency assert at module import** (§4.2 — "no drift"): assert that for every
  `ForgeError` subclass in `EXIT_CODES`, `cls.exit_code == EXIT_CODES[cls]` and
  `cls.code in VALID_ERROR_CODES` and `ERROR_CODE_EXITS[cls.code] == cls.exit_code`, and
  that `set(c.code for c in EXIT_CODES) == VALID_ERROR_CODES`. Raise (e.g.
  `AssertionError`) at import if any disagree.
- **`handle_error(exc, fmt="text") -> int`** (format-aware):
  - `fmt == "text"` (default): UNCHANGED behavior — `Error: <message>` (+ `\n  <detail>`
    when present) to **stderr** via `click.echo(..., err=True)`; return the exit code.
    Writes nothing to stdout.
  - `fmt == "json"`: build a `grain.engine/v1` envelope with `status="error"`, `kind=None`
    (or `ctx.obj["kind"]` if already plumbed — §3.4 permits null), `data=None`,
    `error=envelope_to_dict(to_envelope(exc))`, `grain_version=get_version()` — and print
    it as JSON to **stdout**; return the same exit code.
    - If `exc` is not a `ForgeError`, wrap it as `GeneralError(str(exc))` first so json
      mode emits `grain.general`/1, never a bare traceback (§4.3).
  - Both branches return the identical exit int they do today.

> `get_version()` lives in `src/grain/version.py` (P35-T02). If T02 has not landed when
> this packet is implemented, read the version from the existing source in
> `cli/__init__.py` (do not hardcode); record the dependency as a note. The frame field is
> `grain_version` (snake_case), never `grainVersion` (§3.1).

## Error-object JSON shape (§4.2) — exact, emitted under the frame's `error`

```jsonc
{
  "apiVersion": "grain.error/v1",
  "code": "grain.missing_path",
  "message": "unknown recipe",
  "detail": "no recipe 'foo' under docs/recipes/ or bundled",
  "exit_code": 4
}
```

## Frame JSON shape for a CLI json error (§3.1 + §4.3) — what `handle_error(exc,"json")` prints

```jsonc
{
  "apiVersion": "grain.engine/v1",
  "kind": null,
  "status": "error",
  "grain_version": "<get_version()>",
  "command": null,
  "data": null,
  "gate": null,
  "error": { /* the grain.error/v1 object above, verbatim */ },
  "warnings": []
}
```

## Out of scope for this packet (do NOT build — §8 deferred / sibling packets)
- The `--envelope` flag / `GRAIN_ENGINE_ENVELOPE` env negotiation and `ctx.obj["envelope"]`
  (§3.5); wiring any legacy `workflow`/`recipe` JSON emit site through the wrap helper.
- The frame emit helper that wraps `data` for success/ gate paths (the §3.5 "one helper").
- `src/grain/version.py` / `get_version()` extraction (P35-T02).
- `domain/capabilities.py` / capability registry (P35-T03).
- `recipe_service.engine_error_to_forge` extraction and MCP retyping (§4.3 — sibling MCP
  packet); any change to `services/mcp_service.py` or `apps/grain-mcp/main.py`.
- `domain/confirm.py` / `ConfirmationGate` / the §7 gate shape (sibling non-interactive
  packet). This packet only models that `gate` is a `dict|None` slot on the frame.
- Storing `ctx.obj["kind"]` at command entry (§3.4 CLI integration) — permitted to leave
  `kind=null` on error envelopes here.

## Acceptance Checklist
- [ ] 7 subclasses expose `.code`/`.exit_code` per §4.1; `VALID_ERROR_CODES` == those 7
      tokens; mapping asserted in a test.
- [ ] `EngineEnvelope.__post_init__` enforces the §3.3 table: illegal `ok+error`,
      `gate` without `gate`, `error` with `data` or without `error`, unknown `status`,
      and unregistered `kind` (non-error) each raise; the 3 legal forms construct.
- [ ] `kind=None` is accepted only when `status=="error"`; rejected otherwise.
- [ ] `ErrorEnvelope.__post_init__` raises on bad code, on code↔exit_code mismatch, on bad
      apiVersion; a registry-matching pair constructs.
- [ ] `envelope_to_dict(to_envelope(exc))` for all 7 exceptions → keys
      `apiVersion, code, message, detail, exit_code` in stable order, correct values,
      `detail == ""` when none, `apiVersion == "grain.error/v1"`.
- [ ] `handle_error(exc,"text")` → stderr only, returns exit code, byte-identical to prior.
- [ ] `handle_error(exc,"json")` → `grain.engine/v1` `status:"error"` frame to stdout with
      embedded `grain.error/v1` object, `data` null, returns exit code.
- [ ] Non-`ForgeError` in json mode wraps to `grain.general`/1, no traceback.
- [ ] Import-time consistency assert fires when `EXIT_CODES`/ClassVars/`VALID_ERROR_CODES`
      are made to disagree.
- [ ] One-way import: `errors.py` imports nothing from `envelope.py`; importing the two
      modules in either order succeeds; `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` reached via
      `errors.py` are the same objects as those re-imported in `envelope.py` (identity).
- [ ] `VALID_ENGINE_KINDS` contains every §3.2 named kind AND the five provisional legacy
      tokens (`TaskState`, `ReviewReport`, `SuggestionList`, `DocsAuditReport`, `Status`),
      so an `EngineEnvelope(kind="SuggestionList"|"DocsAuditReport", status="gate"/"ok", …)`
      constructs without a missing-kind raise (T09 dependency).
- [ ] `uv run pytest tests/test_engine_envelope.py` ≥ 8 tests pass; full suite no regressions.

## Test cases to include (`tests/test_engine_envelope.py`)
1. Code/exit table: each of the 7 `ForgeError` subclasses → expected `(code, exit_code)`;
   `VALID_ERROR_CODES` equals the 7 tokens; all codes `grain.`-namespaced.
2. `EngineEnvelope` legal forms: `ok`+data, `gate`+data+gate, `error`+error each construct.
3. `EngineEnvelope` illegal forms (parametrized): `ok` with error; `ok`/`gate` with
   `data=None`; `gate` with `gate=None`; `error` with `data` set; `error` with
   `error=None`; unknown `status`; unregistered `kind` (non-error) — each raises.
4. `kind=None` accepted with `status="error"`, rejected with `status="ok"`.
5. `ErrorEnvelope` rejects unknown code, mismatched `code`↔`exit_code`, wrong apiVersion;
   accepts a registry pair.
6. `to_envelope` + `envelope_to_dict` round-trip for all 7 exceptions: exact key set,
   stable order, values, `detail==""` default.
7. `handle_error(exc,"text")` writes to stderr not stdout, returns the exit code (capsys).
8. `handle_error(exc,"json")` writes a parseable `grain.engine/v1` `status:"error"` frame
   to stdout with the embedded `grain.error/v1` object and `data is None`; returns exit.
9. Non-`ForgeError` (e.g. `RuntimeError`) in json mode → `grain.general`/1, no traceback.
10. Consistency invariant: assert the live `EXIT_CODES`/ClassVars/`VALID_ERROR_CODES`
    agree (and, via a local mutated copy, that a deliberate mismatch is detected).
11. No import cycle: import `grain.domain.errors` then `grain.domain.envelope`, and the
    reverse order, both without error; assert `grain.domain.errors` source contains no
    `import ... envelope`; assert `envelope.VALID_ERROR_CODES is errors.VALID_ERROR_CODES`.
12. Provisional legacy kinds present: `{"TaskState","ReviewReport","SuggestionList",
    "DocsAuditReport","Status"} <= VALID_ENGINE_KINDS`, and constructing an `EngineEnvelope`
    with `kind="SuggestionList"`/`"DocsAuditReport"` (status `gate` and `ok`) succeeds.
```
