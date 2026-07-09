# Deliverable Spec: P35-T02 — Single version resolver

## Required Output

### New Files
- `tasks/P35-T02/task.md` — packet metadata/scope ✓
- `tasks/P35-T02/deliverable_spec.md` — this file ✓
- `src/grain/version.py` — the single `get_version()` resolver
- `tests/test_version.py` — tests (≥ 4)

### Modified Files
- `src/grain/cli/__init__.py` — replace inline `_VERSION` block with `get_version()`
- `src/grain/services/mcp_service.py` — source `serverInfo.version` from `get_version()`

## Why one resolver (spec grounding)
- `engine_contract_spec.md` §2 principle 2: "One frame, one error, one registry, **one
  version resolver**." Every surface "report[s] the **same** version via one `get_version()`
  (§10)."
- §5.2 (resolves X8): "Factor the version resolver out of `cli/__init__.py` into a tiny
  `grain/version.py` (`get_version()` — `importlib.metadata.version("grain-kit")` with the
  `pyproject.toml` fallback, cached). It becomes the **only** version source for: envelope
  `grain_version`, MCP `serverInfo.version`, the `grain_capabilities.yaml` `grain_version`,
  and `grain version`. No hardcoded version strings anywhere (this retires the stale
  `"0.3.0-dev"` and forbids re-introducing hardcoded `"0.5.0"` examples)."
- §10 (implementation notes): "**One version resolver:** `src/grain/version.py::get_version()`
  (extracted from `cli/__init__.py`); the only source ... No hardcoded version strings."
- §8 build order: foundation packets land first — T01 (envelope+errors) → **T02 (version)** →
  T03 (capabilities); this packet is T02.

## Module contract: `src/grain/version.py`

### Header
```python
# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
```
(New `.py` file — carries the Apache-2.0 SPDX header; mirror `src/grain/cli/__init__.py`
lines 1–2.)

### Function
```python
from functools import lru_cache
from importlib.metadata import version as _dist_version, PackageNotFoundError
from pathlib import Path
import tomllib

_UNKNOWN = "unknown"          # the sentinel cli/__init__.py gates on (== "unknown")

@lru_cache(maxsize=1)
def get_version() -> str:
    """Resolve the installed grain-kit version. The ONE version source.

    Order:
      1. importlib.metadata.version("grain-kit")           -> installed dist version
      2. [project].version from the nearest pyproject.toml -> dev-tree fallback
      3. "unknown"                                         -> total-failure sentinel
    Never raises.
    """
    try:
        return _dist_version("grain-kit")
    except PackageNotFoundError:
        pass
    try:
        return _read_pyproject_version()
    except Exception:
        return _UNKNOWN


def _read_pyproject_version() -> str:
    """Walk up from this module's directory to find pyproject.toml; return its
    [project].version. Module-relative — NOT process CWD (the current cli/__init__.py
    fallback opens "pyproject.toml" relative to CWD, which is fragile)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            with open(candidate, "rb") as f:
                return tomllib.load(f)["project"]["version"]
    raise FileNotFoundError("pyproject.toml not found above grain/version.py")
```

### Behavior contract
| condition | result |
|---|---|
| `grain-kit` installed | exact string from `importlib.metadata.version("grain-kit")` |
| not installed, dev tree | `[project].version` from the nearest `pyproject.toml` (module-relative walk-up) |
| not installed, no/invalid pyproject | exactly `"unknown"` (never raises) |
| called N times | resolved once; cached (`lru_cache(maxsize=1)`) |

- `get_version()` is the only public name. `_read_pyproject_version` / `_UNKNOWN` are
  module-private.
- The function MUST NOT import anything from `grain.cli`, `grain.services`, or
  `grain.domain` — it is leaf infrastructure with no Grain-internal dependencies (so the
  envelope/MCP/capabilities packets can import it without cycles).

## Modify: `src/grain/cli/__init__.py`
- Remove the inline block (current lines 6–18): the `import tomllib`,
  `from importlib.metadata import version, PackageNotFoundError`, and the
  `try: _VERSION = version("grain-kit") ... except: _VERSION = "unknown"` ladder.
  (Leave `tomllib` import in place only if still used elsewhere in the file; otherwise drop
  it.)
