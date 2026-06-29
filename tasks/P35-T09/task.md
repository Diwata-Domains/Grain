# Task: Non-interactive completeness

## Metadata
- **ID:** P35-T09
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T09
- **Packet Path:** tasks/P35-T09/
- **Dependencies:** P35-T01, P35-T04
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** non-interactive completeness layer (engine_contract_spec.md §7.1) —
  one confirmation policy, one gate, riding the §3.3 `status: gate` slot of the
  `grain.engine/v1` frame. Honors the §2 principle-1 invariant: `--format json` NEVER calls
  `click.confirm`/`click.prompt`; consent-needed → a `status: gate` envelope, **exit 0**.
  CLI-only, file-backed, no network, no MCP (MCP write tools carry no gate, §5.8).

## Objective
Make the three interactive write blockers (`suggest accept`, `docs audit --fix`, `upgrade`)
completable headlessly through **one** confirmation policy (engine_contract_spec.md §7.1).
Build a new `src/grain/domain/confirm.py` holding the `ConfirmationGate` frozen dataclass +
`VALID_CONFIRM_REASONS` frozenset, and a new `src/grain/cli/confirm.py::gate()` centralizer
that is the single place a command resolves consent — so no command hand-rolls `click.confirm`
anymore. Add a uniform `--yes / -y` flag (plus a hidden, deprecated `--no-confirm` alias) to
`suggest accept`, `docs audit`, and `upgrade`. Route `suggest accept` (both the new-task and
pick-up paths) and `docs audit --fix` through `gate()`. Fix the `docs audit --fix --format
json` silent no-op by moving the fix logic **above** the json early-return and adding a
`fixes_applied` field. Enforce the invariant that in json mode a consent-needed command emits
a `status: gate` `grain.engine/v1` envelope (data present, gate populated, no action taken)
and **exits 0** — never an error and never a prompt. Both the `status: gate` consent emit and
the `status: ok` post-action result emit are **ALWAYS-enveloped** (§3.5), independent of T04's
`--envelope` opt-in (which governs only these sites' pre-existing bare output); the
`suggest accept` emits carry `kind = "SuggestionList"` and the `docs audit` emits carry
`kind = "DocsAuditReport"` (both from T01 `VALID_ENGINE_KINDS`, §3.2).

## Why This Task Exists
Three CLI write paths are interactive dead-ends headlessly (§1, §7.1): `suggest accept` calls
`click.confirm` always (even with `--no-confirm`) and refuses in JSON; `docs audit --fix
--format json` `return`s **before** the fix block — a **silent no-op**; `upgrade` prompts per
file. Flag naming is split-brain (`--no-confirm` vs `--interactive`). A familiar (agent)
therefore cannot complete the SDLC loop's most frequent action ("accept a suggestion → create
a task") or apply doc fixes without dropping to an interactive terminal (§2 principle 1, §1
linchpin). This packet delivers the §8 MVP "Non-interactive" slice: `domain/confirm.py` +
`cli/confirm.py::gate()`; uniform `--yes`; route the blockers through `gate()`; fix the silent
no-op; `status: gate` exit 0. All design decisions are RESOLVED (§9) — OD-2 (tri-state
`status` with `gate` exit 0) is confirmed; do not reopen it.

## Scope
- **NEW `src/grain/domain/confirm.py`** (§7.1):
  - `VALID_CONFIRM_REASONS` frozenset =
    `{new_task_packet_create, active_task_switch, docs_fix_apply, upgrade_overwrite_customized}`.
  - `ConfirmationGate` **frozen** dataclass: `action: str`, `reason: str`, `prompt: str`,
    `preview: dict` (default empty), `retry_with: tuple[str, ...]` (default empty), with a
    `__post_init__` that validates `reason ∈ VALID_CONFIRM_REASONS` and `action`/`prompt`
    non-empty. A `to_dict()` serializing the §7.1 `gate` shape with stable key order.
- **NEW `src/grain/cli/confirm.py::gate(...)`** — the single consent centralizer (§7.1):
  decides per the §7.1 decision matrix and, in json + consent-needed, builds and prints a
  `status: gate` `EngineEnvelope` (T01) to **stdout** and signals "do not proceed, exit 0".
  No command calls `click.confirm`/`click.prompt` directly anymore.
