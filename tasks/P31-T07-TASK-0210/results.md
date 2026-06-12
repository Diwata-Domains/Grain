# Results — TASK-0210

## Summary

All upgrade enforcement deliverables implemented. 1158 tests pass (29 new).

## Deliverables

### `UpgradePolicy` dataclass + `load_upgrade_policy()` (`manifest.py`)
Fields: `min_version`, `min_version_set_at`, `enforce`, `enforce_after_days`, `message`. Defaults to no-op when block is absent or `min_version` is empty.

### `upgrade_policy:` block in manifest template (`docs_manifest.yaml`)
Seeds with `min_version: ""` and `enforce: false` — existing workspaces are never suddenly blocked.

### Version gate (`cli/__init__.py`)
`_enforce_version_gate()` runs on every invocation except bypass commands (`upgrade`, `doctor`, `config`).
- Warn-only mode: banner to stderr when `enforce: false` or within grace period; suppressed in json format.
- Enforce mode: JSON error to stdout + verbose message to stderr + `sys.exit(2)`.
- Grace period: `enforce_after_days` computed from `min_version_set_at`; grace = warn, elapsed = block.
- `GRAIN_SKIP_VERSION_CHECK=1`: bypasses gate; writes row to `tooling_notes.md` every time.

### `write_upgrade_policy_min_version()` (`upgrade_service.py`)
Surgical line-based replacement of `min_version` and `min_version_set_at` in `docs_manifest.yaml`; preserves comments and all other fields. Appends block with defaults if absent.

### Ratchet on `grain upgrade` (`cli/upgrade.py`)
After a non-dry-run `grain upgrade`, calls `write_upgrade_policy_min_version()` with the installed Grain version. Dry-run and `--diff` modes do not ratchet.

### Tests (`test_upgrade_enforcement.py`)
29 tests: `load_upgrade_policy` parsing, no-gate conditions, warn mode, enforce mode, JSON enforce, custom message, grace period (start/elapsed/boundary), allowed-command bypass, `GRAIN_SKIP_VERSION_CHECK` (enforce/warn/append), `write_upgrade_policy_min_version` (update/create/no-manifest/preserves), dry-run no-ratchet.

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
