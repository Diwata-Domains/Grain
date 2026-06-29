# Task: Engine envelope + typed-error foundation

## Metadata
- **ID:** P35-T01
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T01
- **Packet Path:** tasks/P35-T01/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** the foundational slice — `grain.engine/v1` transport frame
  (§3) + the one `grain.error/v1` typed-error object (§4). Landed FIRST per build order
  (§8); T02 (version) and T03 (capabilities) layer on this. Frame is a stdout/`structuredContent`
  transport only — it changes no on-disk artifact (§2 principle 4); stdio-only, no network, no auth.

## Objective
Build the shared engine-contract foundation in a new `src/grain/domain/envelope.py`:
the `EngineEnvelope` frozen dataclass (`apiVersion: grain.engine/v1`, closed-vocabulary
`kind`, tri-state `status`, `grain_version`, optional `command`, `data`, `gate`, `error`,
`warnings`) with `__post_init__` enforcing the §3.3 tri-state invariants, plus the
`ErrorEnvelope` frozen dataclass (`apiVersion: grain.error/v1`, `grain.`-namespaced
`code`, `message`, `detail`, `exit_code`) and the single construct/serialize path
`to_envelope(exc)` / `envelope_to_dict(env)` (§4.2). Promote `code`/`exit_code` to
`ClassVar`s on the 7 `ForgeError` subclasses and add `VALID_ERROR_CODES` (§4.1, 1:1 with
exit codes). Make `cli/error_handler.py::handle_error` format-aware (text unchanged →
stderr; json → a `status: error` envelope to stdout, still exiting the code) and add a
startup consistency assert that `EXIT_CODES` and the registry never drift.

## Why This Task Exists
The headless surface is incoherent: ~15 hand-rolled top-level JSON shapes, no version, no
discriminator, and an untyped error blob (§1). A familiar (agent) cannot reliably know
which schema/version it received or distinguish error classes across surfaces. The engine
contract fixes the frame once so MCP, capabilities, non-interactive, and version all
compose on it (§2). This packet delivers deliverable #1 and #2 of the build order (§8):
the shared `domain/envelope.py` everything imports, and the typed-error anchor (§4) whose
`ErrorEnvelope` the frame embeds verbatim. It is the linchpin for hosted Apex / agent
routing (§1). All design decisions are RESOLVED (§9) — OD-1 (`grain.`-namespaced codes)
and OD-2 (tri-state `status`) are confirmed; do not reopen them.

## Scope
- **Import direction (§4.2 — no runtime cycle).** The dependency is **one-way:
  `envelope.py` → `errors.py`**, never the reverse. `errors.py` defines the `ForgeError`
  taxonomy, the per-class `code`/`exit_code` ClassVars, the `ERROR_CODE_EXITS` registry,
  and `VALID_ERROR_CODES` — and imports nothing from `envelope.py`. `envelope.py` imports
  `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` from `errors.py` at runtime (for the
  `ErrorEnvelope.__post_init__` checks) and references `ForgeError` **only as a type
  annotation** in `to_envelope` via `from __future__ import annotations` +
  `if TYPE_CHECKING: from grain.domain.errors import ForgeError` (no runtime import of the
  class, so no cycle). `to_envelope` reads `exc.code`/`exc.exit_code` off the passed
  instance — it never needs the `ForgeError` symbol at runtime.
- **NEW `src/grain/domain/envelope.py`** (shared frame module, landed first, §8/§10):
  - `VALID_ENGINE_KINDS` frozenset of the registered `kind` tokens (§3.2 table), including
    the legacy-site tokens downstream packets emit, marked provisional per §3.6 (see below).
  - `EngineEnvelope` frozen dataclass with fields: `kind`, `status`, `grain_version`,
    `data`, `command` (optional), `gate` (optional), `error` (optional), `warnings`
    (default empty), and `apiVersion` defaulting to `"grain.engine/v1"` (§3.1).
  - `EngineEnvelope.__post_init__` enforcing the §3.3 tri-state invariants:
    `status ∈ {ok, gate, error}`; `error` non-null **iff** `status == "error"`; `gate`
    non-null **iff** `status == "gate"`; `data` non-null **iff** `status ∈ {ok, gate}`;
    `kind ∈ VALID_ENGINE_KINDS` (unregistered `kind` is a programming error). `kind` may
    be `None` only on error envelopes (§3.4 — `handle_error` may run before any command
    sets its kind).
  - Imports `VALID_ERROR_CODES` and `ERROR_CODE_EXITS` **from `errors.py`** (the owner,
    §4.2) — `envelope.py` does NOT define them. Used by `ErrorEnvelope.__post_init__`.
  - `ErrorEnvelope` frozen dataclass: `code`, `message`, `detail` (default `""`),
    `exit_code`, and `apiVersion` defaulting to `"grain.error/v1"` (§4.2).
    `__post_init__` asserts `code ∈ VALID_ERROR_CODES` and that `code`↔`exit_code` match
    the §4.1 registry.
  - `to_envelope(exc: ForgeError) -> ErrorEnvelope` and `envelope_to_dict(env) -> dict`
    (stable key order) — the single construct/serialize path every surface uses (§4.2).
    The `exc: ForgeError` annotation is resolved under `from __future__ import annotations`
    + `TYPE_CHECKING` so it does not trigger a runtime import of `errors.py`'s `ForgeError`
    class (§4.2 one-way rule).
