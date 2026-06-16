# Task: Implement upgrade enforcement — `upgrade_policy` manifest block and startup gate

## Metadata
- **ID:** TASK-0210
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T07
- **Packet Path:** tasks/P31-T07-TASK-0210/
- **Dependencies:** TASK-0206
- **Primary Adapter:** code

## Objective
Implement upgrade enforcement from `docs/working/upgrade_enforcement_spec.md`. Workspaces can declare a minimum Grain version; Grain enforces it on every invocation.

## Implementation Steps

1. **`upgrade_policy` manifest parsing** (`src/grain/services/config_service.py`):
   - Read `upgrade_policy.min_version`, `min_version_set_at`, `enforce`, `enforce_after_days`, `message` from `docs_manifest.yaml`
   - Return structured config object with defaults if block is absent
   - `min_version: ""` (empty) = no check

2. **Startup version check** (`src/grain/cli/__init__.py`):
   - Before command dispatch: read `upgrade_policy`, compare installed vs. required version
   - Compute grace period: `days_since_set = today - min_version_set_at`
   - Warn-only mode: print one banner line to **stderr** (never stdout)
   - Enforce mode: print block message to stderr, exit with code 2
   - `--format json` when blocked: JSON error on stdout, message on stderr
   - Allowed commands bypass: `grain upgrade`, `grain --version`, `grain doctor`, `grain upgrade --diff`, `grain config`

3. **`GRAIN_SKIP_VERSION_CHECK=1` escape hatch**:
   - Detect env var
   - Auto-append to `tooling_notes.md` via direct file write (not `grain notes add` — that's a stub at this point)
   - Proceed with command after logging

4. **`grain upgrade` writes `upgrade_policy`** (`src/grain/services/upgrade_service.py`):
   - After successful install, update `docs_manifest.yaml`:
     - Set `upgrade_policy.min_version` to just-installed version
     - Set `upgrade_policy.min_version_set_at` to today's ISO date
     - Leave `enforce` and `enforce_after_days` unchanged
   - If `upgrade_policy` block doesn't exist, create it with defaults (`enforce: false`)

5. **`grain init` seeds `upgrade_policy` block** (`src/grain/services/init_service.py`):
   - Add empty `upgrade_policy:` block to seeded `docs_manifest.yaml` template with `min_version: ""` and `enforce: false`

## Deliverable
- Warn-only banner appears when installed version < `min_version` and `enforce: false`
- Enforce mode blocks with exit code 2 when `enforce: true` and grace period elapsed
- Allowed commands bypass the gate
- `grain upgrade` writes `min_version` and `min_version_set_at` after success
- `GRAIN_SKIP_VERSION_CHECK=1` logs to `tooling_notes.md` and proceeds
- Tests: warn mode, enforce mode, grace period calculation, allowed-command bypass, upgrade ratchet, escape hatch logging

## Constraints
- `enforce: false` is the default — existing workspaces are not suddenly blocked
- Banner goes to **stderr** only; never pollutes stdout or `--format json` output
- `grain upgrade` ratchets `min_version` but never changes `enforce` without operator action
- Escape hatch must produce a tooling_notes entry every time — no silent bypass
