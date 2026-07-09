# Task: Change proposal + conformance tests + docs

## Metadata
- **ID:** P37-T11
- **Status:** draft
- **Phase:** Phase 37 — Grain-as-Engine Headless Contract
- **Backlog:** P37-T11
- **Packet Path:** tasks/P37-T11/
- **Dependencies:** P37-T01, P37-T02, P37-T03, P37-T04, P37-T05, P37-T06, P37-T07, P37-T08, P37-T09, P37-T10
- **Primary Adapter:** docs
- **Secondary Adapters:** code
- **Engine-contract:** the ratification + verification slice — drafts the canonical change
  proposal that promotes the contract — `toolkit_contract.md` 1.0→1.1 (canonical) and
  `cli_spec.md` §5/§10 (canonical) are edited in place; `recipe_engine_spec.md` §6 lives in
  `docs/working/` and is PROMOTED toward the canonical recipe doc (`docs/canonical/recipe_spec.md`)
  — and lands the cross-surface conformance test suite that proves
  the §3 frame / §4 error taxonomy / §3.3 tri-state hold identically on CLI json and stdio MCP.
  Writes a CHANGE PROPOSAL into `docs/working/change_proposals.md` — does NOT edit canonical
  docs directly (they require human approval). stdio-only, no network, file-backed.

## Objective
Ratify and verify the Phase 35 contract. Two deliverables, no new product code paths:
(1) a **change proposal** appended to `docs/working/change_proposals.md` (the working-layer
location for proposed canonical edits) that requests the three canonical edits the spec
enumerates (§0, §8): `toolkit_contract.md` 1.0→1.1, `cli_spec.md` §5 + §10, and
`recipe_engine_spec.md` §6; and (2) a **cross-surface conformance test suite**
(`tests/test_engine_contract_conformance.py`) that asserts the contract holds identically
across CLI `--format json` and stdio MCP — taxonomy round-trip, frame parity, tri-state
`__post_init__` legality, the `docs audit --fix` no-op fix, and `version --check` fail-silent.
Plus README/CHANGELOG entries documenting the new headless contract. Per the spec these edits
go to the **working** doc only; the canonical promotion happens via human review of the proposal.
Note the path facts the proposal must get right: `toolkit_contract.md` and `cli_spec.md` are
canonical (`docs/canonical/`); `recipe_engine_spec.md` is a **working** doc (`docs/working/`)
being promoted, and the canonical recipe doc is `docs/canonical/recipe_spec.md`.

## Why This Task Exists
The spec extends the LOCKED canonical `toolkit_contract.md` v1.0 additively and amends two
sibling canonical docs (§0); those edits cannot be made directly (canonical docs require human
approval per the monorepo rule and `change_proposals.md` §1). This packet produces the
reviewable proposal so a human can promote the contract to 1.1. The spec also notes the
critique flagged that **nothing tested cross-surface parity** (§8, §10): the round-trip and
frame-parity guarantees (§3.1, §4.3, §5.1) are the whole point of "one frame, one error" and
must be machine-verified end-to-end once all surfaces (T01–T10) have landed. This is the
capstone packet: it depends on every other P35 packet because it tests the integrated surface
and ratifies the decisions they implement. All design decisions are RESOLVED (§9); the proposal
records them as decided, it does not reopen them.

