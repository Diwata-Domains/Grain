# Deliverable Spec: P37-T08 — Capability file writer + capabilities/workspace CLI

## Required Output

### New Files
- `tasks/P37-T08/task.md` — packet metadata/scope ✓
- `tasks/P37-T08/deliverable_spec.md` — this file ✓
- `src/grain/services/capabilities_service.py` — writer/loader/drift-check
- `src/grain/cli/capabilities.py` — `grain capabilities` group
- `src/grain/cli/workspace.py` — `grain workspace` group
- `tests/test_capabilities_service.py` — service tests
- `tests/test_cli_capabilities_workspace.py` — CLI tests

### Modified Files
- `src/grain/cli/__init__.py` — register `capabilities` + `workspace` groups
- `src/grain/cli/init.py` — call `write_capabilities_file(root)` on init
- `src/grain/cli/upgrade.py` — call `write_capabilities_file(root)` on upgrade
- `src/grain/cli/doctor.py` and/or `src/grain/services/doctor_service.py` — drift warning

All new `.py` files begin with the SPDX header block used across the repo:
```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
```

## Inputs consumed (owned by upstream packets — do NOT redefine)
- `from grain.domain.capabilities import CAPABILITIES, Capability` (P37-T03) — the one
  registry (frozen tuple) + dataclass. Fields per spec §6.1:
  `id, since, kind, drive, stability, command, description, surfaces`. Module also exposes
  `CAPABILITY_REGISTRY_API_VERSION = "grain.capabilities/v1"` and
  `GRAIN_CONTRACT_VERSION = "1.1"`.
- `from grain.version import get_version` (P37-T02) — the single version resolver.
- `from grain.domain.envelope import EngineEnvelope` (+ serializer) (P37-T01) — emit the
  `grain.engine/v1` frame for the CLI JSON output. `kind` set per command.
