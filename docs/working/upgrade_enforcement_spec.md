# Grain Upgrade Enforcement Spec

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0203)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Problem

Grain users running outdated versions against workspaces that require newer features get silent incorrect behavior. There is currently no mechanism that:
1. Tells users their Grain version is behind what the workspace requires
2. Blocks execution until they upgrade (when the workspace maintainer requires it)
3. Automatically ratchets the version requirement after a successful upgrade

---

## 2. Manifest Declaration

`docs/runtime/docs_manifest.yaml` gains an `upgrade_policy` block:

```yaml
upgrade_policy:
  min_version: "0.4.0"          # minimum installed Grain version; set by grain upgrade
  min_version_set_at: "2026-06-11"  # set by grain upgrade; drives grace period calculation
  enforce: false                # false = warn-only (default); true = block commands
  enforce_after_days: 0         # days from min_version_set_at before enforcement activates; 0 = immediate
  message: ""                   # optional custom message shown when blocked or warned
```

**Defaults:**
- `enforce: false` — existing workspaces are not suddenly blocked after Grain v0.4.0
- `enforce_after_days: 0` — when enforcement is enabled, it activates immediately unless a grace period is set
- `min_version: ""` — absent or empty means no version requirement; no check is performed

`grain init` seeds `upgrade_policy:` block with `min_version: ""` and `enforce: false`.

---

## 3. Startup Version Check Logic

On every Grain invocation (except commands listed in §4):

1. Read `upgrade_policy` from `docs_manifest.yaml`
2. If `min_version` is absent or empty → skip check, proceed normally
3. Compare installed version against `min_version` using semver comparison
4. If installed version ≥ `min_version` → proceed normally (optionally show brief "up to date" in `grain status` output)
5. If installed version < `min_version` → determine mode:
   - Compute `days_since_set = today - min_version_set_at`
   - If `enforce: false` OR `days_since_set < enforce_after_days` → **warn-only mode**
   - If `enforce: true` AND `days_since_set >= enforce_after_days` → **enforce mode**

### Warn-only mode

Print one banner line to **stderr** (never stdout):
```
⚠ Grain 0.3.11 installed; this workspace requires ≥0.4.0. Run: grain upgrade
```

Command proceeds normally. Banner appears on every invocation until upgraded.

When `--format json` is active, no banner is printed. Instead, a `"upgrade_warning"` key is added to the JSON response:
```json
{
  "upgrade_warning": {
    "installed": "0.3.11",
    "required": "0.4.0",
    "enforce_in_days": 7
  },
  ... (rest of command output)
}
```

### Enforce mode

Grain prints the block message to stderr and exits with code 2:

```
✗ Grain upgrade required

  This workspace requires Grain ≥0.4.0
  You have 0.3.11 installed.

  All workflow commands are blocked until you upgrade.

  Run:   grain upgrade
  Or:    pip install --upgrade grain-kit
         uv tool upgrade grain-kit

  To preview changes: grain upgrade --diff

  [custom message from upgrade_policy.message if set]
```

`--format json` when blocked:
```json
{
  "error": "upgrade_required",
  "installed_version": "0.3.11",
  "required_version": "0.4.0",
  "message": "All commands blocked. Run: grain upgrade",
  "upgrade_command": "grain upgrade"
}
```

Exit code 2 (not 1) — distinguishes upgrade-blocked from other errors.

---

## 4. Commands Always Allowed

These bypass the version gate entirely:

| Command | Reason |
|---------|--------|
| `grain upgrade` | The fix command; must always be reachable |
| `grain --version` | Diagnostic |
| `grain doctor` | Diagnostic |
| `grain upgrade --diff` | Preview before upgrading |
| `grain config get/set` | Needed to manage the upgrade_policy itself |

---

## 5. `grain upgrade` Writes the Policy

When `grain upgrade` successfully installs a new Grain version:

1. Sets `upgrade_policy.min_version` to the just-installed version string
2. Sets `upgrade_policy.min_version_set_at` to today's date
3. If `enforce` was already `true`, leaves it as `true` with the same `enforce_after_days`
4. If `enforce` was `false` or absent, leaves it as `false` — the maintainer must explicitly enable enforcement

This means: after `grain upgrade`, the workspace's `min_version` automatically ratchets forward. Any user on the old version who pulls the updated `docs_manifest.yaml` will immediately see the warning banner (or be blocked, if `enforce: true`).

---

## 6. Grace Period Behavior

`enforce_after_days: 7` example:

- Day 0: maintainer runs `grain upgrade` → `min_version: 0.4.0`, `min_version_set_at: 2026-06-11`, `enforce: true`, `enforce_after_days: 7`
- Days 0–6: other users see warn-only banner; commands run normally
- Day 7+: enforce mode activates; commands blocked until upgrade

The grace period is computed from `min_version_set_at` in the manifest, not from the user's local state. Everyone in the team has the same grace period window.

---

## 7. Override Escape Hatch

`GRAIN_SKIP_VERSION_CHECK=1` bypasses the version check for one invocation.

**Side effects (always):**
1. Grain automatically calls `grain notes add --type workflow_friction --command "grain <invoked-command>" --observation "GRAIN_SKIP_VERSION_CHECK=1 used; installed 0.3.11, required 0.4.0" --severity medium`
2. If `tooling_notes.md` doesn't exist, it is created first

Silent bypass is never acceptable. The escape hatch is for genuine emergencies (CI runner, offline environment) and must leave a trace.

---

## 8. Implementation Notes (Phase 31)

1. Add `upgrade_policy` block parsing to `config_service.py` (reads `docs_manifest.yaml`)
2. Add version check call at the top of `cli/__init__.py` before command dispatch
3. Implement the `enforce_after_days` + `min_version_set_at` grace period logic
4. Update `upgrade_service.py` to write `upgrade_policy.min_version` and `min_version_set_at` on successful install
5. Add bypass detection (`GRAIN_SKIP_VERSION_CHECK`) with automatic `grain notes add` call
6. Update `grain init` to seed `upgrade_policy:` block with empty defaults
7. Tests: warn-only banner appears; enforce mode blocks; allowed commands bypass; `grain upgrade` ratchets `min_version`; `GRAIN_SKIP_VERSION_CHECK` logs to tooling_notes
