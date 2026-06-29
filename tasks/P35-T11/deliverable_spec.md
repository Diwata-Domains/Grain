# Deliverable Spec: P35-T11 — Change proposal + conformance tests + docs

## Required Output

### New Files
- `tasks/P35-T11/task.md` — packet metadata/scope ✓
- `tasks/P35-T11/deliverable_spec.md` — this file ✓
- `tests/test_engine_contract_conformance.py` — cross-surface conformance suite

### Modified Files
- `docs/working/change_proposals.md` — append ONE proposal (working layer; canonical untouched)
- `README.md` — add a "Headless / engine contract" section
- `CHANGELOG.md` — add the 0.5.0 headless-contract entry + back-compat call-outs

### Forbidden
- **No file under `docs/canonical/` may be modified.** Canonical promotion is a human-approved
  follow-up driven by the proposal (`change_proposals.md` §1; monorepo CLAUDE.md). Verifiable
  via `git status`: only the four files above change.

All new `.py` files begin with the SPDX header block used across the repo:
```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0
```

## Inputs consumed (owned by upstream packets — do NOT redefine/re-implement)
- `from grain.domain.envelope import EngineEnvelope, ErrorEnvelope, to_envelope, envelope_to_dict,
  VALID_ENGINE_KINDS, VALID_ERROR_CODES` (P35-T01) — frame + error object under test.
- `from grain.domain.errors import (the 7 ForgeError subclasses)` (P35-T01) — taxonomy under test.
- `from grain.version import get_version` (P35-T02) — version source for parity/version tests.
- MCP entry points in `src/grain/services/mcp_service.py` (P35-T06) — `tools/call` handler +
  `_ok`/`_gate`/`_err` helpers; the MCP side of every cross-surface assertion.
- `src/grain/adapters/pypi.py::fetch_latest` (P35-T10) — the network call to monkeypatch.
- CLI commands wired by P35-T04/T08/T09/T10 — driven via `click.testing.CliRunner`.

## Part A — Change proposal (`docs/working/change_proposals.md`)

Append ONE proposal using the file's §2 template. It records the canonical promotion the spec
mandates (§0, §8). It is a PROPOSAL (Decision: `needs_review`) — it does not itself edit canonical.

### Required template fields and exact content

**Proposal Title:** `Promote the Grain-as-Engine headless contract (toolkit 1.0→1.1, cli_spec §5/§10, recipe_engine §6)`

**Affected Canonical Docs:**
- `docs/canonical/toolkit_contract.md` (canonical — edited in place 1.0→1.1)
- `docs/canonical/cli_spec.md` (canonical — §5/§10 edited in place)
- `docs/working/recipe_engine_spec.md` (a **working** doc — §6 **promoted** toward the canonical
  recipe doc `docs/canonical/recipe_spec.md`; `recipe_engine_spec.md` is NOT itself under
  `docs/canonical/`. There is no `docs/canonical/recipe_engine_spec.md` — do not cite that path.)

**Reason:** Phase 35 builds the three artifacts `toolkit_contract.md` v1.0 forward-declared as
doc-only (§0) and amends two sibling canonical docs; those edits require human approval and
cannot be made directly. The working spec `docs/working/engine_contract_spec.md` is the
authoritative source; this proposal requests its promotion.

**Proposed Change Summary** — three edits, stated as additive/ratifying (cite §):

1. **`toolkit_contract.md` 1.0 → 1.1 (minor, additive) — §0, §6:**
   - **Built capability registry:** `docs/runtime/grain_capabilities.yaml` (exact locked path)
     now generated from code (`domain/capabilities.py::CAPABILITIES`), gaining additive top-level
     keys `apiVersion: grain.capabilities/v1` + `grain_contract_version: "1.1"` + `grain_version`
     and per-capability `kind/drive/stability/surfaces`; `since:` preserved (§6.1/§6.3).
   - **`grain workspace list`** is now concrete (env → walk-up via the canonical-marker resolver,
     single active workspace, `link_enumeration: "unsupported"`) (§6.4).
   - **`workflow_drive`** capability made concrete as the file-backed recipe drive loop (§5.4/§5.5);
     remains `planned` (no `since`/`command`) in the seed (§6.2).
   - Assert: every field/path the locked doc names is preserved verbatim; everything new is
     additive — a v1.0 reader keying on `id/command/since` is unaffected (§0/§6.3).

2. **`cli_spec.md` §5 (exit-code ratification) — §7.1, §4.3:** ratify TWO behaviour changes,
   exit-code *table itself unchanged* (§4.1):
   - (1) `suggest accept` pick-up in JSON mode exit code **1 → 0** (now a `status: gate`, §3.3).
   - (2) CLI `--format json` errors now emit on **stdout** as a `status: error` envelope (today:
     text on stderr regardless of `--format`); process still exits the same code (§4.3).

