# Task: Single version resolver

## Metadata
- **ID:** P37-T02
- **Status:** draft
- **Phase:** Phase 37 — Grain-as-Engine Headless Contract
- **Backlog:** P37-T02
- **Packet Path:** tasks/P37-T02/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** version layer — the ONE version source per `engine_contract_spec.md`
  §5.2 / §10. Feeds the §3 envelope `grain_version`, MCP `serverInfo.version`, the §6
  `grain_capabilities.yaml` `grain_version`, and the §7 `grain version` command. Carries
  NO envelope shape itself (that is P37-T01); it is pure infrastructure landed in the
  T01→T02→T03 foundation so every later packet imports one resolver.

## Objective
Create `src/grain/version.py` exposing a single cached `get_version() -> str` that resolves
the installed grain-kit version via `importlib.metadata.version("grain-kit")` with a
`pyproject.toml` fallback, and make it the **only** version source in the codebase. Extract
the resolution logic currently inlined in `cli/__init__.py` (the `_VERSION` block), retire
the hardcoded MCP `serverInfo.version` `"0.3.0-dev"`, and ensure no hardcoded version string
remains anywhere a real grain-kit version is reported.

## Why This Task Exists
The headless surface today reports versions from at least two divergent sources: the
`cli/__init__.py` `_VERSION` block (correct) and a stale hardcoded MCP `serverInfo.version`
`"0.3.0-dev"` in `services/mcp_service.py` (`engine_contract_spec.md` §1, §5.2 X8). A
familiar that reads the version over MCP gets a different — and wrong — answer than over the
CLI. The contract requires "one frame, one error, one registry, one version resolver" (§2
principle 2): every surface MUST report the same version via one `get_version()` (§10). This
packet lands that resolver. It is the second of the three foundation packets (T01 envelope +
errors → **T02 version** → T03 capabilities, §8 build order) that the envelope, MCP,
capabilities, and `grain version` packets all depend on.

## Scope
- New `src/grain/version.py`:
  - `get_version() -> str` — return the installed grain-kit version.
    - Primary: `importlib.metadata.version("grain-kit")`.
    - Fallback on `PackageNotFoundError`: read `[project].version` from the nearest
      `pyproject.toml` (resolved relative to this module's location, walking up — NOT the
      process CWD, which is the fragility in the current `cli/__init__.py` fallback).
    - Final fallback (file missing/unparseable): the literal `"unknown"` (preserves the
      existing `_VERSION == "unknown"` sentinel that the version-gate logic in
      `cli/__init__.py` already keys on).
  - Cached so repeated calls do not re-hit `importlib.metadata` or the filesystem
    (`functools.lru_cache` / module-level memo — `get_version()` is idempotent within a
    process).
  - SPDX Apache-2.0 header (Grain was relicensed; new `.py` files carry it — mirror
    `src/grain/cli/__init__.py` lines 1–2).
- Modify `src/grain/cli/__init__.py`:
  - Replace the inline `_VERSION` try/except block (importlib + `tomllib` open of
    `"pyproject.toml"`) with `from grain.version import get_version` and compute
    `_VERSION = get_version()` (keep the `_VERSION` name so the existing version-gate /
    notice call sites at lines 80–264 are untouched).
- Modify `src/grain/services/mcp_service.py`:
  - Replace `MCP_SERVER_INFO = {"name": "grain", "version": "0.3.0-dev"}` so the version
    value comes from `get_version()` (resolved at emit time, not import-frozen to a literal).
- New `tests/test_version.py` covering the criteria below.

## Constraints
- **MVP only (§8).** This packet delivers the resolver and rewires the two version-reporting
  sites that exist today (`cli/__init__.py`, `mcp_service.py`). It does NOT build the
  `grain version` command (§7, separate packet), the `_meta.grainContractVersion`
  advertisement (§5.2, MCP packet), or the `grain_capabilities.yaml` writer (§6, T03/
  capabilities packet) — those each IMPORT `get_version()` when they land.
- **No new behavior beyond resolution.** No network, no PyPI freshness check (that is §7
  `adapters/pypi.py`, a different packet), no install-mode detection (already in
  `doctor_service`), no daemon. stdio-only / no-network / file-backed (§4 principle 4).
