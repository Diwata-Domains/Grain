# Results — TASK-0211

## Summary

All branch policy deliverables implemented. 1189 tests pass (31 new).

## Deliverables

### `docs/working/branch_policy_spec.md`
Full spec covering config schema, modes (phase/task/off), matching logic, suggested branches, escape hatch, custom patterns, and JSON output shapes.

### `BranchPolicy` dataclass + `load_branch_policy()` (`manifest.py`)
Fields: `mode`, `pattern`, `enforce`, `enforce_after_days`, `message`. Invalid `mode` values fall back to `off`. Never raises.

### `branch_policy:` block in manifest template (`docs_manifest.yaml`)
Seeds with `mode: off` — teams that don't use branches are completely unaffected.

### `WorkflowEvaluation.suggested_branch` field (`domain/workflow.py`)
New field on the evaluation dataclass. Populated when `stop_reason == "wrong_branch"` to give agents an actionable `git checkout -b <suggestion>` target.

### `STOP_WRONG_BRANCH` constant + branch check helpers (`workflow_service.py`)
- `STOP_WRONG_BRANCH = "wrong_branch"` constant
- `_read_current_branch()` — subprocess call; returns `""` on detached HEAD or no-git
- `_branch_matches()` — fnmatch for custom patterns; substring check for mode defaults
- `_suggest_branch()` — generates `feature/P{N}-work` or `feature/{task_id}-work`
- `_apply_branch_policy_check()` — post-processor wrapping `evaluate_workflow_state`; warn adds to `evaluation.warnings`; enforce replaces with `wrong_branch` evaluation
- `_log_branch_skip_to_tooling_notes()` — writes row on `GRAIN_SKIP_BRANCH_CHECK=1`
- `evaluate_workflow_state` is now a thin wrapper around `_evaluate_workflow_state_core` + `_apply_branch_policy_check`

### Workflow next warnings rendering (`cli/workflow.py`)
Text output now renders `evaluation.warnings` to stderr after other fields.

### Guard check #5 (`guard_service.py`)
`_check_branch_policy()` runs on every `grain workflow guard` call. `mode: off` → pass (no git call). Mismatch + `enforce: false` → warn. Mismatch + `enforce: true` → fail with `git checkout -b <suggestion>` remediation.

### Tests (`test_branch_policy.py`)
31 tests: `load_branch_policy` parsing + invalid mode fallback, `_branch_matches` (phase/task/custom/empty), `mode: off` no-check, matching branch ok, warn-only mode (text + JSON), enforce mode (wrong_branch + suggested_branch in JSON), task mode, `GRAIN_SKIP_BRANCH_CHECK` (enforce/warn/tooling_notes), `WorkflowEvaluation.suggested_branch` field, `_suggest_branch`, guard (off/warn/fail/remediation).

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
