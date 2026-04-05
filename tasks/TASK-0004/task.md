# Task: Add repository root resolution

## Metadata
- **ID:** TASK-0004
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0001 (source structure must exist)

## Objective
Implement logic to resolve the repository root from the current working directory or an explicit `--repo <path>` option. All CLI commands that operate on repository files must use this resolver. The resolved root must be inspectable and passed explicitly — not stored as hidden state.

## Why This Task Exists
Every CLI command in `cli_spec.md` operates relative to a repository root. Without a shared resolution mechanism, each command would independently invent its own path logic. `cli_spec.md` Section 4.2 defines path resolution as a global CLI rule. `architecture.md` Section 4.1 requires this logic to live outside the CLI layer.

## Scope
- Implement a repository root resolver
- Support auto-detection from current working directory (walk upward looking for a known marker)
- Support explicit override via `--repo <path>`
- Expose the resolved root for use by CLI commands
- Define what constitutes the repository root marker for v1

## Constraints
- Must align with `cli_spec.md` Section 4.2
- Resolver must not live in `cli/` — belongs in `adapters/` (filesystem adapter per `architecture.md` Section 6.4)
- Must not hardcode absolute paths
- Must support relative path arguments (`cli_spec.md` Section 4.2)
- Must not introduce database or background-service dependencies
- Resolution failure must produce a clear error, not a silent fallback

## Escalation Conditions
- Ambiguity about which file or directory serves as the repository root marker
- Root marker choice conflicts with existing repo structure
