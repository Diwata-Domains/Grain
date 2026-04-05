# Task: Implement Packet Context Source Discovery

## Metadata
- **ID:** TASK-0032
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T01
- **Packet Path:** tasks/P4-T01-TASK-0032/
- **Dependencies:** none (Phase 3 done)

## Objective
Implement the packet context source discovery layer: a domain model representing packet-local files and their presence status, a pure domain function to discover those files from a packet directory, and a service function that locates a packet by ID and returns a `PacketSourceSet`. This is the foundation for all Phase 4 context assembly work.

## Why This Task Exists
Phase 4 requires context assembly before exporting packet context to external tools. Before canonical doc selection (P4-T02) or bundle assembly (P4-T04), the system must be able to enumerate what packet-local files exist for a given task. This task provides that primitive.

## Scope
- `PacketFile` dataclass: name, path, present
- `PacketSourceSet` dataclass: task_id, packet_dir, files list with helpers
- `PACKET_FILENAMES` constant (6 filenames, consistent with task_service)
- `discover_packet_files(packet_dir)` pure domain function
- `find_packet_dir` moved to `domain/packets.py` as a public function (removes duplication with task_service private function)
- `context_service.discover_packet_sources(root, task_id)` service function
- Tests in `tests/test_context_sources.py`

## Constraints
- Context domain model lives in `domain/context.py` (architecture.md §6.3)
- Service lives in `services/context_service.py` (architecture.md §6.2)
- No CLI in this task — that is P4-T05
- No canonical doc selection — that is P4-T02
- Filesystem-first; no database dependency

## Escalation Conditions
- If `PacketSourceSet` design conflicts with `ContextBundle` (P4-T04) scope — stop and record