## Scope
- **EDIT `docs/working/change_proposals.md`** (append one proposal using the file's §2
  template; do NOT touch any `docs/canonical/*`):
  - **`toolkit_contract.md` 1.0 → 1.1 (minor, additive).** Build the three forward-declared
    artifacts the locked doc declared doc-only (§0): the **built capability registry**
    (`docs/runtime/grain_capabilities.yaml` with `since:` + new additive
    `apiVersion`/`grain_contract_version`/per-cap `kind/drive/stability/surfaces` keys, §6.3);
    **`grain workspace list`** now concrete (§6.4); **`workflow_drive`** capability made
    concrete (the drive-loop realization, §5.4) — note it remains `planned` in the seed (§6.2).
    State that every field/path the locked doc names is preserved verbatim and everything new
    is additive (a v1.0 reader keying on `id/command/since` is unaffected) (§0, §6.3).
  - **`cli_spec.md` §5 (exit-code ratification).** Ratify the **two** behaviour changes (§7.1):
    (1) `suggest accept` pick-up in JSON mode exit code **1 → 0** (now a `status: gate`, not an
    error); (2) CLI `--format json` errors now print on **stdout** (today they are text on
    stderr regardless of `--format`) as a `status: error` envelope, process still exits the same
    code (§4.3). State explicitly that the 7 exit codes themselves do NOT change (§4.1).
  - **`cli_spec.md` §10.** `errors` → `error` (the untyped `{"errors":[...]}` blob becomes the
    single `grain.error/v1` object embedded in the `grain.engine/v1` envelope, §4.2/§3.1);
    register the new command groups: `capabilities` (list/show/`--check`), `workspace`
    (list/resolve), `version` (`--check`/`--refresh`) (§6.4, §7.2).
  - **`recipe_engine_spec.md` §6** (a **working** doc at `docs/working/recipe_engine_spec.md`,
    promoted toward the canonical recipe doc `docs/canonical/recipe_spec.md` — NOT itself under
    `docs/canonical/`). Un-defer recipe verbs over MCP (`recipe_run` [operator], `recipe_next`,
    `recipe_resume`, `recipe_gate`, `recipe_list`, `recipe_show`, `recipe_status`) — the
    file-backed drive loop is now concrete (§5.4, §5.5).
  - Record the **one canonical conflict resolved by retreat** (§0, §5.6, C1): HTTP MCP + auth
    is out-of-contract / deployment-only; the contract-conformant MCP surface is **stdio**.
    Record the **one-time pre-1.0 MCP break** (§5.1): the 5 existing tools' payload moves from
    `structuredContent` root to `data`, `ok` → `status`.
  - Fill the template fields (Affected Canonical Docs; Reason; Proposed Change Summary; Impact;
    Urgency; Suggested Follow-Up; Decision = `needs_review`).
- **NEW `tests/test_engine_contract_conformance.py`** — the cross-surface conformance suite
  (§8, §10). Five guarantee families, all OBJECTIVELY assertable:
  1. **Taxonomy round-trip (§4.3):** every `ForgeError` subclass (all 7) produces an
     **identical** error dict over CLI `--format json` and over the MCP error path — same
     `apiVersion`/`code`/`message`/`detail`/`exit_code` keys and values. NOTE: CLI `--format json`
     ERROR envelopes are ALWAYS-enveloped and emitted on **stdout WITHOUT `--envelope`** (§4.3) —
     the `--envelope` opt-in (§3.5) governs only legacy *success* sites; error output is always a
     `status: error` envelope. So the round-trip test invokes the failing command with plain
     `--format json` (no `--envelope`) and still parses an `error` envelope — the test is valid.
  2. **Frame parity (§3.1, §5.1):** for a representative **ALWAYS-ENVELOPED** read command —
     `grain capabilities` / `capabilities_list`, or `grain version` / `version_check` — the CLI
     `--format json` envelope and the MCP `tools/call` `structuredContent` carry the **identical**
     `apiVersion` (`grain.engine/v1`), `kind`, and `status` framing. The command MUST be one of
     the new always-enveloped surfaces (§3.5), **NOT** a bare-by-default legacy site like
     `workflow next` / `recipe list` — those emit bare JSON without `--envelope`, so the parity
     assertion would compare a bare CLI dict against an enveloped MCP result and fail.
  3. **Tri-state `__post_init__` legality (§3.3):** the three legal forms (`ok`+data,
     `gate`+data+gate, `error`+error) construct; the illegal combinations raise.
  4. **`docs audit --fix --format json` (§7.1):** actually applies fixes (closes the silent
     no-op) AND reports `fixes_applied` in the payload.
  5. **`grain version --check` fail-silent (§7.2):** on a simulated network failure the command
     degrades to `check_error` (latest null) and exits **0** — never a non-zero exit.
- **EDIT `README.md`** — a short "Headless / engine contract" section: the `grain.engine/v1`
  envelope, `--format json` everywhere, `--envelope` opt-in for legacy sites, the new
  `capabilities`/`workspace`/`version` commands, stdio MCP, and the fail-silent update check.
