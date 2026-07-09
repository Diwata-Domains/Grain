# Deliverable Spec: P37-T10 — Version check command

## Required Output

### New Files
- `tasks/P37-T10/task.md` — packet metadata/scope ✓
- `tasks/P37-T10/deliverable_spec.md` — this file ✓
- `src/grain/cli/version.py` — the `grain version` command (`--check`/`--refresh`) **plus
  the shared version-payload service function** both the CLI and the MCP tool delegate to
  (CLI canonical, §2 principle 5). (A small `services/version_service.py` is an acceptable
  alternative home for the function — but the logic lives here, NOT in `mcp_service.py`.)
- `src/grain/adapters/pypi.py` — `fetch_latest` (stdlib urllib + `AdapterError`).
- `tests/test_version_command.py` (and/or `tests/test_pypi_adapter.py`) — tests (≥ 7).

### Modified Files
- `src/grain/cli/__init__.py` — register the `version` group; add
  `_maybe_notice_new_release(root)` to the `main()` preamble.
- `src/grain/services/mcp_service.py` — register the `version_check` read tool + schema as
  a **thin delegator** to the shared service function (no business logic, §2 principle 5).

### Consumed (NOT modified here)
- `src/grain/domain/capabilities.py` — the `version_check` `Capability` is **seeded and
  owned by P37-T03** (with `surfaces ∋ "cli"`/`"mcp"` pinned); this packet consumes it and
  does NOT add or edit the entry.
- The MCP `_ok` envelope helper and the extended `McpTool` (`write`+`capability`) from
  **P37-T06** — consumed to register the tool; T06 does not register `version_check` itself.

Every new `.py` file begins with the SPDX header:
```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
```

## Module contract: `src/grain/adapters/pypi.py` (§7.2, §4.1)

```python
PYPI_JSON_URL = "https://pypi.org/pypi/grain-kit/json"

def fetch_latest(timeout: float = 2.0) -> str:
    """Return the latest released grain-kit version string from PyPI.

    Stdlib only (urllib.request) — NO new dependencies. On any failure
    (network error, timeout, non-200, malformed JSON, missing
    info.version) raise AdapterError (code grain.adapter, exit 7).
    The CALLER catches AdapterError and degrades — this function never
    swallows the error itself.
    """
```
- Parses `info.version` from the PyPI JSON response.
- Uses an explicit `timeout` on the `urlopen` call (default 2.0s).
- No caching here (cache lives in the CLI layer); this is a pure fetch.

## CLI contract: `src/grain/cli/version.py` (§7.2, §3)

### Signature
```
grain version [--check] [--refresh]
# inherits global --format {text,json} from the root group
```
- `--check`: resolve `latest` (cache-or-network), set update fields, write cache.
- `--refresh`: imply `--check` semantics but force a network fetch (bypass TTL).
- No flag: report installed/workspace only; `latest`/`update_available` reflect a fresh
  cache entry if one exists, else `null`/`false` (no network).
- **Always-enveloped** (§3.5): emits the `grain.engine/v1` frame regardless of the
  `--envelope` opt-out; under `--format text` prints a human summary instead of JSON.

### Emitted envelope (`--format json`, §3.1, §3.3)
```jsonc
{
  "apiVersion": "grain.engine/v1",
  "kind": "VersionInfo",
  "status": "ok",
  "grain_version": "<get_version()>",
  "command": "version",
  "data": { /* grain.version/v1 payload, below */ },
  "gate": null,
  "error": null,
  "warnings": []
}
```
`status` is always `ok` for this command — even offline (fail-silent). A genuinely
malformed invocation (bad flag) is a `UsageError` (`grain.usage`/2) via the central
`handle_error`, not this command's concern.

### `data` payload — `grain.version/v1` (§7.2, verbatim shape)
```jsonc
{
  "apiVersion": "grain.version/v1",
  "installed": "0.5.0",                 // get_version() — NEVER a literal
  "install_mode": "uv-tool",            // detected; drives upgrade_command
  "python": "3.12.3",                   // platform.python_version()
  "latest": "0.5.1",                    // null without --check or on failure
  "update_available": true,             // installed < latest; false if latest is null
  "upgrade_command": "uv tool upgrade grain-kit",  // derived from install_mode
  "checked_at": "2026-06-28T00:00:00Z", // UTC ISO-8601; null if never checked
  "source": "pypi",                     // "pypi" | "cache" | "unavailable"
  "workspace": { "required": "0.4.0", "satisfied": true }  // from upgrade_policy.min_version
}
```
- On `AdapterError`: `latest = null`, `update_available = false`,
  `source = "unavailable"`, and a `check_error` key (short string) is added to `data`;
  process still exits **0**.
- `workspace` reuses the existing `upgrade_policy.min_version` / `_enforce_version_gate`
  read path (read-only — this command does not block or mutate). When no workspace policy
  is set, `required = null`, `satisfied = true`.

### `install_mode` → `upgrade_command` mapping (MVP)
| install_mode | upgrade_command |
|---|---|
| `uv-tool` | `uv tool upgrade grain-kit` |
| `pipx` | `pipx upgrade grain-kit` |
| `pip` | `pip install --upgrade grain-kit` |
| unknown | `uv tool upgrade grain-kit` (conservative default; see escalation) |

## Cache: `.grain/version_check.json` (§7.2)
- Written under the resolved workspace root's `.grain/` dir on every `--check`/`--refresh`.
- Daily TTL: a plain `--check` within 24h of `checked_at` reads the cache
  (`source = "cache"`) and does NOT call `fetch_latest`. `--refresh` ignores the TTL and
  forces a fetch (`source = "pypi"`).
- Stores at least `{ "latest": "...", "checked_at": "<UTC ISO-8601>" }`.
- `GRAIN_NO_UPDATE_CHECK=1` short-circuits BOTH network and cache (no read, no write).

