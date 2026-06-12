# Dev/Runtime Alignment Diagnostics

**Status:** Working decision document — v0.4.0 planning (Phase 30, TASK-0194)

---

## 1. Problem Statement

During active development of Grain, the installed CLI binary (`grain`) frequently lags the source code being edited. A developer modifies `src/grain/services/workflow_service.py`, runs `grain workflow next`, and the old behavior runs. The mismatch is silent — there is no indicator that the running binary doesn't reflect the current source tree.

This creates two distinct failure modes:
1. **Editable install drift:** Developer installed Grain with `pip install -e .` but switched git branches or reverted changes; the editable install points to files that have diverged from what they expect
2. **Stale global install:** Developer installed Grain via `uv tool install grain-kit` at version 0.3.x, is now working in a repo that has source for 0.4.x; they're running old code against new docs

Both are silent and confusing. The diagnostic surface must make both visible on demand.

---

## 2. Design Decision

**Option A — Version hash comparison only:** Compare installed package version string against `pyproject.toml` version in the repo. Simple but only catches inter-version drift; misses same-version editable-install drift.

**Option B — Source file mtime comparison:** Compare mtime of installed package files against repo source. Reliable for editable installs but fragile for non-editable global installs and adds filesystem scan overhead.

**Option C — Install type flag in `--version` + `grain doctor` for full diagnosis:** Detect editable vs. non-editable install mode and surface it in `grain --version`. Add a dedicated `grain doctor` command for full diagnostic state.

**Decision: Option C (install type flag + `grain doctor`)**

Rationale:
- Option A misses the most common case (editable drift)
- Option B adds overhead to every invocation — violates "no latency on normal CLI invocations" constraint
- Option C makes the install type visible at a glance (`grain --version` output includes install mode), and moves the heavier diagnosis to an explicit `grain doctor` command the developer runs when they suspect drift

---

## 3. `grain --version` Changes

Current output: `grain 0.4.0`

New output:
```
grain 0.4.0 (installed)       ← non-editable global install
grain 0.4.0 (editable)        ← pip install -e . from source
grain 0.4.0 (dev)             ← running directly from source tree, not installed
```

Install mode detection:
- Check if the running module's `__file__` path is within a `.dist-info` editable install marker (`direct_url.json` with `"editable": true`)
- Fallback: check for the presence of `__editable__` marker in the package dist-info
- If running as a direct `python -m grain` invocation from the source tree without install, report `(dev)`

This adds negligible overhead — `importlib.metadata` reads are fast and `grain --version` is never called in a hot path.

---

## 4. `grain doctor` Command

A standalone diagnostic command. Not called by other commands. Developer-invoked when they want to understand the current install state.

```
grain doctor
grain doctor --format json
```

### Output (text mode)

```
Grain Doctor — 2026-06-11

Install:
  version       0.4.0
  install mode  editable
  install path  /Users/dev/.venv/lib/python3.12/site-packages/grain/
  source path   /Users/dev/Diwata/Diwata-Labs/products/grain/

Alignment:
  pyproject.toml version  0.4.0            ✓ matches installed
  source mtime            2026-06-11 14:32  (most recently modified file)
  installed mtime         2026-06-11 14:30  ✓ installed within 2 min of source change

Workspace:
  resolved root           /Users/dev/Diwata/Diwata-Labs/products/grain/
  workspace name          grain
  workspace type          product

Python:
  version     3.12.4
  executable  /Users/dev/.venv/bin/python

Checks: 4/4 pass
```

When drift is detected:

```
Alignment:
  pyproject.toml version  0.4.1-dev        ✗ source is ahead of installed (0.4.0)
  → Run: pip install -e . to reinstall from source

  source mtime            2026-06-11 16:45  (most recently modified file)
  installed mtime         2026-06-11 14:30  ✗ installed 2h15m before last source change
  → Files modified since install: 3 (grain/services/workflow_service.py, ...)
```

### Checks performed

| Check | How | Fail condition |
|-------|-----|----------------|
| Version match | Compare `importlib.metadata` version vs. repo `pyproject.toml` | Repo version > installed version |
| Source mtime | Compare `max(src/**/*.py mtime)` vs. dist-info `RECORD` install mtime | Source files modified after install |
| Install mode | Read `direct_url.json` in dist-info | `(installed)` when developer expects `(editable)` |
| Python env | Report Python version and executable path | No fail — informational only |
| Workspace resolution | Run workspace resolution and report result | Reports `unresolved` if no PROJECT_RULES.md found |

### `--format json` output

```json
{
  "grain_version": "0.4.0",
  "install_mode": "editable",
  "install_path": "...",
  "source_path": "...",
  "pyproject_version": "0.4.1-dev",
  "version_match": false,
  "source_mtime": "2026-06-11T16:45:00",
  "install_mtime": "2026-06-11T14:30:00",
  "source_files_modified_since_install": ["grain/services/workflow_service.py"],
  "workspace_root": "...",
  "python_version": "3.12.4",
  "checks": {
    "version_match": false,
    "mtime_ok": false,
    "install_mode_ok": true,
    "workspace_resolved": true
  },
  "overall": "drift_detected"
}
```

---

## 5. Integration Points

### `grain workflow guard`
`grain workflow guard` runs `grain doctor --format json` internally if `--check-dev-alignment` flag is passed and reports drift as a warning (not a violation). This is opt-in — normal guard runs don't add doctor overhead.

### Session start prompt
`prompts/workflow.resume.md` (from T08 spec) should include: "If you see unexpected CLI behavior, run `grain doctor` to check for install/source drift before troubleshooting further."

---

## 6. Non-Goals

- Automatic reinstall — `grain doctor` reports; the developer runs `pip install -e .` themselves
- Watching for changes and auto-reinstalling (a file watcher) — outside local-first, no-daemon constraint
- Checking sibling tool alignment (Assay, Conclave) — each tool runs its own `doctor` equivalent
- Adding drift checks to every Grain command invocation — `grain doctor` is the explicit check path; normal commands don't pay the overhead