- **EDIT `src/grain/domain/errors.py`** (§4.2 — this module OWNS the code registry):
  - Add `code: ClassVar[str]` and `exit_code: ClassVar[int]` to `ForgeError` and override
    per the 7 subclasses to the exact §4.1 pairs. Codes are `grain.`-namespaced. The exit
    integers do NOT change.
  - Define `ERROR_CODE_EXITS: dict[str, int]` (the canonical §4.1 code↔exit registry) and
    `VALID_ERROR_CODES = frozenset(ERROR_CODE_EXITS)` **here**, so `envelope.py` and
    `error_handler.py` import them from `errors.py` (one-way; no import of `envelope.py`).
- **EDIT `src/grain/cli/error_handler.py`** (§4.3):
  - Keep `EXIT_CODES` as the single audited lookup, now derived/consistent with the
    ClassVars; add a module-import-time consistency assert that every `VALID_ERROR_CODES`
    member resolves through `EXIT_CODES` to the matching int and that the two tables do
    not drift (§4.2).
  - `handle_error(exc, fmt)` becomes format-aware (§4.3): `fmt == "text"` (default)
    unchanged — `Error: <message>` (+ indented detail) to **stderr**, returns the exit
    code; `fmt == "json"` — emit a §3 envelope with `status: "error"` and
    `error = envelope_to_dict(to_envelope(exc))` to **stdout**, still returning the same
    exit code. The catch-all wraps non-`ForgeError` exceptions as `GeneralError`
    (`grain.general`) so json mode never emits a bare traceback (§4.3).
- **NEW `tests/test_engine_envelope.py`** covering the criteria below.

## Constraints
- **MVP only (§8).** Build the dataclasses, the error ClassVars, and the format-aware
  `handle_error`/assert ONLY. Do NOT: build the `--envelope`/`GRAIN_ENGINE_ENVELOPE`
  negotiation or wire any legacy `workflow`/`recipe` emit site to the envelope; touch
  `mcp_service.py`, `recipe_service.engine_error_to_forge`, capabilities, version, or the
  HTTP wrapper. Those are sibling/follow-on P35 packets. This packet only makes the frame,
  the error object, and the CLI error path emit it.
- **Decisions are resolved (§9) — do not reopen.** Codes are `grain.`-namespaced (OD-1);
  `status` is tri-state `ok|gate|error` (OD-2). No boolean `ok`, no `error XOR data` XOR
  invariant (that bug is §3.3 X3).
- **Casing:** snake_case everywhere except the `apiVersion` keys (§3.1). No camelCase
  `grainVersion`/`exitCode`.
- **Exit codes are a frozen contract surface (§4.1):** the 7 `code`↔`exit_code` pairs
  must match the locked `cli_spec.md §5` table exactly; do not add, remove, or renumber.
- **One-way import only (§4.2):** `errors.py` MUST NOT import from `envelope.py`. The
  code registry (`ERROR_CODE_EXITS`, `VALID_ERROR_CODES`) lives in `errors.py`;
  `envelope.py` imports it and references `ForgeError` annotation-only via
  `from __future__ import annotations` + `TYPE_CHECKING`. No runtime cycle.
- **Grain idioms:** frozen `@dataclass` + `__post_init__` + `VALID_*` frozensets (mirror
  `domain/recipe_run.py` / `domain/workflow_loop.py`); `ForgeError` taxonomy preserved;
  CLI canonical. New `.py` files carry the SPDX Apache-2.0 header used across the repo
  (`# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison` / `# SPDX-License-Identifier: Apache-2.0`).
- Text-mode `handle_error` output must be byte-for-byte the prior behavior (human/script
  back-compat, §4.3); only the new `fmt` parameter and the json branch are added.

## Deliverable
- `src/grain/domain/envelope.py` with `VALID_ENGINE_KINDS`, `VALID_STATUSES`,
  `EngineEnvelope`, `ErrorEnvelope`, `to_envelope`, `envelope_to_dict` as specified in
  `deliverable_spec.md` (importing `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` from `errors.py`).
- `src/grain/domain/errors.py` with the `code`/`exit_code` ClassVars on all 7 subclasses
  plus the `ERROR_CODE_EXITS` registry and `VALID_ERROR_CODES` frozenset (owned here).