- **EDIT `src/grain/cli/suggest.py`** (§7.1): add `--yes / -y` (+ hidden `--no-confirm`
  alias); route **both** `suggest accept` paths (new-task creation **and** pick-up/active-task
  switch) through `gate()`. Ratify pick-up json exit code **1 → 0** (now a `status: gate`, not
  an error).
- **EDIT `src/grain/cli/docs.py`** + **`src/grain/services/docs_audit_service.py`** (§7.1):
  add `--yes / -y` (+ hidden `--no-confirm`) to `docs audit`; move the `--fix` apply logic
  **above** the `--format json` early-return; build the fixable set, route through `gate()`,
  and on proceed add a `"fixes_applied": [...]` field to the result (closes the silent no-op).
- **EDIT `src/grain/cli/upgrade.py`** (§7.1): add `--yes / -y` (+ hidden `--no-confirm`)
  for **uniform flag surface only**; keep `--interactive` for humans. The
  overwrite-of-customized-files headless path (`upgrade_overwrite_customized`) is **DEFERRED**
  (§7.1, §8, §9) — do not route upgrade's per-file overwrite prompt through `gate()` here.
- **NEW `tests/test_noninteractive.py`** covering the criteria below.

## Constraints
- **MVP only (§8).** Build `domain/confirm.py`, `cli/confirm.py::gate()`, the uniform flag,
  the `suggest accept` + `docs audit --fix` routing, and the silent-no-op fix ONLY. DEFER
  (§8 Deferred): `upgrade --yes` overwrite-of-customized headless path; the `suggest_accept`
  write tool over MCP (§5.8); any familiar self-execution of upgrade.
- **No MCP here (§5.8).** MCP write tools act immediately and carry **no** `status: gate` —
  the gate protects a human at a terminal. Do not add a gate to any MCP tool.
- **The invariant is absolute (§2 principle 1, §7.1):** when `fmt == "json"`, NEITHER
  `gate()` NOR any touched command may call `click.confirm`/`click.prompt`. Consent-needed in
  json → emit the `status: gate` envelope and exit 0.
- **ALWAYS-ENVELOPED rule (§3.5) — the gate + result emits this packet adds are NOT
  governed by T04's `--envelope` opt-in.** The two NEW emit sites this packet introduces — the
  `status: gate` consent envelope and the `status: ok` post-action result envelope on
  `suggest accept` and `docs audit --fix` — are **ALWAYS-enveloped** from day one,
  independent of the `--envelope` flag / `GRAIN_ENGINE_ENVELOPE` env. The T04 opt-in (§3.5)
  governs ONLY those sites' **pre-existing bare** output (the legacy `--format json` shape
  that printed before this packet); the consent gate is a structured signal a familiar MUST be
  able to parse unconditionally, and the post-consent result is its `status: ok` counterpart.
  `gate()` and the proceed-path emit therefore go through the frame regardless of the legacy
  default-bare wiring — do NOT gate these two emits behind `ctx.obj["envelope"]`. (This mirrors
  the cross-cutting always-enveloped rule: NEW emits on suggest accept / docs audit are always
  enveloped, as are all new commands and all MCP results.)
- **Kind tokens (§3.2, from T01 `VALID_ENGINE_KINDS`):** both emits (`status: gate` and
  `status: ok`) for `suggest accept` use `kind = "SuggestionList"`; for `docs audit` they use
  `kind = "DocsAuditReport"`. These are the two registered legacy-site kinds in T01's
  `VALID_ENGINE_KINDS` (§3.2 final row). Pass exactly these tokens to `gate(kind=...)` and to
  the proceed-path `emit(...)` — do NOT invent a new kind (an unregistered kind is a
  programming error caught in `EngineEnvelope.__post_init__`, §3.2).
- **Decisions resolved (§9) — do not reopen.** `status: gate` is exit 0, not an error (OD-2);
  pick-up json exit **1 → 0** and `suggest accept` new-task auto-confirmable via `--yes` (D4
  relaxed to "always *show* + explicit consent") are the deliberate headless-completeness
  fix — ratify, do not re-litigate.