3. **`cli_spec.md` §10 — §3.1, §4.2, §6.4, §7.2:** `errors` → `error` (untyped `{"errors":[...]}`
   blob → the single `grain.error/v1` object embedded in the `grain.engine/v1` envelope); register
   the new command groups `capabilities` (list/show/`--check`), `workspace` (list/resolve),
   `version` (`--check`/`--refresh`).

4. **`recipe_engine_spec.md` §6 — §5.4, §5.5** (working doc `docs/working/recipe_engine_spec.md`,
   promoted toward canonical `docs/canonical/recipe_spec.md`): un-defer recipe verbs over MCP
   (`recipe_run` [operator], `recipe_next`, `recipe_resume`, `recipe_gate`, `recipe_list`,
   `recipe_show`, `recipe_status`); the file-backed, local-FS-only drive loop is now concrete.

Also record (so the reviewer sees them):
- **Canonical conflict resolved by retreat (§0/§5.6, C1):** HTTP MCP + auth is
  out-of-contract / deployment-only; the contract-conformant MCP surface is **stdio** (honors
  locked §2 no-auth and §4.3 no-network). Remote MCP would be a future MAJOR revision.
- **One-time pre-1.0 MCP break (§5.1):** the 5 existing tools' payload moves from
  `structuredContent` root to `data`; `ok` → `status`. Acceptable in a 0.5.0 minor.

**Impact:**
- Implementation: T01–T10 already build it; this promotes the contract surface to 1.1.
- Existing docs: three canonical docs gain additive sections; no removals/renames.
- Task packets: unblocks future phases (legacy-site migration, 0.6.0 default flip) that key on 1.1.
- Validation behaviour: `--format json` errors now structured on stdout; `suggest accept` pick-up
  exit 1→0.
- Workflow behaviour: familiars can drive the loop headlessly over CLI json + stdio MCP.

**Urgency:** medium (contract ratification; not demo-blocking — §0 "Not demo-critical").

**Suggested Follow-Up:** human review → apply the three canonical edits → bump
`GRAIN_CONTRACT_VERSION`/`toolkit_contract.md` to 1.1 → tag 0.5.0.

**Decision → Status:** `needs_review`.

## Part B — Conformance suite: `tests/test_engine_contract_conformance.py`

Five guarantee families. Tests IMPORT and DRIVE the built surfaces; they define no new
envelope/error/service logic. CLI via `click.testing.CliRunner`; MCP via the `mcp_service`
`tools/call` handler. ≥ 8 tests total.

### Family 1 — Taxonomy round-trip (§4.3) — every ForgeError → identical dict over CLI json + MCP
- Parametrize over the 7 subclasses (`GeneralError`…`AdapterError`).
- **Always-enveloped error rule (§4.3):** CLI `--format json` ERROR output is ALWAYS a
  `status: error` envelope emitted on **stdout WITHOUT `--envelope`**. The `--envelope` opt-in
  (§3.5) governs only legacy *success* sites; it does NOT gate error envelopes. So the round-trip
  test invokes the failing command with plain `--format json` (no `--envelope`) and parses an
  `error` envelope off stdout — this is what makes the round-trip test valid.
- Obtain the error dict from **CLI**: invoke a command path that raises that class with
  `--format json` (no `--envelope`), parse stdout, read `envelope["error"]`.
- Obtain the error dict from **MCP**: drive the corresponding tool's failure path, read the
  `structuredContent["error"]`.
- Assert the two dicts are **equal** and each has exactly keys
  `{apiVersion, code, message, detail, exit_code}` with `apiVersion == "grain.error/v1"`,
  the §4.1 `code`↔`exit_code` pair, and matching `message`/`detail`.
- Where a class is not reachable on both surfaces, assert at minimum the shared codes
  (`grain.missing_path`/`grain.usage`/`grain.validation`/`grain.general`) round-trip identically;
  the others are asserted via `to_envelope(exc)` → `envelope_to_dict(...)` equality against the
  surface that does emit them.

### Family 2 — Frame parity (§3.1, §5.1) — CLI↔MCP identical apiVersion/kind/status
- Pick a representative **ALWAYS-ENVELOPED** READ command exposed on both surfaces:
  `grain capabilities` / `capabilities_list` (kind `CapabilityList`) or `grain version` /
  `version_check` (kind `VersionInfo`). **Do NOT** use `workflow next` / `recipe list` — those are
  bare-by-default legacy sites (§3.5): without `--envelope` the CLI emits a bare dict (no
  `apiVersion`/`kind`/`status`), so the parity assertion would compare a bare CLI dict against an
  enveloped MCP result and **fail**. The new commands are always-enveloped from day one (§3.5), so
  both surfaces carry the frame unconditionally and the comparison is apples-to-apples.
