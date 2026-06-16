# Results — TASK-0203

## Status
done — 2026-06-11

## Deliverable
`docs/working/upgrade_enforcement_spec.md` — upgrade enforcement spec.

## Key Decisions

**`upgrade_policy` in manifest:** `min_version`, `min_version_set_at`, `enforce` (default false), `enforce_after_days` (default 0), optional `message`. Seeded as empty defaults by `grain init`.

**`enforce: false` default:** Existing workspaces are not suddenly blocked. Maintainer must explicitly opt in to enforcement.

**`grain upgrade` ratchets `min_version`:** After successful upgrade, manifest automatically updates. Team members pulling the updated manifest immediately see the warning.

**Warn-only banner:** Stderr only. JSON mode adds `upgrade_warning` key instead of banner. Never pollutes stdout.

**Enforce mode:** Exit code 2. JSON error `"error": "upgrade_required"`. Allowed commands: `grain upgrade`, `grain --version`, `grain doctor`, `grain upgrade --diff`, `grain config`.

**Override escape hatch:** `GRAIN_SKIP_VERSION_CHECK=1`. Always logs a `workflow_friction` entry to tooling_notes via `grain notes add`.

## Files Changed
- `docs/working/upgrade_enforcement_spec.md` — created
- `tasks/P30-T14-TASK-0203/task.md` — status set to done