- **Consume, don't redefine:** `EngineEnvelope`/`status` tri-state/serializers come from
  `domain/envelope.py` (P35-T01); the gate emit reuses the CLI envelope/`ctx.obj` seam from
  P35-T04. Do NOT redefine the frame, the `status` vocabulary, or a second emit path.
- **Casing (§3.1):** snake_case everywhere except the `apiVersion` keys. Gate keys are
  `action, reason, prompt, preview, retry_with`.
- **Grain idioms:** frozen `@dataclass` + `__post_init__` + `VALID_*` frozenset (mirror
  `domain/recipe_run.py`); `ForgeError` taxonomy preserved; CLI canonical (§2 principle 5).
  New `.py` files carry the SPDX Apache-2.0 header (`# SPDX-License-Identifier: Apache-2.0`)
  used across the repo (Grain was relicensed) — matching `src/grain/domain/workflow_loop.py`.

## Deliverable
- `src/grain/domain/confirm.py` with `VALID_CONFIRM_REASONS` + the `ConfirmationGate` frozen
  dataclass (`__post_init__` + `to_dict`) as specified in `deliverable_spec.md`.
- `src/grain/cli/confirm.py` with the `gate(...)` centralizer.
- `src/grain/cli/suggest.py`, `src/grain/cli/docs.py`,
  `src/grain/services/docs_audit_service.py`, `src/grain/cli/upgrade.py` edited per scope.
- `tests/test_noninteractive.py` with the cases in the acceptance criteria.
- Full detail in `deliverable_spec.md`.

## Acceptance Criteria
- `ConfirmationGate.__post_init__` raises on a `reason ∉ VALID_CONFIRM_REASONS` (e.g.
  `"foo"`) and on an empty `action`/`prompt`; each of the four valid reasons
  (`new_task_packet_create`, `active_task_switch`, `docs_fix_apply`,
  `upgrade_overwrite_customized`) constructs and `to_dict()` returns exactly the keys
  `{action, reason, prompt, preview, retry_with}` (stable order) (§7.1).
- **JSON invariant (§7.1 decision matrix):** `grain --format json suggest accept <id>`
  **without** `--yes`, when consent is needed, writes a `status:"gate"` `grain.engine/v1`
  envelope to **stdout** (with `data` = the existing accept dict and a populated `gate` whose
  `reason ∈ VALID_CONFIRM_REASONS` and `retry_with` contains `"--yes"`), takes **no** action
  (no packet created / no active-task switch), and exits **0**; the same command **with**
  `--yes` performs the action and emits `status:"ok"`. A test asserts no `click.confirm`/
  `click.prompt` is invoked in either json path.
- `suggest accept` pick-up in json mode returns exit **0** (ratified from the prior exit 1),
  as a `status:"gate"` envelope when un-consented and `status:"ok"` with `--yes`.
- `grain --format json docs audit --fix` **applies** the fixes (no longer a silent no-op):
  with `--yes` it writes the fixable changes and the result `data` contains `"fixes_applied"`
  listing what was applied; without `--yes` it emits a `status:"gate"` envelope, writes
  **nothing**, and exits 0 — proving the fix block now runs above the json early-return.
- `docs audit` and `suggest accept` accept the hidden `--no-confirm` alias as a synonym for
  `--yes` (same behavior); `upgrade` accepts `--yes`/`--no-confirm` without error while its
  overwrite-of-customized headless behavior stays deferred (asserted: the flag parses; no new
  overwrite-customized gating is exercised).
- **Always-enveloped (§3.5):** the `status: gate` consent emit and the `status: ok` result
  emit on `suggest accept` and `docs audit --fix` are emitted as a `grain.engine/v1` frame in
  `--format json` **regardless** of `--envelope` / `GRAIN_ENGINE_ENVELOPE`. A test asserts that
  with the legacy opt-in OFF (default-bare), both emits are STILL enveloped (frame keys present),
  while a pre-existing bare site stays bare — proving the opt-in governs only legacy output.
- **Kind tokens (§3.2):** the `suggest accept` envelopes carry `kind == "SuggestionList"` and
  the `docs audit` envelopes carry `kind == "DocsAuditReport"` (both ∈ T01 `VALID_ENGINE_KINDS`)
  on both the `status: gate` and `status: ok` emits — asserted on the emitted frames.