- The canonical-marker workspace resolver (decision #5, §6.4) — call the existing resolver
  function from the `grain.toml`-as-marker migration; do NOT hardwire
  `docs/runtime/PROJECT_RULES.md`.

## Module contract: `src/grain/services/capabilities_service.py` (spec §6.3, §10)

### Constants
```python
CAPABILITIES_REL_PATH = "docs/runtime/grain_capabilities.yaml"   # exact locked path (§3.2/§6.3)
```

### Functions
```python
def write_capabilities_file(root: str | Path) -> Path:
    """Serialize the live CAPABILITIES tuple + get_version() to
    <root>/docs/runtime/grain_capabilities.yaml and return the written path.
    Creates docs/runtime/ if absent. The file is a derived, verifiable cache —
    it is NEVER the source of truth and is never hand-edited (§6.1/§6.3)."""

def load(root: str | Path) -> dict:
    """Read + YAML-parse <root>/docs/runtime/grain_capabilities.yaml and return the dict.
    Raise ConfigError (grain.config / exit 6) if the file is missing, unreadable,
    or not valid YAML mapping."""

def check_drift(root: str | Path) -> list[str]:
    """Compare the on-disk file against the live registry + get_version().
    Return a list of human-readable drift messages (empty == no drift).
    Drift conditions:
      - top-level grain_version != get_version()
      - the set of capability ids in the file != set of live CAPABILITIES ids
        (report added and removed ids by name)
      - for any shared id, file `since` != live `since` (report id + both values)
    """
```

### On-disk file shape (`grain_capabilities.yaml`) — additive over locked §3.2
```yaml
apiVersion: grain.capabilities/v1        # the FILE's apiVersion (§6.1)
grain_contract_version: "1.1"            # bilateral schema (§6.1)
grain_version: "0.5.0"                   # from get_version() — NEVER hardcoded (§5.2/§10)
capabilities:
  - id: workflow_state                   # one mapping per Capability, registry order
    since: "0.2.0"                        # null when stability == planned
    kind: read                           # ∈ {read, write, discovery}
    drive: headless                      # ∈ {headless, confirm, interactive}
    stability: stable                    # ∈ {stable, experimental, planned}
    command: "grain workflow next"       # canonical CLI invocation; null if planned/file-only
    description: "..."
    surfaces: [cli, mcp]                 # ⊆ {cli, mcp, file}
  # ... one entry per CAPABILITIES member (seed list in §6.2)
```
- New top-level keys (`apiVersion`, `grain_contract_version`, `grain_version`) and the
  per-capability `kind/drive/stability/surfaces` are **additive**: a locked v1.0 reader
  keying on `id/command/since` is unaffected (unknown keys ignored) — §6.3.
- Serialization order follows the `CAPABILITIES` tuple order (deterministic file).

## CLI contract: `src/grain/cli/capabilities.py` (spec §6.4, always-enveloped §3.5)

```
grain capabilities                  # alias of `list`
grain capabilities list             # kind: CapabilityList  — LIVE from CAPABILITIES (§6.4)
grain capabilities show <id>        # kind: Capability      — one entry
grain capabilities --check          # drift check: exit 0 clean / exit 6 ConfigError on drift
```

- `list`/`show` read **live from `CAPABILITIES`**, never from the YAML file (§6.1/§6.4),
  so a familiar negotiates against the installed binary.
- `--format json` (and these new commands are always-enveloped):
  - `list` → `EngineEnvelope(kind="CapabilityList", status="ok",
    data={"capabilities": [<asdict per Capability>], "count": N})`.
  - `show <id>` → `EngineEnvelope(kind="Capability", status="ok",
    data={<the one capability dict>})`.
  - `show <unknown-id>` → `UsageError` → handled by `error_handler` into a
    `status="error"` envelope with `error.code == "grain.usage"`, **exit 2** (§4.3
    precedent: "unknown tool → `UsageError`" — an unknown capability id is a usage error,
    not a missing path).
  - `--check` clean → `EngineEnvelope(kind="CapabilityList", status="ok",
    data={"drift": [], "ok": true})`, **exit 0**.
  - `--check` drift → `ConfigError` → `status="error"` envelope,
    `error.code == "grain.config"`, `error.detail` = the joined drift messages,
    **exit 6**.
- `--format text` (default): human table for `list`/`show`; `--check` prints the drift
  list (or "no drift") and exits with the same codes. Never prompts (§2 principle 1).

## CLI contract: `src/grain/cli/workspace.py` (spec §6.4, always-enveloped)

```
grain workspace list        # kind: WorkspaceList  — discovery (env → walk-up)
grain workspace resolve     # echo the single resolved workspace + why
```

- Resolution: env var → walk-up via the **canonical-marker resolver** (decision #5, §6.4);
  MVP implements env + walk-up only (single active workspace, locked §8 steps 1–2).
- `list` `--format json` →
  ```jsonc
  EngineEnvelope(kind="WorkspaceList", status="ok", data={
    "workspaces": [ { "root": "<abs path>", "marker": "<grain.toml | ...>",
                      "source": "env" | "walk-up" } ],   // exactly one in MVP
    "link_enumeration": "unsupported"   // explicit boundary flag (§6.4, resolves C3)
  })
  ```
- `resolve` `--format json` →
  ```jsonc
  EngineEnvelope(kind="WorkspaceList", status="ok", data={
    "root": "<abs path>",
    "source": "env" | "walk-up",
    "reason": "GRAIN_WORKSPACE env set" | "marker found at <path>"
  })
  ```
- If no workspace resolves: `MissingPathError` (`grain.missing_path`, exit 4) in both.
- `link_enumeration: "unsupported"` is mandatory so a familiar is not misled into thinking
  one workspace is all there are (§6.4). Multi-workspace enumeration is deferred (§8).

## Wiring
- `cli/__init__.py`: `cli.add_command(capabilities)` and `cli.add_command(workspace)`.
- `cli/init.py`: after the workspace scaffold is written, call
  `capabilities_service.write_capabilities_file(root)`.
- `cli/upgrade.py`: during the upgrade flow, call
  `capabilities_service.write_capabilities_file(root)` (refresh the cache).
- `doctor`: add a check that calls `capabilities_service.check_drift(root)`; non-empty →
  emit a doctor **warning** listing the drift (NOT a hard failure — the hard-fail path is
  `capabilities --check`, §6.3).

## Out of scope for this packet (do NOT build here)
- `domain/capabilities.py` / the `Capability` dataclass / `CAPABILITIES` tuple / the
  `VALID_CAP_*` frozensets — owned by **P37-T03**; import only.
- `grain/version.py` / `get_version()` — owned by **P37-T02**; import only.
- `domain/envelope.py` / `EngineEnvelope` / error taxonomy / `error_handler` changes —
  owned by **P37-T01**; consume only.
- `grain capabilities reconcile --contract` and any "drivable verdict" logic — deferred,
  reserve the verb name only (§6.5).
- Multi-workspace / linked-workspace enumeration in `workspace list` — deferred; emit the
  `link_enumeration: "unsupported"` flag instead (§6.4, §8).
- The `capabilities_list` MCP tool / `tools/list` derived view — that is the MCP packet's
  job (§5.3/§5.7); this packet exposes only the CLI + the file + the service functions the
  MCP tool will later reuse.
- Any network / PyPI / `grain version` work (§7) — separate packet (P37-T02).
- Hardwiring `docs/runtime/PROJECT_RULES.md` as the workspace marker — forbidden (§6.4).

## Acceptance Checklist
- [ ] `write_capabilities_file(root)` writes the locked path with
      `apiVersion == "grain.capabilities/v1"`, `grain_contract_version == "1.1"`,
      `grain_version == get_version()`, and `(id, since)` pairs equal to live
      `CAPABILITIES`.
- [ ] `check_drift` returns `[]` right after a write; returns a non-empty,
      id/field-naming list after each mutation: (a) removed id, (b) changed `since`,
      (c) changed `grain_version`.
- [ ] `load` raises `ConfigError` (exit-6 mapping) on missing/malformed file.
- [ ] `grain --format json capabilities` → `kind: CapabilityList`, `status: ok`, data
      lists every live capability.
- [ ] `grain --format json capabilities show <id>` → `kind: Capability`; unknown id →
      exit 2, `error.code == "grain.usage"` (§4.3 "unknown tool → `UsageError`").
- [ ] `grain capabilities --check` exits 0 when in sync; exits 6 with
      `error.code == "grain.config"` after the file is drifted.
- [ ] `grain --format json workspace list` → `kind: WorkspaceList`,
      `data.link_enumeration == "unsupported"`, exactly one workspace entry.
- [ ] `grain --format json workspace resolve` → single resolved root + `source`/`reason`;
      resolution honors the canonical-marker resolver (env override + walk-up), no
      `PROJECT_RULES.md` hardwire.
- [ ] `grain init` then `grain capabilities --check` exits 0; `grain doctor` reports drift
      as a warning (not failure) when the file is stale.
- [ ] `uv run pytest tests/test_capabilities_service.py
      tests/test_cli_capabilities_workspace.py` ≥ 8 tests pass; full suite no regressions.

## Test cases to include
### `tests/test_capabilities_service.py`
1. `write_capabilities_file` writes the exact locked path; parsed top-level keys +
   `grain_version == get_version()`.
2. Round-trip: `(id, since)` set in the file equals the live `CAPABILITIES` set.
3. `check_drift` empty immediately after write.
4. Drift on removed/renamed id → message names the id.
5. Drift on changed `since` → message names id + both values.
6. Drift on changed `grain_version` → message names both versions.
7. `load` raises `ConfigError` on missing file and on malformed YAML.

### `tests/test_cli_capabilities_workspace.py` (CliRunner)
8. `capabilities` (json) → `kind: CapabilityList`, lists all live ids.
9. `capabilities show <known>` → `kind: Capability`; `show <unknown>` → exit 2,
   `grain.usage` (§4.3 "unknown tool → `UsageError`").
10. `capabilities --check` exit 0 in sync; exit 6 `grain.config` after the file is drifted.
11. `workspace list` (json) → `kind: WorkspaceList`,
    `data.link_enumeration == "unsupported"`.
12. `workspace resolve` honors `GRAIN_WORKSPACE` env override (source == `env`) and
    walk-up (source == `walk-up`); resolved root matches the marker, not a hardwired
    `PROJECT_RULES.md`.
13. `init` writes a file for which `capabilities --check` then exits 0; `doctor` warns
    (does not fail) on a stale file.
