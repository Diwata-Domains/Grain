# Results — TASK-0218

## Summary

Implemented `grain metrics` for per-phase workflow velocity and stop-reason
tracking. Read-only, cached with a 1-hour TTL, JSON-exportable, and degrades
gracefully on sparse / pre-v0.4.0 metadata.

## Deliverables

- `src/grain/services/metrics_service.py` — computes per-phase duration
  (open→close, where open = prior phase's `closed_at`), task count, and closure
  rate (from `backlog.md` totals when available), plus stop-reason frequency from
  `.grain` workflow-state snapshots. Caches to `.grain/metrics_cache.json` with a
  1-hour TTL. Bespoke `@dataclass` results (`MetricsResult`, `PhaseMetrics`,
  `StopReasonCount`); never raises for expected absences; all best-effort reads.
- `src/grain/cli/metrics.py` — `grain metrics` (summary), `grain metrics --phase N`
  (single-phase detail), `grain metrics export` (full JSON history, ignores cache),
  `--no-cache` flag, and `--format json` on all paths. Group uses
  `invoke_without_command=True` (same pattern as `suggest`).
- Registered `metrics_group` in `src/grain/cli/__init__.py` (import block + add_command).

## Design notes

- Phase metadata fields vary across history: phase 31 has `closed_at` +
  `grain_version`; phases 16–30 predate the archive feature and lack them. Missing
  fields → `None`/`""` and `coverage: "partial"`, with a summary-level coverage note.
- There is no formal workflow-state history log, so stop-reason tallying reads the
  canonical `.grain/last_workflow_state.json`, any `*workflow_state*.json` siblings,
  and an optional `.grain/workflow_history/*.json` dir. Absent history → empty list.
- Closure rate derives from `backlog.md` task totals per phase when present;
  otherwise `tasks_total`/`closure_rate` are `None` and only `tasks_done` is shown.

## Test Results

- `tests/test_metrics_service.py` — 16 tests: metadata read/count, duration from
  prior close, partial coverage, dir-name phase inference, closure rate from
  backlog, stop-reason tally (eval shape, top-level shape, history dir), single-phase
  lookup, cache write/reuse/TTL-expiry/staleness, export.
- `tests/test_metrics_cmd.py` — 10 tests: summary text/json, empty, `--no-cache`,
  `--phase` detail text/json, phase-not-found (exit 2 text / ok:false json), export.
- Full suite: 1346 passed, 1 xfailed.

## Closure Decision

- **Decision:** closed
- **Reason:** all acceptance criteria met; full suite green; read-only, no archive mutation.

### Closure Blockers

- None