- **EDIT `CHANGELOG.md`** — an unreleased/0.5.0 entry summarizing the headless contract
  (envelope, typed errors, expanded MCP, capability registry, non-interactive `--yes`/gate,
  version check) and CALLING OUT the back-compat changes (suggest-pick-up exit 1→0; json errors
  on stdout; the one-time MCP `structuredContent` shape break).

## Constraints
- **MVP only (§8).** Test and ratify exactly what T01–T10 build. Do NOT write conformance
  tests for deferred items (§8 "Deferred"): legacy-site migration / 0.6.0 default flip,
  `suggest_accept` over MCP, recipe auto-mode / `workflow_loop` over MCP,
  `capabilities reconcile`, multi-workspace enumeration, `upgrade --yes`, HTTP+auth/remote MCP.
- **Do NOT edit canonical docs.** All canonical edits are described in the change PROPOSAL only
  (`docs/working/change_proposals.md`). Editing any `docs/canonical/*` is out of scope and
  forbidden — promotion is a human-approved follow-up (`change_proposals.md` §1; monorepo rule).
- **Do NOT re-implement product code.** This packet writes a test module + docs only. The
  conformance tests IMPORT and drive the surfaces built by T01–T10 (CliRunner for CLI; the MCP
  service entry points for MCP); they define no new envelope/error/service logic.
- **Decisions are resolved (§9) — do not reopen.** The proposal records OD-1..OD-6 + decision #5
  as DECIDED. Frame is `grain.engine/v1`; error is `grain.error/v1`; status is tri-state.
- **Grain idioms.** The new `tests/test_engine_contract_conformance.py` carries the SPDX header
<!-- REUSE-IgnoreStart -->
  (`# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison` / `# SPDX-License-Identifier: Apache-2.0`);
<!-- REUSE-IgnoreEnd -->
  reuse the existing test fixtures/CliRunner pattern in the repo's `tests/`.
- **stdio-only / no network / file-backed (§2 principle 4).** The version-check fail-silent test
  must SIMULATE network failure (monkeypatch `adapters/pypi.fetch_latest` to raise
  `AdapterError`); it must NOT make a real network call.

## Deliverable
- An appended proposal in `docs/working/change_proposals.md` covering the three canonical
  edits (toolkit 1.0→1.1; cli_spec §5 + §10; recipe_engine_spec §6) per `deliverable_spec.md`.
- `tests/test_engine_contract_conformance.py` with the five guarantee families above.
- README/CHANGELOG entries for the headless contract + the ratified back-compat changes.

## Acceptance Criteria
- `docs/working/change_proposals.md` gains exactly one new proposal whose "Affected Canonical
  Docs" lists `toolkit_contract.md`, `cli_spec.md`, and `recipe_engine_spec.md`; its body
  names the **1.0 → 1.1** bump, the **two** §5 exit-code behaviour changes (suggest pick-up
  1→0; json errors on stdout), the §10 `errors`→`error` + envelope + the three new command
  groups, and the §6 recipe-verbs-over-MCP un-defer; Decision status is `needs_review`. No file
  under `docs/canonical/` is modified (verifiable: `git status` shows only the working doc +
  test + README + CHANGELOG changed).
- **Taxonomy round-trip test:** for each of the 7 `ForgeError` subclasses the error dict
  obtained via CLI `--format json` (invoked **without `--envelope`** — error envelopes are always
  emitted, on stdout, per §4.3) equals the error dict obtained via the MCP error path
  (same `apiVersion == "grain.error/v1"`, same `code`, `exit_code`, `message`, `detail` keys
  and values); the test fails if any class diverges between surfaces.
- **Frame-parity test:** a representative **ALWAYS-ENVELOPED** read command (`grain capabilities`
  / `capabilities_list`, or `grain version` / `version_check` — NOT a bare-by-default legacy site
  like `workflow next` / `recipe list`, §3.5) yields a CLI envelope and an MCP `structuredContent`
  with identical `apiVersion == "grain.engine/v1"`, identical `kind`, and identical `status`; the
  test asserts equality of those three top-level fields across surfaces. (Using a legacy site would
  leave the CLI side bare without `--envelope` and the parity assertion would fail.)
- **Tri-state legality test:** the three legal envelopes (`ok`+data; `gate`+data+gate;
  `error`+error) construct successfully and each illegal combination (`ok` with error set;
  `gate` with `gate=None`; `error` with `data` set or `error=None`; unknown `status`) raises.