- **Forbid hardcoded version strings.** After this packet, no module may report a real
  grain-kit version from a string literal. The only permitted literal is the `"unknown"`
  fallback sentinel inside `version.py`. Re-introducing a hardcoded `"0.3.0-dev"` / `"0.5.0"`
  / any `MAJOR.MINOR.PATCH` literal as a reported version is a regression the test guards
  against (§5.2: "forbids re-introducing hardcoded version strings").
- Preserve the `"unknown"` sentinel contract: `cli/__init__.py` gates on `_VERSION ==
  "unknown"` (lines 80, 130); `get_version()` MUST return exactly `"unknown"` on total
  resolution failure, never raise.

## Deliverable
- `src/grain/version.py` with cached `get_version()` as specified in `deliverable_spec.md`.
- `src/grain/cli/__init__.py` rewired to source `_VERSION` from `get_version()`.
- `src/grain/services/mcp_service.py` sourcing `serverInfo.version` from `get_version()`.
- `tests/test_version.py` with the cases enumerated in the acceptance criteria.

## Acceptance Criteria
- `get_version()` returns `importlib.metadata.version("grain-kit")` verbatim when the package
  is installed (asserted by monkeypatching/mocking `importlib.metadata.version` to a sentinel
  and observing it is returned unchanged).
- When `importlib.metadata.version` raises `PackageNotFoundError`, `get_version()` returns the
  `[project].version` parsed from `pyproject.toml`; when that path also fails (file absent or
  unparseable) it returns exactly `"unknown"` and does not raise.
- `get_version()` is cached: two consecutive calls return the same value and the underlying
  `importlib.metadata.version` resolver is invoked at most once (assert via a call-count mock).
- `grep -rn` over `src/grain/` finds no `"0.3.0-dev"` literal and no module assigning a
  `MAJOR.MINOR.PATCH` (or `-dev`) string literal as a reported version; `MCP_SERVER_INFO`
  (or its replacement) and `cli/__init__.py` `_VERSION` both resolve through `get_version()`
  (asserted by a test that the MCP `initialize` result's `serverInfo.version` equals
  `get_version()`, not `"0.3.0-dev"`).
- `uv run pytest tests/test_version.py` passes with ≥ 4 tests, and the full suite
  (`uv run pytest`) shows no regressions (the CLI version-gate and MCP `initialize` paths
  still behave identically for an installed package).

## Dependencies
- none (foundation packet; T01 and T03 do not block T02).

## Relevant Files
- `src/grain/version.py` (new) — the single `get_version()` resolver.
- `src/grain/cli/__init__.py` (modify) — lines 6–18 inline `_VERSION` block replaced by
  `get_version()`; downstream gate/notice sites (lines 80–264) reference `_VERSION` unchanged.
- `src/grain/services/mcp_service.py` (modify) — line 18 `MCP_SERVER_INFO` and line 164
  `serverInfo` emit, sourced from `get_version()`.
- `tests/test_version.py` (new) — resolver + caching + no-hardcoded-version tests.
- `docs/working/engine_contract_spec.md` §5.2, §7.2, §8, §10 (contract for the resolver).

## Escalation Conditions
- If any reported-version call site beyond `cli/__init__.py` and `mcp_service.py` is found
  during the grep sweep (e.g. a hardcoded version in `apps/grain-mcp/main.py` or a doctor
  string), rewire it to `get_version()` if mechanical; if it requires non-trivial change,
  record a blocker rather than expanding scope — the `apps/grain-mcp` pass-through fix is
  owned by the MCP/HTTP packet (§5.6).
- If the `pyproject.toml` walk-up cannot reliably locate the file in an installed (wheel)
  layout, that is expected — the package is installed, so the importlib path succeeds and the
  fallback is dev-tree-only; do not over-engineer the fallback. Log a note if any test
  environment exercises the fallback unexpectedly.

## Model Recommendation
Sonnet-class. The resolver is small and mechanical; the only subtlety is the module-relative
`pyproject.toml` walk-up and the caching/call-count test. Follow the contract in
`deliverable_spec.md` literally.
