# Deliverable Spec: P37-T05 — engine_error_to_forge extraction

## Required Output

### New Files
- `tasks/P37-T05/task.md` — packet metadata/scope ✓
- `tasks/P37-T05/deliverable_spec.md` — this file ✓
- `tests/test_engine_error_to_forge.py` — mapping + catch-all tests (≥ 6), SPDX header.

### Modified Files
- `src/grain/services/recipe_service.py` — add the pure `engine_error_to_forge` function.
- `src/grain/cli/recipe.py` — collapse `_drive`'s inline `except` chain to delegate to it.

(No new `.py` module: the function joins the existing `recipe_service.py`, which already
<!-- REUSE-IgnoreStart -->
carries the `# SPDX-FileCopyrightText` / `# SPDX-License-Identifier: Apache-2.0` header.)
<!-- REUSE-IgnoreEnd -->

## Function contract: `recipe_service.engine_error_to_forge`

```python
def engine_error_to_forge(exc: RecipeEngineError | RecipeSchemaError) -> ForgeError:
    """Map a recipe engine/loader exception to its canonical ForgeError (spec §4.3).

    Pure: no I/O, no print, no SystemExit — returns the ForgeError; the caller
    (cli/recipe.py::_drive -> _fail, or mcp_service -> _err) decides the sink.

    Accepts a UNION: RecipeSchemaError is a ValueError (domain/recipe.py:63), NOT a
    RecipeEngineError subclass, so it must be in the signature and dispatched by its
    own isinstance branch. The final `return ValidationError(...)` is the exhaustive
    catch-all (F14) ONLY over the RecipeEngineError tree: any unmapped/future
    RecipeEngineError subclass resolves to ValidationError. RecipeSchemaError reaches
    ValidationError via its explicit branch, not the base-class catch-all.
    """
```

**Spec-correction call-out:** engine_contract_spec §4.3 wording ("the `RecipeEngineError`
family already funnels through `recipe.py::_drive`" and the table grouping
`RecipeSchemaError` with the `RecipeEngineError (catch-all)` row) is **inaccurate** about the
hierarchy — `RecipeSchemaError` subclasses `ValueError`, not `RecipeEngineError`. The mapping
*outcome* (`→ ValidationError` / exit 3) is preserved; flag the prose for a follow-up spec
edit. Do NOT reopen §9 decisions.

Imports/types: returns instances from `grain.domain.errors`
(`MissingPathError`, `UsageError`, `ValidationError` — all `ForgeError` subclasses).
Operates on the engine-error classes already defined in `recipe_service.py`
(`RecipeEngineError`, `RecipeNotFoundError`, `RunNotFoundError`, `MissingParamError`,
`GateStateError`) and `RecipeSchemaError` (from `grain.domain.recipe`, already imported).

### Mapping table (spec §4.3 — verbatim, message/detail preserved from today's `_drive`)

| `isinstance(exc, ...)` (most-specific first) | returns | `.code` (P37-T01) | `.exit_code` | message, detail |
|---|---|---|---|---|
| `RecipeNotFoundError` | `MissingPathError` | `grain.missing_path` | 4 | `"unknown recipe", str(exc)` |
| `RunNotFoundError` | `MissingPathError` | `grain.missing_path` | 4 | `"unknown run", str(exc)` |
| `MissingParamError` | `UsageError` | `grain.usage` | 2 | `"missing required recipe param", str(exc)` |
| `GateStateError` | `UsageError` | `grain.usage` | 2 | `"invalid gate decision", str(exc)` |
| `RecipeSchemaError` | `ValidationError` | `grain.validation` | 3 | `"malformed recipe", str(exc)` |
| `RecipeEngineError` (catch-all: any other subclass) | `ValidationError` | `grain.validation` | 3 | `"recipe engine error", str(exc)` |

Implementation shape (dispatch order matters — check subclasses before the
`RecipeEngineError` base so the catch-all stays last; `RecipeSchemaError` is checked
explicitly because it is outside the `RecipeEngineError` tree and would never be reached by
the final `return`):

```python
if isinstance(exc, RecipeNotFoundError):
    return MissingPathError("unknown recipe", str(exc))
if isinstance(exc, RunNotFoundError):
    return MissingPathError("unknown run", str(exc))
if isinstance(exc, MissingParamError):
    return UsageError("missing required recipe param", str(exc))
if isinstance(exc, GateStateError):
    return UsageError("invalid gate decision", str(exc))
if isinstance(exc, RecipeSchemaError):     # ValueError, NOT a RecipeEngineError — explicit
    return ValidationError("malformed recipe", str(exc))
return ValidationError("recipe engine error", str(exc))  # F14 catch-all (RecipeEngineError tree)
```

The `.code` / `.exit_code` are NOT set here — they are the ClassVars P37-T01 puts on each
`ForgeError` subclass (§4.2). This function only chooses the class + message/detail.

## Refactor contract: `cli/recipe.py::_drive`

Before (lines ~85–104) — six engine `except` branches. After:

```python
try:
    return fn(*args, **kwargs)
except ForgeError as exc:
    _fail(exc)                                   # already-typed: pass through unchanged
except RecipeSchemaError as exc:
    _fail(engine_error_to_forge(exc))            # ValueError, NOT in RecipeEngineError tree
except RecipeEngineError as exc:
    _fail(engine_error_to_forge(exc))            # the one shared map (spec §4.3 / §10)
```

- Keep `except ForgeError` FIRST and unchanged — already-typed errors are NOT routed through
  `engine_error_to_forge` (it accepts `RecipeEngineError | RecipeSchemaError`, not
  `ForgeError`).
