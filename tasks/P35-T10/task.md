# Task: Version check command

## Metadata
- **ID:** P35-T10
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T10
- **Packet Path:** tasks/P35-T10/
- **Dependencies:** P35-T01, P35-T02, P35-T03, P35-T06
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** non-interactive area deliverable #11 (`grain version --check`,
  spec §7.2). Always-enveloped new command (§3.5): wraps a `kind: VersionInfo` payload
  whose own `apiVersion: grain.version/v1` lives inside `data`. The single network
  exception (PyPI freshness, §2 principle 4 / §7.2) — flag-gated, fail-silent, exit 0.

## Objective
Implement `grain version` (and `grain version --check` / `--refresh`) as a new
always-enveloped CLI command that reports the installed grain-kit version and, on
`--check`, compares it against the latest PyPI release. Add a stdlib-only PyPI adapter
that the command calls and degrades gracefully when offline. Wire a cache-read-only
human one-liner ("a new release is available") into the `main()` preamble. The
`version_check` capability is **seeded and owned by P35-T03** (§6.2) with `surfaces ∋
"mcp"` already pinned — this packet **consumes** that seed (no re-add) and owns both the
`grain version` command AND the MCP `version_check` read tool (the tool is moved out of
P35-T06 into this packet), each delegating to one shared version-payload service function.
This delivers spec §7.2, and is the installed-vs-latest axis of the three version axes the
spec deliberately separates.

## Why This Task Exists
The headless contract requires a familiar to know whether the installed Grain is current
without a browser or a human, and a human keeper to be nudged toward upgrades without a
blocking network call in the hot path (spec §7.2). Today the version string is hardcoded
in three places (the stale `serverInfo.version` `"0.3.0-dev"`, etc.); §5.2/§10 demand a
single resolver. This packet consumes that resolver (P35-T02), the envelope/error
foundation (P35-T01), the `version_check` capability seed (P35-T03), and the MCP `_ok`
helper + extended `McpTool` (`write`+`capability`, P35-T06) to ship the user-facing
`version` surface and its MCP twin. It also proves the §2 principle-4 network carve-out: a
package-manager freshness check is the one allowed, opt-in, flag-gated network touch that
does not violate locked §4.3.

## Scope
- **Shared version-payload service function** — own a single function (e.g.
  `cli/version.py::build_version_payload(...)` or a small `services/version_service.py`)
  that builds the `grain.version/v1` `data` payload (installed/latest/cache/workspace
  logic). BOTH the CLI `grain version --check` AND the MCP `version_check` tool call this
  one function; **no version business logic lives in `mcp_service.py`** (§2 principle 5,
  §5.4). The CLI is canonical; the MCP tool is a thin delegator.
- **New `src/grain/cli/version.py`** — the `grain version` command group/command:
  - `grain version` (no flag): emit `kind: VersionInfo` with installed/install_mode/
    python/workspace; `latest`/`update_available` reflect cache if present, else null/false.
  - `grain version --check`: hit the PyPI adapter (or daily cache), populate `latest`,
    `update_available`, `upgrade_command`, `checked_at`, `source`; refresh the cache.
  - `grain version --refresh`: force a network hit even if the daily cache is fresh.
  - Always-enveloped (§3.5): the command ignores the legacy `--envelope` opt-out; the
    `data` payload carries `apiVersion: grain.version/v1` per §7.2.
  - Fail-silent: when the adapter raises `AdapterError`, catch it, set `latest: null`,
    `source: "unavailable"`, add a `check_error`, and **still exit 0** (§7.2).
  - Honor `GRAIN_NO_UPDATE_CHECK=1`: short-circuit all network/cache reads (§7.2).
- **New `src/grain/adapters/pypi.py`** — `fetch_latest(timeout: float = 2.0) -> str`
  using stdlib `urllib` only (no new deps), raising `AdapterError` (`grain.adapter`,
  exit 7) on any network/parse/timeout failure (§7.2, §4.1).
- **Daily cache** `.grain/version_check.json` (TTL 1 day); `--refresh` forces a hit;
  `source` is `"pypi" | "cache" | "unavailable"` (§7.2).
- **`_maybe_notice_new_release(root)`** in the `main()` preamble (touch
  `src/grain/cli/__init__.py`): cache-read-only (no network in hot path), text-mode only
  (never under `--format json`), non-blocking, honors `GRAIN_NO_UPDATE_CHECK`, prints one
  human line. Cache is populated only by explicit `--check` (§7.2).