- CLI: `--format json` (NO `--envelope` needed) → parse envelope. MCP: `tools/call` → read
  `structuredContent`.
- Assert `cli["apiVersion"] == mcp["apiVersion"] == "grain.engine/v1"`,
  `cli["kind"] == mcp["kind"]` (and ∈ `VALID_ENGINE_KINDS`),
  `cli["status"] == mcp["status"] == "ok"`.
- Assert the MCP result also sets `isError == (status == "error")` (here `False`).

### Family 3 — Tri-state `__post_init__` legality (§3.3)
- LEGAL constructs succeed:
  - `EngineEnvelope(kind=<valid>, status="ok", grain_version=v, data={...})`
  - `EngineEnvelope(kind=<valid>, status="gate", grain_version=v, data={...}, gate={...})`
  - `EngineEnvelope(kind=<valid>, status="error", grain_version=v, error={...})`
- ILLEGAL constructs raise:
  - `status="ok"` with `error` set; `status="ok"` with `data=None`
  - `status="gate"` with `gate=None`
  - `status="error"` with `data` set; `status="error"` with `error=None`
  - `status="bogus"` (unknown); `kind` not in `VALID_ENGINE_KINDS` for a non-error envelope.
- (This re-verifies the P35-T01 invariant at the integration layer; reuse the value matrix
  from `tests/test_engine_envelope.py`.)

### Family 4 — `docs audit --fix --format json` applies + reports `fixes_applied` (§7.1)
- Set up a temp workspace with a doc that has a fixable audit issue.
- **With consent** (`--yes`, JSON): assert the command APPLIES the fix (the on-disk file content
  changes, or a re-run audit reports clean) AND `envelope["data"]["fixes_applied"]` is a
  non-empty list naming the fix(es). Exit 0, `status: ok`.
- **Without consent** (no `--yes`, JSON, fix needed): assert `status == "gate"`,
  `gate.reason == "docs_fix_apply"`, NOTHING is applied, exit **0** (§3.3/§7.1 matrix).
- This closes the documented silent no-op (today `--format json` returns before the fix block).

### Family 5 — `grain version --check` fail-silent exit 0 on network failure (§7.2)
- `monkeypatch` `grain.adapters.pypi.fetch_latest` to raise `AdapterError` (no real network).
- Invoke `grain --format json version --check` (with cache bypass, e.g. `GRAIN_NO_UPDATE_CHECK`
  unset + a temp/empty cache, or `--refresh`).
- Assert exit code **== 0**; `envelope["status"] == "ok"` (a degraded answer is not an error);
  `data["latest"] is None`; a `check_error` is present and/or `data["source"] == "unavailable"`;
  no traceback on stderr.

### Test-file conventions
- SPDX header at top.
- Reuse existing repo fixtures (temp workspace / `grain init` helper / `CliRunner`) from the
  current `tests/`; do not invent a new harness.
- Each MCP assertion goes through the real `mcp_service` `tools/call` dispatch so the test
  exercises the same code path a familiar would (CLI canonical, MCP delegating to the same
  service function, §5.4).
- No network, no daemon, no HTTP wrapper invocation (stdio surfaces only, §2 principle 4).

## Part C — README.md
Add a concise "Headless / engine contract" section covering:
- The `grain.engine/v1` envelope (one frame: `apiVersion`/`kind`/`status`/`data`/`gate`/`error`)
  on both CLI `--format json` and stdio MCP (§3.1/§5.1).
- `--envelope` / `GRAIN_ENGINE_ENVELOPE=1` opt-in for legacy JSON sites; new commands always enveloped (§3.5).
- New commands: `grain capabilities` (list/show/`--check`), `grain workspace` (list/resolve),
  `grain version` (`--check`/`--refresh`) (§6.4/§7.2).
- Typed `grain.error/v1` errors with `grain.`-namespaced codes 1:1 with exit codes (§4).
- Non-interactive: `--yes` + `status: gate` for consent; JSON never prompts (§7.1).
- stdio MCP only; the HTTP wrapper is deployment-only / out-of-contract, no auth (§5.6).
- The PyPI freshness check is opt-in, flag-gated, fail-silent (`GRAIN_NO_UPDATE_CHECK`) (§7.2).

## Part D — CHANGELOG.md
Add a 0.5.0 (unreleased) entry. MUST include:
- Added: `grain.engine/v1` envelope; typed `grain.error/v1` errors; expanded stdio MCP surface
  (full drive loop + recipe verbs); capability registry + `grain capabilities`; `grain workspace`;
  `grain version --check` (fail-silent); `--yes`/gate non-interactive model.
