# Task: Implement CLI ergonomics — `--format json` coverage, stop reasons, `grain status`

## Metadata
- **ID:** TASK-0209
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T06
- **Packet Path:** tasks/P31-T06-TASK-0209/
- **Dependencies:** TASK-0207, TASK-0208
- **Primary Adapter:** code

## Objective
Implement the CLI output ergonomics improvements from `docs/working/cli_ergonomics_spec.md`. All automation-relevant commands get stable `--format json`. Stop reasons are canonicalized. `grain status` becomes the single workspace-state command.

## Implementation Steps

### Stop reason vocabulary
File: `src/grain/services/workflow_service.py`
1. Define all 11 stop reasons as module-level constants (no inline string literals)
2. Document constants with one-line descriptions
3. Ensure every `grain workflow next` output path uses a constant, not a string

### `--format json` on new commands
Already done in their respective tasks (T04, T05), but verify:
- `grain docs audit --format json` → from T04
- `grain archive list --format json` → from T05
- `grain workflow guard --format json` → from T02

Add `--format json` to commands not covered by other tasks:
- `grain doctor --format json` — implement `grain doctor` command (spec in `docs/working/dev_runtime_alignment.md`)
- `grain notes list --format json` — stub `grain notes` command group with `list` and `add` subcommands (full implementation is Phase 37, but the stub must exist so agents can call `grain notes add` without getting "No such command")

### `grain doctor` implementation
File: `src/grain/cli/doctor.py` (new), `src/grain/services/doctor_service.py` (new)
Checks: installed version vs. pyproject.toml version, source mtime vs. install mtime, install mode (editable/installed/dev), workspace resolution.
Output: text health card + `--format json`.

### `grain --version` install mode
File: `src/grain/cli/__init__.py` or version module
Add `(editable)`, `(installed)`, or `(dev)` suffix to `grain --version` output.

### `grain status` command
File: `src/grain/cli/status.py` (new)
- Reads `.grain/last_workflow_state.json` if <5 min old, else runs `grain workflow next`
- Reads `.grain/last_docs_audit.json` if <10 min old, else runs brief audit
- Combines into workspace state summary
- Text output: phase, tasks summary, current task, workflow stop reason, health summary, install mode
- `--format json` output per spec
- `--verbose` appends full audit findings + linked workspaces + recent git summary

### Text output style
File: `src/grain/cli/output.py`
Add shared helpers for: section headers, key-value formatting (col 20 pad), symbol constants (✓ ✗ ⚠ → + ~), `→ command` hint lines.

### `cli_spec.md` JSON schemas section
File: `docs/canonical/cli_spec.md`
Add "JSON Output Schemas" section documenting top-level keys for: `grain workflow next`, `grain workflow guard`, `grain docs audit`, `grain archive list`, `grain doctor`, `grain status`.
Add canonical stop reason vocabulary table.

## Deliverable
- `grain doctor` working with `--format json`
- `grain --version` shows install mode
- `grain status` working with `--format json` and caching
- `grain notes add` stub (logs to tooling_notes.md — no CLI parsing yet; minimal stub to unblock agents)
- `cli_spec.md` JSON schemas section updated
- Tests: `grain status` returns correct JSON shape, `grain doctor` checks run, stop reason constants used

## Constraints
- `grain status` must complete in <1s for cached state; live fallback may be slower
- `grain notes add` stub must produce a correctly-formatted tooling_notes.md row
- Do not change existing command output formats — additive only
