# Grain Workspace Model

**Version:** 1.0
**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0191)

---

## 1. Purpose

This document specifies how Grain resolves the active workspace, how multiple workspaces coexist in a monorepo, how workspaces can be linked to each other, and how cross-workspace context and dependencies flow.

The model is backwards-compatible: a single-repo Grain setup with no workspace links continues to work exactly as before. Multi-repo and monorepo features activate only when workspace declarations are present.

---

## 2. Workspace Definition

A Grain workspace is any directory tree rooted at a directory containing `docs/runtime/PROJECT_RULES.md`. This is the existing Grain root-detection anchor and it does not change.

```
myproject/
  docs/
    runtime/
      PROJECT_RULES.md   ← workspace root marker
      docs_manifest.yaml
    canonical/
    working/
  tasks/
```

---

## 3. Workspace Resolution Order

When Grain is invoked from any directory, it resolves the active workspace as follows:

1. **Explicit flag** — `grain --workspace <path>` targets that workspace directly; no resolution is performed
2. **Environment variable** — `GRAIN_WORKSPACE=<path>` overrides all auto-detection; useful for CI or multi-terminal setups
3. **Nearest ancestor walk** — walk upward from CWD; use the first directory that contains `docs/runtime/PROJECT_RULES.md`
4. **Ambiguity** — if step 3 finds multiple candidate roots at the same depth (shouldn't happen in practice but possible if workspace links point inward), Grain exits with a structured error listing the candidates and their paths

The nearest workspace wins. In a monorepo, running `grain workflow next` from `products/grain/` operates on the Grain product workspace, not the root workspace, because `products/grain/docs/runtime/PROJECT_RULES.md` is closer.

### Resolution output
`grain workspace show` prints the resolved workspace path, name, and type. `--format json` for machine consumption.

---

## 4. Workspace Declaration

Each workspace may declare metadata about itself in `docs/runtime/workspace_manifest.yaml`. This file is optional — workspaces that don't declare it behave as standalone workspaces.

```yaml
# docs/runtime/workspace_manifest.yaml

workspace:
  name: grain                   # short identifier, used in cross-workspace references
  type: product                 # product | platform | company | standalone
  description: "Grain CLI workspace"

  # Optional: path to a parent context workspace whose canonical docs are available here
  parent: "../../"

  # Optional: sibling workspaces this workspace can reference
  siblings:
    - name: assay
      path: "../assay-sdk/"
      type: product
    - name: conclave
      path: "../../apps/conclave/"
      type: product
    - name: infra
      path: "../../Diwata-Infra/"
      type: platform
```

Workspace types:
- `product` — a product codebase with its own backlog and task lifecycle
- `platform` — shared infrastructure or tooling workspace (e.g., Diwata-Infra)
- `company` — org-level docs repo with no code (canonical specs, decisions, landscape)
- `standalone` — default; no declared relationships, no cross-workspace features

---

## 5. Workspace Linking — `grain context link`

`grain context link <path>` registers an external Grain workspace as a linked context source. Once linked, its canonical docs are accessible during context assembly as a named source without copying any files.

### Command interface

```
grain context link <path>           Register a workspace as a linked context source
grain context link --list           Show all currently linked workspaces
grain context link --remove <name>  Remove a registered link
```

### What linking does

1. Validates that `<path>` contains a Grain workspace (looks for `docs/runtime/PROJECT_RULES.md`)
2. Reads the workspace name from `workspace_manifest.yaml` (falls back to the directory basename)
3. Appends an entry to `docs/runtime/workspace_links.yaml`:

```yaml
# docs/runtime/workspace_links.yaml — managed by grain context link
links:
  - name: infra
    path: "../../Diwata-Infra/"
    type: platform
    linked_at: "2026-06-11"
  - name: assay
    path: "../assay-sdk/"
    type: product
    linked_at: "2026-06-11"
```

4. No files are copied. No symlinks are created. The link is a path reference only.

### What linking enables

When `grain task prepare` assembles context for a task, it can pull from linked workspaces if the task's `context_sources` field or the adapter profile references them:

```yaml
# In a task's context_sources block:
context_sources:
  - linked:infra/docs/canonical/architecture.md
  - linked:assay/docs/canonical/product_scope.md
```

The `linked:<workspace-name>/` prefix resolves through `workspace_links.yaml` to the actual path.

### Backwards compatibility

Workspaces without `workspace_links.yaml` are unaffected. Context assembly ignores the `linked:` prefix resolution step when no links file exists.

---

## 6. `grain workspace list`

Lists all Grain workspaces visible from the current workspace, combining:
- The current workspace
- Declared siblings from `workspace_manifest.yaml`
- Links from `workspace_links.yaml`
- Any parent workspace declared in `workspace_manifest.yaml`

```
$ grain workspace list
WORKSPACE       TYPE       PATH                              STATUS
grain           product    .                                 active
assay           product    ../assay-sdk/                     linked
infra           platform   ../../Diwata-Infra/               linked
diwata-labs     company    ../../                            parent
```

`--format json` returns the same as a structured array.

`--verify` checks that all declared paths exist and contain valid workspace markers; reports broken links.

---

## 7. Cross-Workspace Task Dependencies

A task packet may declare a dependency on another workspace's phase or task completing before this task can begin.

### Declaration format

In `task.md` metadata:

```markdown
## Metadata
- **ID:** TASK-0191
- **External-Dependencies:**
  - assay:P3-close          # assay workspace Phase 3 must be closed
  - infra:TASK-0042-done    # infra workspace TASK-0042 must be done
```

### Resolution

`grain workflow guard` checks external dependencies when `workspace_links.yaml` is present:
1. Resolves the workspace name to a path via `workspace_links.yaml`
2. Reads the dependency target's status from the sibling workspace's backlog or task packet
3. Reports `external_dependency_unmet` if the target is not in the required state
4. Reports `external_workspace_unreachable` if the path is broken or the workspace has no readable state

`grain workflow guard` does not block on external dependencies in strict mode unless `--check-external` is explicitly passed — external workspace state is informational by default, not a hard gate. This keeps local work unblocked even when sibling workspaces are mid-phase.

---

## 8. Monorepo Scenarios

### Scenario A: monorepo with multiple independent product workspaces

```
diwata-labs/
  products/
    grain/docs/runtime/PROJECT_RULES.md    ← workspace root
    assay/docs/runtime/PROJECT_RULES.md    ← workspace root
  apps/
    apex/docs/runtime/PROJECT_RULES.md     ← workspace root (if Grain-onboarded)
  docs/runtime/PROJECT_RULES.md           ← company-level workspace root
```

Running `grain workflow next` from `products/grain/src/` resolves to the `products/grain/` workspace (nearest ancestor). No ambiguity.

Running from `diwata-labs/` (the monorepo root) resolves to the company-level workspace — correct behavior for org-wide planning.

### Scenario B: product workspace with a linked platform workspace

`products/grain/` has a link to `../../Diwata-Infra/` declared in `workspace_links.yaml`. Tasks in the Grain workspace that need to reference Infra's architecture docs can use `linked:infra/docs/canonical/architecture.md` in their context sources.

The link does not merge the two backlogs. Each workspace's task lifecycle is fully independent.

### Scenario C: new workspace linking to an existing one

A developer working in a new product repo runs:
```
grain context link ../../Diwata-Infra/
```

This registers Diwata-Infra as a linked context source. No changes to Diwata-Infra are required.

---

## 9. Impact on Existing Grain Commands

| Command | Change |
|---------|--------|
| `grain workflow next` | Adds workspace resolution step; no output change for single-workspace use |
| `grain task prepare` | Resolves `linked:` prefixes in context sources if links file present |
| `grain workflow guard` | Checks external dependencies if `--check-external` flag is passed |
| `grain init` | Seeds `workspace_manifest.yaml` stub if `--type` flag is given |
| `grain upgrade` | Upgrades `workspace_manifest.yaml` schema version if needed |

All changes are additive. Existing single-workspace repos see no behavioral difference.

---

## 10. What This Model Does Not Do

- **Merge backlogs** — each workspace keeps its own independent backlog and task lifecycle
- **Synchronize task status across workspaces** — external dependency checks are read-only and advisory
- **Replace a monorepo management tool** — this model handles Grain's context and state concerns only; build systems, CI, and dependency management remain outside Grain's scope
- **Network-aware workspace discovery** — workspaces are identified by local filesystem paths; remote workspace URLs are not supported