- **`except RecipeSchemaError` MUST be kept** (do NOT collapse to only `except
  RecipeEngineError`). `RecipeSchemaError` subclasses `ValueError` (domain/recipe.py:63), so
  a lone `except RecipeEngineError` would let it escape `_drive` uncaught — it would surface
  as an unhandled exception / exit 1 instead of the contracted `ValidationError` exit 3. Both
  `except` branches delegate to the SAME `engine_error_to_forge`, so the surfaces still
  share one map. Order between the two delegating branches is immaterial (disjoint trees),
  but `except ForgeError` stays first.
- `_fail` (lines ~64–67) is unchanged: `handle_error(exc)` → `raise SystemExit(code)`.
- Import `engine_error_to_forge` alongside the existing `recipe_service` imports in
  `cli/recipe.py`; `RecipeSchemaError` is already imported there (line ~39) and
  `RecipeEngineError` at line ~46 — keep both.
- Net behavior identical to today: same messages, same exit codes (4/2/3), same
  exhaustiveness over the `RecipeEngineError` tree + the explicit `RecipeSchemaError` path.

## How the MCP side will use it (context only — NOT built in this packet)

The MCP recipe tools (sibling P35 packet) will call
`engine_error_to_forge(exc)` then pass the result to their `_err(tool, forge)` helper
(§4.3 MCP bullet, §5.1). That packet imports this function; this packet only guarantees the
function exists, is pure, and is the same map `_drive` uses. Do not add MCP helpers here.

## Out of scope for this packet (do NOT build here)
- The MCP `_err`/`_ok`/`_gate` helpers, MCP recipe tool registration, or any
  `mcp_service.py` changes (MCP packet).
- `EngineEnvelope` / `ErrorEnvelope` / `to_envelope` / `envelope_to_dict` / format-aware
  `handle_error` (all P37-T01).
- Adding/renaming `ForgeError` subclasses, `code` strings, exit codes, or `VALID_ERROR_CODES`
  (P37-T01).
- Any change to the engine-error class hierarchy in `recipe_service.py`.
- Any envelope/`--envelope` flag, capabilities, version, or non-interactive work.

## Acceptance Checklist
- [ ] `engine_error_to_forge(RecipeNotFoundError("..."))` → `MissingPathError`,
      `.code == "grain.missing_path"`, `.exit_code == 4`, message `"unknown recipe"`.
- [ ] `engine_error_to_forge(RunNotFoundError("..."))` → `MissingPathError`, exit 4,
      message `"unknown run"`.
- [ ] `engine_error_to_forge(MissingParamError("..."))` → `UsageError`,
      `.code == "grain.usage"`, exit 2.
- [ ] `engine_error_to_forge(GateStateError("..."))` → `UsageError`, exit 2.
- [ ] `engine_error_to_forge(RecipeSchemaError("..."))` → `ValidationError`,
      `.code == "grain.validation"`, exit 3, message `"malformed recipe"` (resolved via the
      explicit `RecipeSchemaError` branch — `RecipeSchemaError` is a `ValueError`, accepted
      by the union signature).
- [ ] An unmapped `RecipeEngineError` subclass (existing `InputNotReadyError`/
      `UnknownTokenError`, or an ad-hoc subclass) → `ValidationError`, exit 3 (catch-all).
- [ ] Function is pure: no `SystemExit` raised, nothing printed to stdout/stderr; returns
      the `ForgeError` (asserted via capsys + return-type check).
- [ ] `_drive` body no longer constructs `MissingPathError(`/`UsageError(`/`ValidationError(`
      inline (grep); its only `except` branches are `ForgeError` (pass-through, first),
      `RecipeSchemaError` (delegates to `engine_error_to_forge`), and `RecipeEngineError`
      (delegates to `engine_error_to_forge`). NOTE: `RecipeSchemaError`/`RecipeEngineError`
      DO still appear as the `except` selectors — a "names no longer appear" grep is wrong.
- [ ] `_drive` keeps a dedicated `except RecipeSchemaError`: driving a stub `fn` that raises
      `RecipeSchemaError` still `SystemExit`s with code 3 (proves it is NOT swallowed/escaped
      by collapsing to a lone `except RecipeEngineError`).
- [ ] Existing recipe CLI error tests still pass (unchanged exit codes/messages).
- [ ] `uv run pytest tests/test_engine_error_to_forge.py` ≥ 6 tests pass; full suite no
      regressions.

## Test cases to include (`tests/test_engine_error_to_forge.py`)
1. `RecipeNotFoundError` → `MissingPathError`, code/exit asserted, message `"unknown recipe"`.
2. `RunNotFoundError` → `MissingPathError`, exit 4, message `"unknown run"`.
3. `MissingParamError` → `UsageError`, code/exit 2; `GateStateError` → `UsageError`, exit 2.
4. `RecipeSchemaError` → `ValidationError`, code/exit 3, message `"malformed recipe"`
   (proves the union signature + explicit branch: `RecipeSchemaError` is a `ValueError`,
   not a `RecipeEngineError`).
5. Catch-all: an unmapped `RecipeEngineError` subclass → `ValidationError`, exit 3,
   message `"recipe engine error"`. (Define a throwaway subclass in the test to prove
   future-proofing over the `RecipeEngineError` tree.)
6. Purity: `engine_error_to_forge` returns (does not raise) and prints nothing
   (capsys empty); detail equals `str(exc)` for at least one case.
7. Integration — `RecipeSchemaError` is NOT swallowed: driving a stub `fn` that raises
   `RecipeSchemaError` through the refactored `_drive` still `SystemExit`s with code 3
   (regression guard against collapsing to a lone `except RecipeEngineError`, which would
   let the `ValueError` escape).
8. (Optional integration) Driving a stub `fn` that raises `RecipeNotFoundError` through the
   refactored `_drive` still `SystemExit`s with code 4.
