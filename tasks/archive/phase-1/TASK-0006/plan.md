# Plan: TASK-0006

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical task — creating placeholder files and a simple loader function. No design ambiguity. `reviewer_model` should verify placeholder content is generic (no project-specific logic) and loader placement matches `architecture.md` Section 6.6.

## Steps

1. Add placeholder template files at repo root:
   - `templates/docs/canonical_doc.md` — generic placeholder for a canonical doc
   - `templates/tasks/task_packet.md` — generic task packet template (aligns with existing `templates/phase_packet.md` shape)
   - `templates/prompts/prompt.md` — generic prompt placeholder

2. Implement `src/ai_build_toolkit/templates/loader.py`:
   - `get_template(name: str, repo_root: Path) -> str` — reads and returns template content from `<repo_root>/templates/<name>`
   - Raises `FileNotFoundError` with a clear message if the template does not exist

3. Write tests in `tests/test_template_loader.py`:
   - Known template is loaded and returns content
   - Unknown template raises `FileNotFoundError`

## Patch Strategy
- New files: `templates/docs/canonical_doc.md`, `templates/tasks/task_packet.md`, `templates/prompts/prompt.md`
- New file: `src/ai_build_toolkit/templates/loader.py`
- New file: `tests/test_template_loader.py`
- No changes to other modules
