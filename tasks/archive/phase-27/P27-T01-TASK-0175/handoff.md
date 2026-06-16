# Handoff: TASK-0175

## What Changed
- Added packet-local `observability.json` support for active task execution metadata.
- Added `grain task observe` for manual inspection and updates.
- Surfaced active-task observability in `grain workflow next`.
- Recorded automatic workflow activation and close actions.

## Verification
- `25 passed in 0.93s` across task-observe, workflow-next, and workflow-run focused tests.

## Operator Notes
- Use `grain task observe --executor <id> --model-class <class> --stage execute --action <action>` when external agents perform work that Grain cannot infer directly.
- Later Phase 27 tasks can reuse the same packet-local JSON rather than inventing a new state channel.
