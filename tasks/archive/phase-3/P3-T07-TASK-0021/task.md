# Task: Implement Packet Status Parser and Updater

## Metadata
- **ID:** TASK-0021
- **Status:** in_progress
- **Phase:** Phase 3 — Task Packet System
- **Backlog:** P3-T07
- **Dependencies:** TASK-0019 (domain/packets.py exists)

## Objective
Extend `domain/packets.py` with status constants, transition map, `PacketRecord` dataclass, metadata parser, record reader, and status writer. Create `validators/packet_validator.py` with status value and transition validators. These are the domain primitives that P3-T03, P3-T06, P3-T08, P3-T09, P3-T11, and P3-T12 all depend on.

## Source Documents
- `docs/canonical/data_contracts.md` — Section 10 (status contract), Section 11 (transition contract), Section 9 (metadata format)
- `docs/canonical/architecture.md` — Section 6.3 (`domain/`), Section 6.5 (`validators/`)

## Constraints
- Status constants and transition map live in `domain/packets.py`
- `PacketRecord` is a dataclass: `id`, `status`, `phase`, `path`
- Metadata parser reads only the `## Metadata` block from `task.md` — no deeper parsing (Q4)
- Write logic updates only the `Status` line in the metadata block — no rewriting of other content
- `validators/packet_validator.py` imports from `domain/packets.py` — no inverse dependency
- No CLI or service changes in this task

## Escalation Conditions
- None anticipated — all status values and transitions are fully specified in data_contracts.md