- **Register `version` group** in `cli/__init__.py`; reuse `get_version()` (P35-T02) and
  `_enforce_version_gate`/`upgrade_policy.min_version` (read-only) for the `workspace`
  axis. No hardcoded version strings (§5.2, §10).
- **Capability (consume, do NOT re-add):** the `version_check` `Capability` is **seeded
  and owned by P35-T03** in `domain/capabilities.py::CAPABILITIES` (`since: 0.5.0`,
  `kind: read`, `drive: headless`, `surfaces` already pin `cli` + `mcp`, §6.2). This packet
  **consumes** that seed and does **not** re-add or re-edit the capability entry.
- **MCP tool (owned here, moved out of P35-T06):** register the `version_check` MCP
  **read** tool (`write=False`, `capability="version_check"`) using the extended `McpTool`
  + `_ok` helper from P35-T06; it returns the identical payload under the §3 envelope
  (§5.4, §5.7) by delegating to the shared version-payload service function above. P35-T06
  does NOT register this tool; T06's `tools/list` surfaces it deterministically because
  T03 pins `surfaces ∋ "mcp"`.
- **Tests** in `tests/` covering the criteria below.

## Constraints
- **MVP only (§8).** In scope: installed-vs-latest (`--check`) and installed-vs-workspace
  axes only. **Deferred / out of scope:** installed-vs-repo-source (that is `doctor`/#8 —
  link, do not duplicate, §7.2); background/opportunistic network refresh from the
  preamble; any familiar **self-execution** of the upgrade (Grain only *reports*
  `update_available`, §8). `upgrade --yes` is a different packet (§7.1).
- **Network discipline (§2 principle 4, §7.2).** `--check`/`--refresh` are the ONLY paths
  that touch the network, and only when invoked. The preamble notice is cache-read-only.
  All network/cache is suppressed by `GRAIN_NO_UPDATE_CHECK=1`.
- **Fail-silent invariant (§7.2).** A network/PyPI failure NEVER changes the process exit
  code — `grain version --check` exits 0 offline, surfacing `source: "unavailable"` +
  `check_error` in the payload. `AdapterError` is caught in the command, not propagated.
- **No hardcoded versions (§5.2, §10).** `installed` comes from `get_version()`; the
  command must not embed a literal version string.
- **Grain idioms.** New `.py` files carry the SPDX Apache-2.0 header (Grain relicensed:
  `SPDX-FileCopyrightText: 2024-2026 Shaznay Sison` / `SPDX-License-Identifier:
  Apache-2.0`). CLI is canonical; the MCP tool delegates to the same service function
  (§2 principle 5, §5.4). Errors use the `ForgeError` taxonomy (`AdapterError` →
  `grain.adapter`/7, §4.1). Stdio-only / no-daemon — no HTTP, no auth.

## Deliverable
- `src/grain/cli/version.py` (incl. the shared version-payload service function),
  `src/grain/adapters/pypi.py`, the `_maybe_notice_new_release` preamble wiring + `version`
  group registration in `cli/__init__.py`, the `version_check` MCP read tool (delegating to
  the shared service fn), and tests — all as specified in `deliverable_spec.md`. The
  `version_check` `Capability` is **consumed from P35-T03's seed, not added here.**

## Acceptance Criteria
- `grain --format json version` emits a `grain.engine/v1` envelope with `kind:
  "VersionInfo"`, `status: "ok"`, exit 0; `data.apiVersion == "grain.version/v1"`,
  `data.installed == get_version()` (no literal), and `data.latest == null` /
  `data.update_available == false` when no `--check` and no cache (§3, §7.2).
- With the PyPI adapter stubbed to a newer release, `grain --format json version --check`
  sets `data.latest`, `data.update_available == true`, a non-empty `data.upgrade_command`
  derived from `install_mode`, `data.source == "pypi"`, and a populated `data.checked_at`;
  it writes `.grain/version_check.json` (§7.2).
- With the PyPI adapter stubbed to raise `AdapterError`, `grain version --check` exits **0**,
  `data.latest == null`, `data.source == "unavailable"`, and a `check_error` is present —
  no traceback, no non-zero exit (§7.2 fail-silent).
- `--refresh` forces a network fetch even when `.grain/version_check.json` is fresh
  (assert via call count / cache mtime), while a second plain `--check` within the TTL
  reads the cache (`data.source == "cache"`) without calling `fetch_latest` (§7.2).
