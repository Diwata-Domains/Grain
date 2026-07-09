# Task: engine_error_to_forge extraction

## Metadata
- **ID:** P37-T05
- **Status:** draft
- **Phase:** Phase 37 — Grain-as-Engine Headless Contract
- **Backlog:** P37-T05
- **Packet Path:** tasks/P37-T05/
- **Dependencies:** P37-T01
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** typed error model (§4) — extract the one engine-error→`ForgeError`
  map so `recipe.py::_drive` AND the MCP recipe tools call the SAME function; carries the
  §4.3 mapping table verbatim. Stdio-only / no-network / file-backed (no HTTP, no daemon).

## Objective
Extract the inline engine-error→`ForgeError` mapping currently hand-rolled in
`cli/recipe.py::_drive` into a single pure function
`recipe_service.engine_error_to_forge(exc: RecipeEngineError | RecipeSchemaError) ->
ForgeError`, then make **both** `_drive` and the MCP recipe tools call that one function.
This removes the duplicate/divergent error translation between the CLI and MCP recipe
surfaces so a familiar reading `error.code`/`error.exit_code` over MCP lands on the *exact
same* taxonomy class it would get from the CLI exit code (the §4 symmetry promise). No new
error classes, no behavior change to the existing CLI mapping.

**Real-bug note (drives the signature + `_drive` shape):** `RecipeSchemaError` is
`class RecipeSchemaError(ValueError)` (`src/grain/domain/recipe.py:63`), **NOT** a
`RecipeEngineError` subclass. So (a) the function signature must accept
`RecipeEngineError | RecipeSchemaError` and dispatch by `isinstance`, and (b) `_drive` MUST
keep a dedicated `except RecipeSchemaError` branch — it cannot be collapsed into a single
`except RecipeEngineError` catch-all, because a bare `except RecipeEngineError` would let a
`RecipeSchemaError` (a plain `ValueError`) escape `_drive` uncaught and surface as exit 1
instead of the contracted exit 3. This also means the spec §4.3 wording "the
`RecipeEngineError` family already funnels through `recipe.py::_drive`" (and the implied
"every engine error subclasses `RecipeEngineError`") is **inaccurate** for
`RecipeSchemaError`; see the spec-correction callout in "Why This Task Exists".

## Why This Task Exists
Spec §4.3 ("How each surface emits it", recipe-engine-errors row) requires the
`RecipeEngineError` family to funnel through a **pure** `recipe_service.engine_error_to_forge`
so `_drive` and the MCP recipe tools call the *same* function — this is the explicit
resolution of the "errors↔mcp reconcile note" ("extract + both call it"). Spec §10
("One error path") names `recipe_service.engine_error_to_forge` as the single
engine-error→`ForgeError` map called by both `recipe.py::_drive` and the MCP recipe tools.
Today the mapping lives only inline in `_drive` (a chain of `except` clauses); the MCP
recipe tools (added in a sibling P35 packet) need the identical mapping, and duplicating
the `except` chain would let the two surfaces drift. This packet is in the §8 MVP slice
("`engine_error_to_forge` extracted and reused by `_drive` + MCP").

