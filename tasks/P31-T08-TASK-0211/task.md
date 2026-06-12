# Task: Implement branch policy — `branch_policy` manifest block and workflow gate

## Metadata
- **ID:** TASK-0211
- **Status:** ready
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T08
- **Packet Path:** tasks/P31-T08-TASK-0211/
- **Dependencies:** TASK-0205
- **Primary Adapter:** code

## Objective
Implement opt-in branch enforcement. Completely absent by default — teams that don't use branches, or use their own naming convention, are entirely unaffected. Teams that opt in get warn-only or enforced branch checks at every `grain workflow next` call.

## Design Decisions

### D1 — Opt-in only
`branch_policy` block absent from `docs_manifest.yaml` = no branch checking. `grain init` seeds `mode: off`. No surprise enforcement.

### D2 — Two modes, not a type system
`mode: phase` checks that the current git branch matches a phase-derived pattern.
`mode: task` checks that the current git branch matches a task-derived pattern.
`mode: off` (default) disables all checks.
Hotfixes and one-off work use `GRAIN_SKIP_BRANCH_CHECK=1` — no special hotfix type.

### D3 — Warn before enforce
`enforce: false` (default) emits a warning banner to stderr. Never blocks, never pollutes stdout or `--format json` output.
`enforce: true` triggers `wrong_branch` stop reason with a suggested branch name.

### D4 — Suggested branch name is actionable
When the branch doesn't match, the stop reason includes a suggested branch name the operator/agent can run `git checkout -b <suggestion>` on directly.

## Implementation Steps

### 1. Spec (`docs/working/branch_policy_spec.md`)
Write the canonical spec before touching code. Cover: config schema, default patterns per mode, grace period calculation, escape hatch behaviour, `grain init` seeding, JSON output shape.

### 2. Config parsing (`src/grain/services/config_service.py`)
Add `BranchPolicy` dataclass and `branch_policy` block reading from `docs_manifest.yaml`:
```yaml
branch_policy:
  mode: off           # "phase" | "task" | "off"
  pattern: ""         # optional override; defaults are mode-derived
  enforce: false
  enforce_after_days: 0
  message: ""         # optional custom message shown on violation
```
Default patterns:
- `mode: phase` → `*-P{phase}-*`
- `mode: task` → `*-{task_id}*` or `*-P{phase}-T{task_num}-*`

### 3. Branch detection (`src/grain/services/workflow_service.py`)
Add `_read_current_branch(root: Path) -> str` using `git rev-parse --abbrev-ref HEAD`.
After resolving active phase and active task, run branch check if `branch_policy.mode != "off"`.
Warn-only: append a warning line to the result, don't change stop reason or ok flag.
Enforce: return `wrong_branch` stop reason with `suggested_branch` in blocking_reasons.

### 4. `grain workflow guard` integration
`grain workflow guard` already runs after T02 is done. Add branch check as check #6 (after the 5 existing checks from enforcement_spec).

### 5. `GRAIN_SKIP_BRANCH_CHECK=1` escape hatch
Detect env var in branch-check path.
Auto-append to `docs/working/tooling_notes.md` (same pattern as `GRAIN_SKIP_VERSION_CHECK`).
Proceed with command after logging.

### 6. `grain init` seeding
Add absent `branch_policy:` block to seeded `docs_manifest.yaml` template with `mode: off`.

### 7. Tests
- `mode: off` → no branch check runs
- `mode: phase`, branch matches → ok
- `mode: phase`, branch mismatches, `enforce: false` → ok with warning in output
- `mode: phase`, branch mismatches, `enforce: true` → `wrong_branch` stop reason
- `mode: task`, branch matches task ID → ok
- `GRAIN_SKIP_BRANCH_CHECK=1` → logs tooling_notes entry, proceeds
- `branch_policy` block absent → no check (same as `mode: off`)

## Deliverable
- `docs/working/branch_policy_spec.md` written
- `grain workflow next` runs branch check when `branch_policy.mode != "off"`
- `grain workflow guard` includes branch check
- `grain init` seeds `branch_policy: {mode: off}` block
- `GRAIN_SKIP_BRANCH_CHECK=1` logs to tooling_notes.md and proceeds
- Tests: all 7 scenarios above pass

## Constraints
- `mode: off` (and absent block) must be completely silent — zero performance cost, zero output
- Branch detection must handle detached HEAD gracefully (treat as no-match, never crash)
- Warn-only banner goes to stderr only; never pollutes stdout or `--format json` output
- `wrong_branch` stop reason must include a `suggested_branch` field in JSON output so agents can act on it without parsing prose