- **Changed (back-compat call-outs):**
  - `suggest accept` pick-up in JSON mode now exits **0** (was 1) — it is a `status: gate`, not an error.
  - CLI `--format json` errors now print on **stdout** as a `status: error` envelope (was text on stderr).
  - **One-time pre-1.0 MCP break:** `tools/call` payload moved from `structuredContent` root to
    `data`; `ok` field → `status`.
- Fixed: `docs audit --fix --format json` silent no-op (now applies + reports `fixes_applied`).
- Note: contract bumped `toolkit_contract.md` 1.0 → 1.1 (pending human ratification of the proposal).

## Out of scope for this packet (do NOT build/test here)
- Editing any `docs/canonical/*` — proposal only (human-approved promotion follow-up).
- Any product/source code change in `src/grain/**` — T01–T10 own all behaviour; this packet
  imports/drives + documents + ratifies only.
- Conformance tests for DEFERRED items (§8): legacy-site migration / 0.6.0 default flip /
  0.7.0 removal; `grain.engine/v2` / `--api` negotiation; `suggest_accept` over MCP; recipe
  auto-mode / `workflow_loop` over MCP; `capabilities reconcile`; multi-workspace enumeration;
  `upgrade --yes`; HTTP+auth / remote MCP; background network refresh.
- Real network calls (the version-check test MUST monkeypatch `fetch_latest`).

## Acceptance Checklist
- [ ] `docs/working/change_proposals.md` has ONE new proposal; Affected Canonical Docs =
      {toolkit_contract.md, cli_spec.md, recipe_engine_spec.md}; body names 1.0→1.1, the two §5
      changes, §10 `errors`→`error` + the three groups, and §6 recipe-over-MCP; Decision =
      `needs_review`.
- [ ] No `docs/canonical/` file modified (`git status` shows only the 4 working/test/doc files).
- [ ] Family 1: each shared `ForgeError` code yields an identical `error` dict over CLI json + MCP
      (keys `{apiVersion, code, message, detail, exit_code}`, `apiVersion == "grain.error/v1"`).
- [ ] Family 2: representative ALWAYS-ENVELOPED read command (`capabilities_list`/`version_check`,
      NOT `workflow next`/`recipe list`) → identical `apiVersion`/`kind`/`status` across CLI &
      MCP; MCP `isError == (status=="error")`.
- [ ] Family 3: the 3 legal envelopes construct; each illegal combination raises.
- [ ] Family 4: `docs audit --fix --yes --format json` applies + `fixes_applied` non-empty;
      without `--yes` → `status: gate`, nothing applied, exit 0.
- [ ] Family 5: `version --check` with `fetch_latest` raising → exit 0, `latest` null,
      `check_error`/`source: unavailable` present, no network call.
- [ ] README has the "Headless / engine contract" section; CHANGELOG has the 0.5.0 entry with the
      three back-compat call-outs.
- [ ] `uv run pytest tests/test_engine_contract_conformance.py` ≥ 8 tests pass; full suite no regressions.

## Test cases to include (`tests/test_engine_contract_conformance.py`)
1. (Family 1) Parametrized round-trip of the shared error codes (missing_path/usage/validation/
   general) — CLI json `error` dict == MCP `error` dict.
2. (Family 1) `to_envelope`/`envelope_to_dict` for all 7 classes yields the §4.1 `code`/`exit_code`
   pairs with `apiVersion == "grain.error/v1"` (the codes not reachable on both live surfaces).
3. (Family 2) Read-command frame parity on an ALWAYS-ENVELOPED command (`capabilities_list` or
   `version_check`, NOT `workflow next` / `recipe list` — §3.5): CLI envelope vs MCP
   `structuredContent` — identical `apiVersion`/`kind`/`status`; `kind ∈ VALID_ENGINE_KINDS`.
4. (Family 2) MCP success result sets `isError == False` and mirrors the envelope in `content[0].text`.
5. (Family 3) Three legal envelope forms construct.
6. (Family 3) Illegal combinations each raise (parametrized: ok+error, ok+no-data, gate+no-gate,
   error+data, error+no-error, bogus status, bad kind).
7. (Family 4) `docs audit --fix --yes --format json` applies + reports `fixes_applied`.
8. (Family 4) `docs audit --fix --format json` without `--yes` → `status: gate`
   (`reason == "docs_fix_apply"`), nothing applied, exit 0.
9. (Family 5) `version --check` with patched `fetch_latest` raising `AdapterError` → exit 0,
   `latest` null, `check_error`/`source: unavailable`, no real network.
