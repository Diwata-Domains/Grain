# Task: Implement Packet Directory Creation

## Metadata
- **ID:** TASK-0022
- **Status:** done
- **Phase:** Phase 3 — Task Packet System
- **Backlog:** P3-T03
- **Dependencies:** TASK-0019 (next_task_id), TASK-0020 (templates exist)

## Objective
Implement `create_packet_directory(root, phase, task_num)` in `services/task_service.py`. Allocates next TASK-#### ID, constructs `P<N>-T<NN>-TASK-####` directory, creates it, and populates it with the four required template files.

## Source Documents
- `docs/canonical/data_contracts.md` — Section 7, Section 8, Section 13.3
- `docs/canonical/architecture.md` — Section 6.2 (services), Section 8.2 (creation flow)
