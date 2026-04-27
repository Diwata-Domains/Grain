# Deliverable Spec: TASK-0006

## Definition of Done

This task is complete when all of the following are true:

1. Placeholder template files exist at:
   - `templates/docs/canonical_doc.md`
   - `templates/tasks/task_packet.md`
   - `templates/prompts/prompt.md`
2. `src/ai_build_toolkit/templates/loader.py` exists with `get_template(name, repo_root)`
3. `get_template()` returns file content for a known template path
4. `get_template()` raises `FileNotFoundError` with a clear message for an unknown template
5. Template loader lives in `src/ai_build_toolkit/templates/`, not in `cli/` or `services/`
6. Placeholder content is generic — no project-specific logic
7. Tests cover known and unknown template resolution — all passing

## Out of Scope
- Template rendering or variable substitution (v1 uses plain markdown)
- Manifest-driven template discovery (Phase 2+)
- Packet-specific template population (P3-T02)