**Spec correction required (call-out, do NOT silently rely on the wrong wording).**
Spec §4.3 describes recipe-engine errors as "the `RecipeEngineError` family" funneling
through `_drive`, and the §4.3 mapping table groups `RecipeSchemaError` under the
`RecipeEngineError` (catch-all) row as if it were a `RecipeEngineError` subclass. It is
not: `RecipeSchemaError` subclasses `ValueError` (`domain/recipe.py:63`), is raised by the
recipe *loader/normalizer* (not the run engine), and is imported into both `recipe_service`
and `cli/recipe.py` separately. The mapping table's *outcome* for `RecipeSchemaError`
(`→ ValidationError` / `grain.validation` / exit 3) is correct and is preserved here; only
the prose's hierarchy claim is wrong. This packet therefore (a) types the function as
`RecipeEngineError | RecipeSchemaError`, (b) keeps `RecipeSchemaError` as its own `_drive`
branch, and (c) flags the §4.3 wording for a follow-up spec edit ("`RecipeSchemaError` is a
`ValueError`, not a `RecipeEngineError`; both are accepted by `engine_error_to_forge` and
both are caught in `_drive`"). This is a wording/doc fix, not a §9 decision reopen.

## Scope
- New function in `src/grain/services/recipe_service.py`:
  - `engine_error_to_forge(exc: RecipeEngineError | RecipeSchemaError) -> ForgeError` — a
    **pure** function (no I/O, no print, no `SystemExit`) that maps an engine/loader
    exception to the correct `grain.domain.errors.ForgeError` subclass per the §4.3 table,
    preserving the message + detail it already produces today (e.g.
    `MissingPathError("unknown recipe", str(exc))`). The union signature is required because
    `RecipeSchemaError` is a `ValueError`, not a `RecipeEngineError` (see real-bug note);
    dispatch is by `isinstance`, most-specific-first.
  - The mapping is the §4.3 table, exactly:

    | engine error | ForgeError | code / exit |
    |---|---|---|
    | `RecipeNotFoundError`, `RunNotFoundError` | `MissingPathError` | `grain.missing_path` / 4 |
    | `MissingParamError`, `GateStateError` | `UsageError` | `grain.usage` / 2 |
    | `RecipeSchemaError`, `RecipeEngineError` (catch-all) | `ValidationError` | `grain.validation` / 3 |

  - The final `return ValidationError(...)` is the catch-all (the F14 invariant, *scoped to
    the `RecipeEngineError` tree*): every **`RecipeEngineError`** subclass — present or
    future — that is not explicitly mapped lands on `ValidationError`. `RecipeSchemaError`
    is handled by its own explicit `isinstance(exc, RecipeSchemaError)` branch (it is NOT in
    the `RecipeEngineError` tree, so it would not be reached by a base-class catch-all). Use
    isinstance ordering (most-specific first; `RecipeSchemaError` before the final return) so
    every accepted input resolves.
- Refactor `src/grain/cli/recipe.py::_drive`: replace the inline per-class `except` chain
  with **two** delegating branches — `except RecipeSchemaError as exc:
  _fail(engine_error_to_forge(exc))` AND `except RecipeEngineError as exc:
  _fail(engine_error_to_forge(exc))`. Both routes go through the one shared function; the
  `RecipeSchemaError` branch is mandatory and MUST be kept (a bare `except RecipeEngineError`
  would NOT catch `RecipeSchemaError`, since it is a `ValueError` outside that hierarchy, and
  the schema error would escape as exit 1). Keep the pre-existing `except ForgeError as exc:
  _fail(exc)` pass-through branch FIRST and unchanged (already-typed errors short-circuit;
  they are NOT routed through the new function). Behavior (messages, exit codes) is identical
  to today.
- Tests in `tests/` (e.g. `tests/test_engine_error_to_forge.py`): assert each engine error
  class maps to the expected `ForgeError` subclass with the expected `.code` / `.exit_code`
  (from P37-T01 ClassVars), and that the catch-all routes an unmapped/future
  `RecipeEngineError` subclass to `ValidationError`.

## Constraints
- **MVP only.** This packet does NOT wire the MCP recipe tools themselves (that is the MCP
  packet's job); it only delivers the shared function and migrates `_drive` to call it, so
  the MCP packet can import and call it. Do not build `_err`/`_ok`/`_gate` MCP helpers here.
- **No taxonomy changes.** Do not add/rename `ForgeError` subclasses, error `code` strings,
  or exit codes — those are owned by P37-T01 (§4.1/§4.2). This packet only *maps onto* the
  existing taxonomy.
- **Pure function.** `engine_error_to_forge` must not print, exit, log, or touch the
  filesystem/network — it returns a `ForgeError`; the caller decides what to do with it
  (`_drive` calls `_fail`; MCP calls `_err`). Honors the stdio-only/no-network contract
  (§2 principle 4) — the function moves no bytes.
- **No `data`-shape or envelope work.** This packet does not touch `EngineEnvelope`,
  `ErrorEnvelope`, `to_envelope`, or `handle_error` — it produces the `ForgeError` those
  consume. (Envelope/error object delivered by P37-T01.)
- **Idioms.** Mirror the existing `_drive` exception ordering; the function lives in
  `recipe_service.py` (the service the CLI command already delegates to, keeping CLI
  canonical per §2 principle 5). The file already carries the SPDX Apache-2.0 header — no
  new `.py` module is required (function added to existing service); the new test file
  carries the SPDX Apache-2.0 header.

## Deliverable
- `src/grain/services/recipe_service.py` gains the pure `engine_error_to_forge` function as
  specified in `deliverable_spec.md`.
- `src/grain/cli/recipe.py::_drive` collapsed to delegate to `engine_error_to_forge`.
- `tests/test_engine_error_to_forge.py` (new) covering the mapping table + catch-all.

## Acceptance Criteria
- `engine_error_to_forge(RecipeNotFoundError("x"))` and `engine_error_to_forge(
  RunNotFoundError("x"))` each return a `MissingPathError` instance whose `.exit_code == 4`
  and `.code == "grain.missing_path"`.
- `engine_error_to_forge(MissingParamError("x"))` and `engine_error_to_forge(
  GateStateError("x"))` each return a `UsageError` with `.exit_code == 2` /
  `.code == "grain.usage"`.
- `engine_error_to_forge(RecipeSchemaError("x"))` returns a `ValidationError` with
  `.exit_code == 3` / `.code == "grain.validation"` (routed through the shared function, via
  its explicit `RecipeSchemaError` branch); a bare/other `RecipeEngineError` subclass not
  listed in the table (e.g. `InputNotReadyError`, `UnknownTokenError`, or an ad-hoc new
  `RecipeEngineError` subclass defined in the test) ALSO returns a `ValidationError`
  (catch-all is exhaustive over the `RecipeEngineError` tree).
- `engine_error_to_forge` is pure: calling it does not raise `SystemExit`, does not write
  to stdout/stderr, and returns (does not raise) the `ForgeError`. (Asserted by capturing
  output and checking the return type.)
- After the refactor, `cli/recipe.py::_drive` contains no per-class `_fail(MissingPathError
  /UsageError/ValidationError(...))` construction inline: the only `except` branches are the
  `ForgeError` pass-through (first, unchanged), an `except RecipeSchemaError` delegating to
  `engine_error_to_forge`, and an `except RecipeEngineError` catch-all delegating to
  `engine_error_to_forge`. Verifiable by grep: `_drive`'s body no longer constructs
  `MissingPathError(`/`UsageError(`/`ValidationError(` and contains exactly the three
  `except` clauses above. (NOTE: `RecipeSchemaError` and `RecipeEngineError` DO still appear
  in `_drive` — as the two `except` selectors — so a "names no longer appear" grep would be
  wrong; the body delegates rather than maps inline.)
- Existing CLI recipe error behavior is unchanged: driving an engine call that raises
  `RecipeNotFoundError` still exits 4 with the same `unknown recipe` message; one that
  raises `RecipeSchemaError` still exits 3 (caught by the dedicated `RecipeSchemaError`
  branch and routed through `engine_error_to_forge`) — i.e. existing recipe CLI tests still
  pass.
- `uv run pytest tests/test_engine_error_to_forge.py` passes with ≥ 6 tests and the full
  suite shows no regressions.

## Dependencies
- **P37-T01** (envelope + typed errors) — provides the `ForgeError` `code`/`exit_code`
  ClassVars and `VALID_ERROR_CODES` that the mapping's return values are asserted against
  (§4.1/§4.2). This packet maps onto that taxonomy; it cannot be verified before T01 lands.

## Relevant Files
- `src/grain/services/recipe_service.py` — engine error classes (`RecipeEngineError` family,
  lines ~97–151) live here; `RecipeSchemaError` is imported from `grain.domain.recipe`
  (recipe.py:63, a `ValueError`) at line ~42; add `engine_error_to_forge` here.
- `src/grain/cli/recipe.py` — `_drive` (lines ~70–104) inline mapping to extract; `_fail`
  (lines ~64–67) stays the CLI-side sink.
- `src/grain/domain/errors.py` — `ForgeError` taxonomy (`MissingPathError`, `UsageError`,
  `ValidationError`); the `code`/`exit_code` ClassVars come from P37-T01.
- `docs/working/engine_contract_spec.md` §4.3 (the mapping table + "extract + both call
  it"), §10 ("One error path"), §8 (MVP slice).
- `tests/test_engine_error_to_forge.py` (new) — mapping + catch-all tests.

## Escalation Conditions
- If P37-T01 has not landed the `ForgeError` `code`/`exit_code` ClassVars, the function can
  still be written and the *type* assertions made, but the `.code`/`.exit_code` assertions
  cannot pass — record a blocker rather than hardcoding code strings here.
- The one KNOWN engine error reaching `_drive` that is NOT a `RecipeEngineError` subclass is
  `RecipeSchemaError` (a `ValueError`); it is handled intentionally here via the union
  signature + dedicated `except` branch (see real-bug note). If extracting reveals a
  *further* error reaching `_drive` that is neither `RecipeEngineError` nor `RecipeSchemaError`
  (so neither `except` would catch it), stop and log a change proposal — do not silently
  widen the function's accepted type beyond `RecipeEngineError | RecipeSchemaError`.
- If the MCP recipe tools' needs imply a different mapping than §4.3 (they should not),
  do not fork the function — raise it as a spec question.

## Model Recommendation
Sonnet-class. This is a mechanical extract-and-delegate refactor against a fixed table with
a clear purity constraint; the §4.3 table and the existing `_drive` chain fully determine
the implementation. Opus is unnecessary unless the catch-all exhaustiveness proof needs
care.