- **`docs audit --fix --format json` test:** on a workspace with a fixable doc issue, the
  command (with the consent flag) APPLIES the fix (the on-disk file changes / re-audit is clean)
  AND the JSON payload contains a non-empty `fixes_applied`; running it without consent in JSON
  mode emits `status: gate`, applies nothing, and exits 0.
- **`version --check` fail-silent test:** with `adapters/pypi.fetch_latest` monkeypatched to
  raise `AdapterError`, `grain --format json version --check` exits **0**, the payload's
  `latest` is null and a `check_error`/`source: unavailable` is present — no non-zero exit, no
  traceback, no real network call.
- `uv run pytest tests/test_engine_contract_conformance.py` passes with ≥ 8 tests and the full
  suite shows no regressions.

## Dependencies
- **P37-T01** (envelope + typed-error foundation) — the `grain.engine/v1` frame + taxonomy under test.
- **P37-T02** (version resolver) — `get_version()` referenced by the parity/version tests.
- **P37-T03** (capability registry) — the registry the §10 group registration ratifies.
- **P37-T04** (envelope CLI wiring + opt-in flag) — the CLI json envelope the tests parse.
- **P37-T05** (`engine_error_to_forge` extraction) — recipe-error parity across CLI/MCP.
- **P37-T06** (MCP surface expansion) — the MCP side of every cross-surface assertion.
- **P37-T07** (HTTP wrapper pass-through fix) — the §5.6 retreat recorded in the proposal.
- **P37-T08** (capability file writer + capabilities/workspace CLI) — the §6 surface ratified.
- **P37-T09** (non-interactive `--yes` / `gate()`) — the `docs audit --fix` + gate behaviour tested.
- **P37-T10** (`grain version` + `--check`) — the fail-silent behaviour tested.

## Relevant Files
- `docs/working/change_proposals.md` (edit) — append the canonical-promotion proposal.
- `tests/test_engine_contract_conformance.py` (new) — cross-surface conformance suite.
- `README.md` (edit) — headless / engine contract section.
- `CHANGELOG.md` (edit) — 0.5.0 entry + back-compat call-outs.
- `tests/test_engine_envelope.py` (reference, P37-T01) — tri-state / round-trip patterns to extend.
- `src/grain/domain/envelope.py`, `src/grain/domain/errors.py` (reference) — frame + taxonomy under test.
- `src/grain/services/mcp_service.py` (reference) — MCP entry points the parity tests drive.
- `src/grain/adapters/pypi.py` (reference, P37-T10) — the `fetch_latest` to monkeypatch.
- `docs/working/engine_contract_spec.md` §0 (canonical relationship), §3 (envelope), §4 (errors),
  §5 (MCP), §6 (capabilities), §7 (non-interactive + version), §8 (MVP/build order), §9 (resolved).
- `docs/working/change_proposals.md` §2 (proposal template to follow).

## Escalation Conditions
- If a conformance test reveals a genuine CLI↔MCP divergence (a surface does not actually emit
  the §3 frame or the §4 error object identically), STOP and log a blocker against the owning
  packet (T04/T06) — fix it there, do NOT patch the divergence inside the test or re-implement
  the surface in this packet.
- If the live `cli_spec.md §5`/`§10` or `toolkit_contract.md` text has drifted from what the
  spec assumes (so the proposal cannot cite the section accurately), record the discrepancy in
  the proposal's "Reason" and flag it for the human reviewer — do not silently reconcile.
- If any deferred item (§8) appears to need a conformance test to pass, it is out of scope —
  record it as a follow-up in the CHANGELOG/proposal, do not pull it into MVP.

## Model Recommendation
Opus-class for the proposal authoring (it must precisely and faithfully summarize three
canonical edits + two ratified back-compat changes without reopening resolved decisions) and
for the cross-surface parity assertions (the round-trip/frame-parity tests are where the
"one frame, one error" claim is actually proven — subtle to get exactly right). The README/
CHANGELOG prose and the per-test scaffolding are mechanical; a Sonnet-class model can execute
the test cases if the five guarantee families and the §-citations in `deliverable_spec.md` are
followed literally.
