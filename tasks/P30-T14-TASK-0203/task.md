# Task: Spec upgrade enforcement — forced upgrade gate when workspace requires newer Grain

## Metadata
- **ID:** TASK-0203
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T14
- **Packet Path:** tasks/P30-T14-TASK-0203/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a mechanism that forces Grain users to upgrade when the workspace they're operating in requires a version newer than what's installed. This is a workspace governance feature: the workspace maintainer declares a minimum Grain version; Grain enforces it on every invocation, blocking all workflow operations until the user upgrades.

## Why This Task Exists
In solo use, version drift is a nuisance. In team use or when a workspace ships v0.4.0 features (enforce/scaffold/suggest), it's a correctness problem: an operator running Grain 0.3.x against a workspace configured for 0.4.x features will silently get the wrong behavior — missing commands, ignored config, broken hooks. The operator has no signal that their version is wrong. `grain upgrade` already exists, but nothing prompts the user to run it, and nothing blocks them from proceeding with a stale install.

## Scope

### Part 1 — Manifest upgrade requirement declaration

Add an `upgrade_policy` block to `docs_manifest.yaml`:

```yaml
upgrade_policy:
  min_version: "0.4.0"           # minimum installed Grain version required
  enforce: true                  # true = block commands; false = warn only (default)
  enforce_after_days: 7          # grace period before enforcement kicks in (default: 0)
  message: ""                    # optional custom message shown when blocked
```

`min_version` is the only required field. `enforce` defaults to `false` (warn-only) so existing workspaces are not suddenly blocked. Maintainers explicitly opt into enforcement by setting `enforce: true`.

`grain upgrade` writes `min_version` automatically when it upgrades the workspace to a new Grain version — it sets `min_version` to the version it just installed. This means after running `grain upgrade`, the workspace requires that version or higher.

### Part 2 — Startup version check

On every Grain invocation (except the commands listed in Part 3), Grain reads `upgrade_policy` from `docs_manifest.yaml` and checks: is installed version ≥ `min_version`?

**Warn-only mode (`enforce: false` or within grace period):**
Every invocation prints a single banner line before the command output:
```
⚠ Grain 0.3.11 installed; this workspace requires 0.4.0. Run: grain upgrade
```
The command still runs. The banner goes to stderr, not stdout — it does not pollute `--format json` output.

**Enforce mode (`enforce: true` and grace period elapsed):**
Grain prints the block message and exits with a non-zero code before executing the command:
```
✗ Grain upgrade required

  This workspace requires Grain 0.4.0. You have 0.3.11.
  All commands are blocked until you upgrade.

  Run: grain upgrade
  Or:  pip install --upgrade grain-kit

  To check what will change: grain upgrade --diff
```
Machine-readable output (`--format json`) when blocked:
```json
{
  "error": "upgrade_required",
  "installed_version": "0.3.11",
  "required_version": "0.4.0",
  "upgrade_command": "grain upgrade"
}
```

### Part 3 — Commands always allowed

These commands bypass the version gate — they must work regardless of install version:
- `grain upgrade` — the fix command; must always be reachable
- `grain --version` — for diagnostics
- `grain doctor` — for diagnostics
- `grain upgrade --diff` — to preview changes before committing

All other commands are blocked in enforce mode.

### Part 4 — Grace period behavior

If `enforce_after_days: 7` is set, enforce mode activates 7 days after `min_version` was set (tracked by the `upgrade_policy.min_version_set_at` timestamp written by `grain upgrade`). During the grace period, the warn-only banner appears but commands are not blocked.

This gives team members time to upgrade before the gate activates — without requiring the maintainer to manually coordinate.

### Part 5 — `grain upgrade` writes the policy

When `grain upgrade` successfully installs a new Grain version, it updates `docs_manifest.yaml`:
1. Sets `upgrade_policy.min_version` to the just-installed version
2. Sets `upgrade_policy.min_version_set_at` to today's date
3. If `enforce` was already `true`, leaves it as `true`
4. If `enforce` was `false` or absent, leaves it as `false` — the maintainer must explicitly enable enforcement

This means running `grain upgrade` naturally ratchets the `min_version` forward, so the workspace always declares the version its features require.

### Part 6 — Override escape hatch

`GRAIN_SKIP_VERSION_CHECK=1` env var bypasses the version check. It is:
- Logged to `docs/working/tooling_notes.md` automatically: a `workflow_friction` entry noting the override and the version gap
- Intended for emergencies only, not routine use

## Deliverable
`docs/working/upgrade_enforcement_spec.md` — covering: manifest declaration format, startup check logic, blocked/warn output formats, grace period behavior, upgrade command write-back, override escape hatch.

## Constraints
- Must not break existing workspaces: `enforce` defaults to `false`; no workspace is suddenly blocked after upgrading to 0.4.0
- Machine-readable output must work even when blocked — the JSON error response must be parseable by agents
- `grain upgrade` must remain accessible when blocked — it is the only path out
- Grace period is optional — `enforce_after_days: 0` activates enforcement immediately after upgrade
- The override escape hatch must produce a tooling_notes entry — silent bypass is not acceptable