## Preamble notice: `_maybe_notice_new_release(root)` (§7.2)
- Called from the `main()` preamble in `cli/__init__.py`.
- **Cache-read-only** — never calls `fetch_latest` or any network path.
- Text-mode only: prints nothing when the invocation is `--format json`.
- Honors `GRAIN_NO_UPDATE_CHECK`; prints nothing when set.
- Non-blocking: any read error → print nothing (never raise into the preamble).
- When the cache shows `installed < latest`, prints exactly ONE line to stderr, e.g.
  `Grain 0.5.1 is available (you have 0.5.0). Run: uv tool upgrade grain-kit`.

## Capability registry entry — CONSUMED from P37-T03 (`domain/capabilities.py`, §6.2)
**Do NOT add or edit this entry — P37-T03 seeds and owns it.** It is reproduced here only
so the MCP tool and the presence-assertion test know the exact contract shape they consume:
```python
Capability(
    id="version_check",
    since="0.5.0",
    kind="read",
    drive="headless",
    stability="stable",
    command="grain version --check",
    description="Report installed grain-kit version and check PyPI for a newer release.",
    surfaces=("cli", "mcp"),   # pinned by T03 — drives the T06 tools/list filter
)
```

## MCP tool — OWNED here, moved out of P37-T06 (`services/mcp_service.py`, §5.4, §5.7)
- Register a **read** tool `version_check` (`write=False`, `capability="version_check"`)
  using the **`McpTool` (`write`+`capability`) and `_ok` helper delivered by P37-T06**.
- Delegates to the SAME shared version-payload service function the CLI command calls (CLI
  canonical, §2 principle 5 / §5.4) — **no business logic duplicated in `mcp_service.py`**.
- Returns the §3 envelope via `_ok(tool="version_check", kind="VersionInfo", data=<payload>)`;
  the `data` is byte-for-byte the CLI `version --check` payload for identical inputs.
- `serverInfo.version` and the payload `installed` both come from `get_version()` (§5.2) —
  this tool must not reintroduce a hardcoded version.
- Because T03 pins `surfaces ∋ "mcp"`, the T06 `tools/list = filter(surfaces ∋ "mcp")`
  surfaces this tool deterministically; T06 itself registers no `version_check` tool.

## Out of scope for this packet (do NOT build here, §8)
- Installed-vs-repo-source comparison (that is `doctor`/#8 — link, don't duplicate).
- Background / opportunistic network refresh from the preamble (preamble is cache-only).
- Familiar self-execution of the upgrade — Grain only *reports* `update_available`.
- `upgrade --yes` and the `gate()` confirmation flow (§7.1, separate packet).
- The envelope dataclass, `ErrorEnvelope`, `to_envelope`/`envelope_to_dict`, and
  `get_version()` themselves (delivered by P37-T01 / P37-T02 — consumed here, not built).
- Multi-index / private-index PyPI configuration (single canonical PyPI JSON endpoint).

## Acceptance Checklist
- [ ] `grain --format json version` → `kind: VersionInfo`, `status: ok`, exit 0,
      `data.apiVersion == grain.version/v1`, `data.installed == get_version()`,
      `data.latest == null`, `data.update_available == false` (no `--check`, no cache).
- [ ] `version --check` with a stubbed-newer `fetch_latest` → `latest` set,
      `update_available == true`, non-empty `upgrade_command` from `install_mode`,
      `source == "pypi"`, `checked_at` populated, `.grain/version_check.json` written.
- [ ] `version --check` with `fetch_latest` raising `AdapterError` → exit **0**,
      `latest == null`, `source == "unavailable"`, `check_error` present, no traceback.
- [ ] `--refresh` forces a fetch even with a fresh cache; a plain `--check` within TTL
      reads the cache (`source == "cache"`) without calling `fetch_latest`.
- [ ] `GRAIN_NO_UPDATE_CHECK=1` → no network and no cache I/O on `--check`;
      `_maybe_notice_new_release` prints nothing (also silent under `--format json`);
      exactly one stderr line in text mode when the cache shows an available update.
- [ ] `version_check` present in `CAPABILITIES` (seeded by P37-T03; `since 0.5.0`, read,
      headless, surfaces ⊇ {cli, mcp}) — assert presence only, packet adds no entry. MCP
      `version_check` tool (registered here) returns the §3 envelope whose `data` is
      byte-for-byte equal to the CLI `--check` payload for the same inputs (one shared
      service fn; no logic in `mcp_service.py`).
- [ ] `uv run pytest` → ≥ 7 new tests pass; full suite no regressions.

## Test cases to include
1. JSON envelope shape + `kind`/`status`/`installed` (no `--check`, no cache).
2. `--check` happy path (stub `fetch_latest` → newer): update fields, cache written,
   `source == "pypi"`.
3. `--check` offline: `fetch_latest` raises `AdapterError` → exit 0, `unavailable`,
   `check_error`, no traceback.
4. Cache hit: second `--check` within TTL reads cache (`source == "cache"`),
   `fetch_latest` not called (assert call count 0).
5. `--refresh`: forces `fetch_latest` even with a fresh cache (assert call count ≥ 1).
6. `GRAIN_NO_UPDATE_CHECK=1`: no network, no cache read/write; preamble notice silent.
7. `_maybe_notice_new_release`: one line in text mode when cache shows an update; silent
   under `--format json` and when `GRAIN_NO_UPDATE_CHECK` is set.
8. CLI↔MCP payload parity: `version_check` MCP tool `data` equals the CLI `--check`
   payload for identical stubbed inputs (§5.4 / frame-parity).
9. `install_mode` → `upgrade_command` mapping covers `uv-tool`/`pipx`/`pip`/unknown.