- Add `from grain.version import get_version` and set `_VERSION = get_version()`.
- Keep the module-level name `_VERSION` — the version-gate and update-notice call sites
  (lines 80, 105, 115, 123, 130, 149, 156, 179, 188, 202, 216, 264) reference `_VERSION`
  and must remain unchanged. The `_VERSION == "unknown"` guards (lines 80, 130) continue to
  work because `get_version()` returns `"unknown"` on total failure.

## Modify: `src/grain/services/mcp_service.py`
- Current: `MCP_SERVER_INFO = {"name": "grain", "version": "0.3.0-dev"}` (line 18), emitted
  at the `initialize` result `"serverInfo": MCP_SERVER_INFO` (line 164).
- Required: the emitted `serverInfo.version` MUST equal `get_version()`. Acceptable shapes:
  - build the dict at emit time:
    `"serverInfo": {"name": "grain", "version": get_version()}`, or
  - keep a `MCP_SERVER_INFO` with `"name": "grain"` and inject `"version": get_version()`
    when building the `initialize` result.
- The literal `"0.3.0-dev"` MUST NOT remain in the file.
- `from grain.version import get_version` added.

## Out of scope for this packet (do NOT build here)
- `grain version` command + `--check` / `--refresh` (`cli/version.py`, §7.2) — separate packet.
- `adapters/pypi.py` PyPI freshness check, cache, `GRAIN_NO_UPDATE_CHECK`, `_maybe_notice_
  new_release` (§7) — separate packet.
- `_meta.grainContractVersion` / `engineApiVersion` advertisement on `initialize` (§5.2) —
  MCP packet.
- The `grain.engine/v1` envelope `grain_version` field wiring (§3) — that field consumes
  `get_version()` but is built in the envelope packet (T01).
- `grain_capabilities.yaml` `grain_version` serialization (§6.3) — capabilities packet (T03).
- `apps/grain-mcp/main.py` hardcoded FastAPI version (§5.6) — MCP/HTTP pass-through packet
  (only escalate here if trivially co-located; do not expand scope).
- install-mode detection (already `doctor_service.detect_install_mode`).

## Acceptance Checklist
- [ ] `src/grain/version.py` exists with the Apache-2.0 SPDX header and a cached
      `get_version() -> str`.
- [ ] Installed path: mocking `importlib.metadata.version` to a sentinel string returns that
      string verbatim from `get_version()`.
- [ ] Fallback path: with `version` raising `PackageNotFoundError`, `get_version()` returns
      the `pyproject.toml` `[project].version`; with both unavailable it returns exactly
      `"unknown"` and does not raise.
- [ ] Caching: two calls return the same value; the underlying resolver is invoked at most
      once (call-count assertion). (Clear the cache between tests via
      `get_version.cache_clear()`.)
- [ ] `"0.3.0-dev"` no longer appears in `src/grain/`; MCP `initialize` `serverInfo.version`
      == `get_version()` (asserted by calling the MCP initialize handler).
- [ ] `cli/__init__.py` `_VERSION` is sourced from `get_version()` and the `"unknown"`
      sentinel still gates the version checks.
- [ ] `uv run pytest tests/test_version.py` ≥ 4 tests pass; `uv run pytest` full suite no
      regressions.

## Test cases to include (`tests/test_version.py`)
1. Installed: monkeypatch `grain.version._dist_version` to return `"9.9.9"`; assert
   `get_version() == "9.9.9"` (call `cache_clear()` first).
2. Fallback: monkeypatch `_dist_version` to raise `PackageNotFoundError`; assert
   `get_version()` returns a valid semver string read from the repo `pyproject.toml`
   (`[project].version`).
3. Total failure: monkeypatch `_dist_version` to raise `PackageNotFoundError` AND
   `_read_pyproject_version` to raise; assert `get_version() == "unknown"` and that no
   exception propagates.
4. Caching: monkeypatch `_dist_version` with a call counter; call `get_version()` twice;
   assert equal results and the counter == 1.
5. No-hardcoded-version guard: read `src/grain/services/mcp_service.py` source and assert
   `"0.3.0-dev"` is absent; call the MCP `initialize` handler and assert the returned
   `serverInfo["version"] == get_version()`.
