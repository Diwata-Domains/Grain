# Deliverable Spec: TASK-0004

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/adapters/filesystem.py` exists with `find_repo_root()` and `resolve_repo_root()`
2. `find_repo_root()` walks upward from a given path and returns the repo root when the marker is found
3. `find_repo_root()` raises a clear, descriptive error when no marker is found
4. `resolve_repo_root()` uses an explicit path when provided, otherwise delegates to `find_repo_root(Path.cwd())`
5. `--repo <path>` is available as a global option on the `abt` command
6. Resolver lives in `adapters/`, not in `cli/` or `services/`
7. No hardcoded absolute paths
8. Unit tests cover: auto-detection, explicit override, and missing-marker error case — all passing

## Out of Scope
- Passing the resolved root into command handlers (commands will invoke the resolver themselves — that is part of each command's implementation)
- Any manifest, packet, or document logic
- Any service or domain logic
