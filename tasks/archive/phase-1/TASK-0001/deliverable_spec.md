# Deliverable Spec: TASK-0001

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/` exists with all six module subdirectories matching `architecture.md` Section 6:
   - `cli/`
   - `services/`
   - `domain/`
   - `adapters/`
   - `validators/`
   - `templates/`
2. Each module directory contains at minimum an `__init__.py`
3. `import ai_build_toolkit` succeeds from project root
4. Each submodule import succeeds: `cli`, `services`, `domain`, `adapters`, `validators`, `templates`
5. `pyproject.toml` registers the package correctly with a `src` layout
6. No implementation logic beyond initialization stubs is present
7. One import test exists and passes

## Out of Scope
- Any CLI wiring or command logic
- Any service, domain, adapter, or validator implementation
- Template content beyond directory existence
- Any behavior beyond importable package structure