- Text mode is unchanged for humans: `suggest accept` / `docs audit --fix` without `--yes`
  still call `click.confirm` (interactive), and with `--yes` proceed without prompting
  (§7.1 matrix rows `text/no` and `text/yes`).
- `uv run pytest tests/test_noninteractive.py` passes with ≥ 8 tests and the full suite shows
  no regressions.

## Dependencies
- **P35-T01** (engine envelope + typed-error foundation) — provides `domain/envelope.py`:
  `EngineEnvelope`, the tri-state `status` (`gate`), `VALID_ENGINE_KINDS`, and the
  serializer the `status: gate` emit goes through. Required before the gate can be emitted.
- **P35-T04** (envelope CLI wiring + opt-in flag) — provides the CLI emit seam / `ctx.obj`
  (`["fmt"]`, `["kind"]`, `["envelope"]`) and the `emit(...)` helper pattern that `gate()`
  reuses to print the gate envelope on the same surface as the `status: ok` path.

## Relevant Files
- `src/grain/domain/confirm.py` (new) — `ConfirmationGate` + `VALID_CONFIRM_REASONS`.
- `src/grain/cli/confirm.py` (new) — the `gate()` consent centralizer.
- `src/grain/cli/suggest.py` (edit) — `--yes`/`--no-confirm`; route accept (new-task +
  pick-up) through `gate()`; pick-up json exit 1→0.
- `src/grain/cli/docs.py` (edit) — `--yes`/`--no-confirm`; route `docs audit --fix` through
  `gate()`.
- `src/grain/services/docs_audit_service.py` (edit) — move fix above the json early-return;
  add `fixes_applied`.
- `src/grain/cli/upgrade.py` (edit) — `--yes`/`--no-confirm` uniform flag surface only
  (overwrite-customized deferred).
- `src/grain/domain/envelope.py` (dependency, P35-T01) — `EngineEnvelope`/`status` tri-state
  (import, do not modify).
- `src/grain/cli/emit.py` / `src/grain/cli/__init__.py` (dependency, P35-T04) — emit seam +
  `ctx.obj` (reuse, do not redefine).
- `tests/test_noninteractive.py` (new) — gate + flag + silent-no-op-fix tests.
- `docs/working/engine_contract_spec.md` §7.1 (gate/flag/matrix), §3.3 (tri-state status),
  §5.8 (MCP carries no gate), §8 (MVP/deferred), §9 (resolved decisions) — the contract.

## Escalation Conditions
- If the expected kind tokens `SuggestionList` (suggest accept) or `DocsAuditReport`
  (docs audit) are **absent** from T01 `VALID_ENGINE_KINDS` (§3.2 final row), STOP and log a
  change proposal to add the `kind` to the spec §3.2 table + `VALID_ENGINE_KINDS` — do not
  invent a kind here (an unregistered kind is a programming error caught in
  `EngineEnvelope.__post_init__`, §3.2).
- If routing the always-enveloped gate/result emit (§3.5) appears to require the T04
  `--envelope` default to be flipped (these are legacy JSON sites, default-bare), STOP — these
  two NEW emits are ALWAYS-enveloped and must NOT be gated behind `ctx.obj["envelope"]`; the
  T04 opt-in governs only the pre-existing bare output of these sites. If emitting the frame
  unconditionally for these two sites conflicts with P35-T04's default-bare wiring, record a
  blocker rather than flipping the global default (0.6.0, §8 Deferred).
- If wiring `upgrade --yes` to actually gate overwrite-of-customized files seems necessary to
  satisfy a test, STOP — that path is deferred (§7.1/§8/§9); only the flag surface ships here.

## Model Recommendation
Opus-class for the gate decision matrix and the absolute json-never-prompt invariant — the
§7.1 matrix, the pick-up exit 1→0 ratification, and the "move fix above the json early-return"
restructuring of `docs audit` have subtle ordering/exit-code edges worth getting right once.
The dataclass and flag plumbing are otherwise mechanical; a Sonnet-class model can execute if
the §7.1 decision matrix and the `ConfirmationGate` shape in `deliverable_spec.md` are
followed literally.
