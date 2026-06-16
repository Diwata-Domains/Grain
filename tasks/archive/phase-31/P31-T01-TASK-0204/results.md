# Results — TASK-0204

## Summary

Fixed 4 DX bugs (3 from Phase 30 tooling notes + 1 surfaced during Phase 30 execution). All 1024 tests pass.

## Deliverables

### Bug 1 — Stale task pointer routing (workflow_service.py)
**Status:** fixed

Root cause: `packet_status == "done"` branch set `active_task_id = "none"` silently, allowing the router to fall through to the next ready task without surfacing the stale pointer.

Fix: return `stale_task_pointer` stop reason immediately when `current_task.md` points to a completed packet. Agent/operator must clear `Task ID:` to `none` before the workflow advances.

### Bug 2 — Packet ID reuse after archiving (domain/packets.py)
**Status:** already fixed (no change needed)

`next_task_id()` already uses `tasks_root.rglob("*")` and the docstring confirms archive scanning. No code change required.

### Bug 3 — `grain phase close` missing `--phase` flag (cli/phase.py, services/phase_close_service.py)
**Status:** fixed

Added `--phase` / `-p` flag to `grain phase close`. When provided, validates that the given phase matches the active phase exactly — guards against accidentally closing the wrong phase. Service signature updated to `close_phase(root, dry_run=False, phase_override=None)`.

### Bug 4 — `--format` global flag order in docs (multiple files)
**Status:** fixed

`--format` is a global option on the `grain` group — it must come before subcommands (`grain --format json workflow next`, not `grain workflow next --format json`).

Fixed in: `docs/runtime/AGENTS.md`, `docs/runtime/CLAUDE.md`, `docs/canonical/enforcement_spec.md`, `docs/canonical/toolkit_contract.md`, `docs/working/current_focus.md`, `README.md`, `prompts/task.execute.md`, `prompts/tasks.next_and_implement.md`, `src/grain/data/prompts/task.execute.md`, `src/grain/data/prompts/tasks.next_and_implement.md`.

Added note to `docs/canonical/cli_spec.md` §4.3 documenting the global flag placement rule.

### Bonus — Simple packet validator (validators/packet_validator.py)
**Status:** fixed (surfaced during Phase 30 T14, high severity)

`validate_packet_files` now detects simple packets: `task.md` exists but no planning files (`context.md`, `plan.md`, `deliverable_spec.md`) are present. Simple packets pass file validation. Once any planning file exists, all three are required (prevents partial setups from silently passing).

Added three new tests: simple packet passes, partial planning files fail, and behaviour when `task.md` is absent.

## Test Results
- Pre-fix: 557 pass, 1 fail (simple packet)
- Post-fix: 1024 pass, 0 fail, 1 xfail

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
