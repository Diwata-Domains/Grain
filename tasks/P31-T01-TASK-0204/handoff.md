# Handoff — TASK-0204

## What changed

- `src/grain/services/workflow_service.py` — stale pointer now surfaces `stale_task_pointer` stop reason instead of silent reset
- `src/grain/services/phase_close_service.py` — `close_phase()` accepts `phase_override`; validates against active phase
- `src/grain/cli/phase.py` — `grain phase close` has `--phase`/`-p` flag
- `src/grain/validators/packet_validator.py` — simple packet detection; `_PLANNING_FILES` constant added
- Multiple docs — `--format` global flag order corrected throughout

## What T02 needs to know

- `stale_task_pointer` is now a live stop reason; the enforcement spec (T02) should list it in the stop reason vocabulary
- `validate_packet_files` is now safe to call on simple packets without stub files
- `grain phase close --phase N` is available for agent scripts that need to be explicit about which phase they're closing