- `GRAIN_NO_UPDATE_CHECK=1` makes `grain version --check` perform no network or cache read
  (assert `fetch_latest` is not called and no cache file is written/read), and
  `_maybe_notice_new_release` prints nothing; the notice is also silent under `--format
  json` and emits exactly one line in text mode when the cache shows an available update
  (§7.2).
- `version_check` is present in `CAPABILITIES` as **seeded by P35-T03** (`since: 0.5.0`,
  `kind: read`, `drive: headless`, surfaces ⊇ {cli, mcp}) — this packet adds no capability
  entry; assert presence only. The MCP `version_check` read tool (registered here) returns
  a `grain.engine/v1` envelope whose `data` is **byte-for-byte equal** to the CLI `version
  --check` payload for the same stubbed inputs, proving both call the one shared service
  function with no logic in `mcp_service.py` (§2 principle 5, §5.4, §6.2).
- `uv run pytest` over the new tests passes (≥ 7 tests) with no regressions in the full suite.

## Dependencies
- **P35-T01** — `domain/envelope.py` (`EngineEnvelope`, `VALID_ENGINE_KINDS` incl.
  `VersionInfo`, `ErrorEnvelope`, `to_envelope`/`envelope_to_dict`) and the `AdapterError`
  → `grain.adapter` error wiring this command emits/catches.
- **P35-T02** — `src/grain/version.py::get_version()`, the single version resolver this
  command and the MCP tool consume for `installed` / `serverInfo.version` (§5.2, §10).
- **P35-T03** — `domain/capabilities.py::CAPABILITIES` with the **`version_check`
  `Capability` already seeded and owned** (`since: 0.5.0`, `surfaces ∋ "cli"`/`"mcp"`,
  §6.2). This packet consumes that entry (no re-add) and relies on the pinned `surfaces` so
  the T06 `tools/list` filter surfaces the tool deterministically.
- **P35-T06** — the MCP `_ok` envelope helper and the extended `McpTool`
  (`write`+`capability`) this packet uses to register the `version_check` read tool; T06
  does NOT register the `version_check` tool itself (moved here).

## Relevant Files
- `src/grain/cli/version.py` (new) — `grain version` command (`--check`/`--refresh`).
- `src/grain/adapters/pypi.py` (new) — `fetch_latest` (stdlib urllib, `AdapterError`).
- `src/grain/cli/__init__.py` (touch) — register `version` group; add
  `_maybe_notice_new_release(root)` to the `main()` preamble; reuse `get_version` and
  `_enforce_version_gate`/`upgrade_policy.min_version` (read-only) for the workspace axis.
- `src/grain/domain/capabilities.py` (dependency, P35-T03) — `version_check` `Capability`
  consumed (seeded/owned by T03; NOT edited here).
- `src/grain/services/mcp_service.py` (touch) — register the `version_check` read tool
  (thin delegator to the shared service fn; no business logic, §2 principle 5).
- `src/grain/domain/envelope.py` (dependency, P35-T01) — frame + error shapes consumed.
- `src/grain/version.py` (dependency, P35-T02) — `get_version()`.
- MCP `_ok` helper + extended `McpTool` (dependency, P35-T06) — consumed to register the tool.
- `docs/working/engine_contract_spec.md` §2, §3, §4, §5.4, §5.7, §6.2, §7.2, §8 (contract).

## Escalation Conditions
- If `install_mode` cannot be reliably detected for `upgrade_command` derivation, ship a
  conservative default (e.g. `uv tool upgrade grain-kit`) and log a change proposal rather
  than guessing fragile heuristics.
- If the canonical PyPI JSON endpoint shape or the cache schema needs a field not named in
  §7.2, stop and record a blocker rather than extending the `grain.version/v1` payload
  ad hoc (payload shape is a contract surface).
- If `_maybe_notice_new_release` cannot read the cache without risking a network call or a
  slow stat in the hot path, prefer printing nothing (non-blocking is the invariant).

## Model Recommendation
Sonnet-class can implement against this packet: the logic is mechanical given the fixed
payload shape and the fail-silent/cache rules spelled out in `deliverable_spec.md`. Use an
Opus-class model only if the cache TTL / `--refresh` / `GRAIN_NO_UPDATE_CHECK` interaction
or the CLI↔MCP payload-parity test needs design judgment.
