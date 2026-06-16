# Handoff: TASK-0177

## What Changed
- Added bundle-level context-budget metadata with token-warning thresholds.
- Added trim hints for the safest non-packet sources to remove first.
- Surfaced the budget in `grain context build` and `grain context export`.

## Verification
- `40 passed in 2.18s` across focused context, observability, and workflow command tests.

## Operator Notes
- Treat the budget as a deterministic proxy, not provider-native billing data.
- `P27-T03` can reuse `export_metadata.context_budget` directly for TUI panels.
