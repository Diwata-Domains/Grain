# Branch Policy Spec

**Status:** Working spec — v0.4.0 planning (Phase 31, TASK-0211)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Problem

Teams using branch-per-phase or branch-per-task workflows have no Grain enforcement. Agents working across multiple branches silently execute against the wrong workspace state. This spec defines an opt-in branch check that warns or blocks when the active git branch doesn't match the workspace's declared policy.

---

## 2. Manifest Declaration

`docs/runtime/docs_manifest.yaml` gains a `branch_policy` block:

```yaml
branch_policy:
  mode: off             # "phase" | "task" | "off" (default)
  pattern: ""           # optional glob override; empty = use mode default
  enforce: false        # false = warn banner on stderr; true = wrong_branch stop reason
  enforce_after_days: 0 # reserved for future grace period logic; ignored in v0.4.0
  message: ""           # optional custom message shown on violation
```

**Defaults:**
- `mode: off` — absent or off means no branch checking. Zero performance cost.
- `enforce: false` — warn-only by default; no surprise blocking.
- `grain init` seeds `branch_policy: {mode: off}`.

---

## 3. Modes

### `mode: off`
No branch checking. Completely silent.

### `mode: phase`
The current git branch must contain `P{N}` where N is the active phase number.

Default matching rule: `branch contains "P{phase}"`.

Examples:
- `feature/P31-dx-hardening` ✓
- `main` ✗ (does not contain `P31`)
- `fix/P31-T08-hotfix` ✓

Custom pattern: `pattern: "*-P{phase}-*"` — uses fnmatch with `{phase}` substituted.

### `mode: task`
The current git branch must reference the active task ID or phase.

Default matching rule: branch contains `{task_id}` OR contains `P{phase}`.

Examples (active task `TASK-0211`, phase `31`):
- `feature/TASK-0211-branch-policy` ✓
- `feature/P31-T08-work` ✓ (contains `P31`)
- `main` ✗

---

## 4. Check Logic

On every `grain workflow next` invocation:

1. Read `branch_policy` from `docs_manifest.yaml`
2. If `mode: off` or block absent → skip entirely
3. Read current git branch via `git rev-parse --abbrev-ref HEAD`
4. Detached HEAD (returns `HEAD`) → treated as no-match
5. Apply pattern matching against active phase and task ID
6. If match → proceed normally
7. If no match → check escape hatch (`GRAIN_SKIP_BRANCH_CHECK=1`)
8. If bypass → log to `tooling_notes.md`, proceed
9. If `enforce: false` → add warning to evaluation; command proceeds
10. If `enforce: true` → return `wrong_branch` stop reason

### `grain workflow guard` (check #5)
Same logic applies as a named guard check `branch_policy`. Violations appear as `fail`; warn-only as `warn`.

---

## 5. Output

### Warn-only (stderr only)
```
branch 'main' does not satisfy branch_policy (mode: phase) — suggested: feature/P31-work
```
Banner appears in `evaluation.warnings`. Command proceeds with `ok: true` unless other checks block it.

### Enforce (`stop_reason: wrong_branch`)

`grain workflow next` JSON:
```json
{
  "stop_reason": "wrong_branch",
  "ok": false,
  "blocking_reasons": ["branch 'main' does not satisfy branch_policy (mode: phase) — suggested: feature/P31-work"],
  "suggested_branch": "feature/P31-work",
  "active_phase": "31"
}
```

`grain workflow guard` JSON:
```json
{
  "id": "branch_policy",
  "result": "fail",
  "severity": "error",
  "message": "branch 'main' does not satisfy branch_policy (mode: phase) — suggested: feature/P31-work",
  "remediation": "git checkout -b feature/P31-work"
}
```

---

## 6. Suggested Branch Names

| Mode | Active state | Suggestion |
|------|-------------|------------|
| phase | phase 31 | `feature/P31-work` |
| task | TASK-0211 active | `feature/TASK-0211-work` |
| task | no active task | `feature/P31-work` |

Agents can run `git checkout -b <suggested_branch>` directly from the JSON output.

---

## 7. Escape Hatch

`GRAIN_SKIP_BRANCH_CHECK=1` bypasses the branch check for one invocation.

Side effects (always, even in warn mode):
- Appends a row to `docs/working/tooling_notes.md` recording the bypass with current branch and required mode.
- Creates the file if absent.

Silent bypass is never acceptable.

---

## 8. Custom Patterns

`pattern` is a fnmatch glob with substitution variables:
- `{phase}` → active phase number (e.g. `31`)
- `{task_id}` → active task ID (e.g. `TASK-0211`)

Examples:
- `"release/*"` — any release branch
- `"*-P{phase}-*"` — explicit phase separator
- `"*/{task_id}*"` — task ID anywhere after a slash