- `src/grain/cli/error_handler.py` with the derived `EXIT_CODES`, the consistency assert,
  and the format-aware `handle_error(exc, fmt)`.
- `tests/test_engine_envelope.py` with the cases in the acceptance criteria.

## Acceptance Criteria
- Each of the 7 `ForgeError` subclasses exposes `.code` and `.exit_code` matching the §4.1
  table exactly (`GeneralError`→`grain.general`/1 … `AdapterError`→`grain.adapter`/7), and
  `VALID_ERROR_CODES` equals that set of 7 `grain.`-namespaced tokens; a test asserts the
  full mapping.
- `EngineEnvelope.__post_init__` enforces the tri-state table (§3.3): constructing
  `status="ok"` with `error` set, `status="gate"` with `gate=None`, `status="error"` with
  `data` set or `error=None`, an unknown `status`, or a `kind` not in
  `VALID_ENGINE_KINDS` (for a non-error envelope) each raises; the three legal forms
  (`ok` with data, `gate` with data+gate, `error` with error) each construct successfully.
- `ErrorEnvelope.__post_init__` raises when `code ∉ VALID_ERROR_CODES` or when
  `code`↔`exit_code` disagree with the §4.1 registry; a matching pair constructs.
- `to_envelope(exc)` then `envelope_to_dict(...)` on each of the 7 exceptions yields a dict
  with exactly the keys `apiVersion, code, message, detail, exit_code` (stable order),
  `apiVersion == "grain.error/v1"`, the correct `code`/`exit_code`, and `detail` present
  as `""` when the exception carries none.
- `handle_error(exc, "text")` writes `Error: <message>` (+ indented detail) to **stderr**,
  writes nothing to stdout, and returns the §4.1 exit code (byte-identical to prior
  behavior); `handle_error(exc, "json")` writes a `status:"error"` `grain.engine/v1`
  envelope (with the embedded `grain.error/v1` object under `error`, `data` null) to
  **stdout** and returns the same exit code. A non-`ForgeError` passed in json mode is
  wrapped as `grain.general`/1 (no traceback emitted).
- The module-import consistency assert in `error_handler.py` fails (raises at import) if
  `EXIT_CODES` and `VALID_ERROR_CODES`/the ClassVars are made to disagree (covered by a
  test that monkeypatches/parametrizes the tables or asserts the live invariant).
- No circular import: `import grain.domain.errors` then `import grain.domain.envelope`
  **and** the reverse order both succeed; `grain.domain.errors` has no runtime import of
  `grain.domain.envelope` (assertable via `importlib`/source inspection), and
  `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` are the same objects whether reached via
  `errors.py` or via `envelope.py`'s re-imported references (identity check).
- `uv run pytest tests/test_engine_envelope.py` passes with ≥ 8 tests and the full suite
  shows no regressions.

## Dependencies
- none — this is the foundation; T02/T03 and all other P35 packets depend on it.

## Relevant Files
- `src/grain/domain/envelope.py` (new) — the shared frame + error object + serializers;
  imports `VALID_ERROR_CODES`/`ERROR_CODE_EXITS` from `errors.py` (one-way, §4.2).
- `src/grain/domain/errors.py` (edit) — `code`/`exit_code` ClassVars on the 7 subclasses
  plus `ERROR_CODE_EXITS` + `VALID_ERROR_CODES` (the code registry lives here, not envelope).
- `src/grain/cli/error_handler.py` (edit) — format-aware `handle_error` + consistency assert.
- `tests/test_engine_envelope.py` (new) — envelope/error tests.
- `src/grain/domain/recipe_run.py`, `src/grain/domain/workflow_loop.py` (reference) —
  frozen `@dataclass` + `__post_init__` + `VALID_*` idiom and SPDX header to mirror.
- `docs/working/engine_contract_spec.md` §3 (envelope), §4 (errors), §8 (MVP/build order),
  §9 (resolved decisions), §10 (implementation notes) — the authoritative contract.

## Escalation Conditions
- If the live `cli_spec.md §5` exit-code table disagrees with the §4.1 registry (so a code
  cannot be made 1:1 with an exit code), STOP and log a change proposal — do not silently
  pick one; exit codes are a locked contract surface.
- If wiring the json branch of `handle_error` requires reading `ctx.obj["kind"]`/`["fmt"]`
  in a way not yet plumbed (§3.4), keep `kind` `null` on the error envelope (explicitly
  permitted) and record the plumbing as a note for the CLI-integration follow-on — do not
  build the `ctx.obj` negotiation here.

## Model Recommendation
Opus-class for the invariant design — the tri-state `__post_init__` matrix and the
code↔exit_code consistency assert have subtle edge cases (the X3 XOR bug this replaces is
exactly the kind of thing to get right once). The implementation is otherwise mechanical;
a Sonnet-class model can execute against this packet if the §3.3 tri-state table and the
§4.1 code table in `deliverable_spec.md` are followed literally.
