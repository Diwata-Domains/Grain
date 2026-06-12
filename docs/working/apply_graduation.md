# Apply Graduation Criteria

**Status:** Working decision document — v0.4.0 planning (Phase 30, TASK-0193)

---

## 1. Purpose

This document defines the conditions under which a writable artifact workflow graduates from `propose`/`export` mode to safe in-place `apply`. It determines which artifact types can have `apply` enabled in v0.4.0 execution phases.

`propose` is always safe because it creates a new file and leaves the original untouched. `apply` mutates the original in place. Graduation requires that Grain's validation coverage is strong enough to catch malformed changes deterministically — and that a rollback path exists if something goes wrong.

---

## 2. Universal Graduation Requirements

All artifact types must satisfy every requirement below before `apply` is enabled for them. These are not per-type — they are absolute prerequisites.

| # | Requirement | Rationale |
|---|-------------|-----------|
| R1 | All required validators return zero failures | Partial validation = unknown risk; `apply` bars unknown risk |
| R2 | At least one validator emits a non-empty, human-readable change summary | Operator must be able to read what changed before confirming apply |
| R3 | No unacknowledged residual risk flags | Risk flags must be empty or explicitly acknowledged with `--accept-risk "<note>"` |
| R4 | Original artifact is backed up before apply executes | Enables recovery without relying on git history |
| R5 | A review bundle is generated and written to the task packet before close | Same review evidence requirement as `propose` mode |
| R6 | Apply requires explicit operator confirmation (`--confirm` flag) | No silent apply; always a human gate before in-place mutation |

Validators marked `advisory_only` in the adapter profile downgrade failures to warnings. They do not block graduation or apply.

---

## 3. Rollback Mechanism

Before any `apply` runs, Grain:
1. Copies the original artifact to `.grain/backups/<task_id>/<artifact_basename>.<timestamp>.bak`
2. Writes a backup manifest entry to the task packet noting the original path and backup path
3. Only then executes the in-place write

`grain task restore --backup <task_id>` reads the backup manifest and restores the original. This does not require git — it works in any workspace regardless of version control state.

Backup files are not committed to version control (`.grain/backups/` is in Grain's default `.gitignore`). They are ephemeral until the task closes; at close they can be pruned by `grain task close --prune-backups`.

---

## 4. Per-Type Assessment

### 4.1 `.docx` (Word documents)

**Available validators:**
- Structure: heading hierarchy validation, table row/column count consistency, paragraph ordering
- Reference: internal cross-reference link validity
- No policy validators for content correctness (content is semantic, not structural)

**Change summary capability:** Yes — Grain's `DocsExtractor` provides section-level diff (which headings changed, which paragraphs were added/removed). A non-empty change summary is reliably producible.

**Rollback:** Original copied to `.grain/backups/` before apply.

**Remaining gaps:**
- No semantic content validators (Grain cannot verify that the new content is factually correct or matches the intent)
- Tracked-changes metadata (`.docx` change tracking) is not parsed or preserved

**Graduation verdict for v0.4.0: GRADUATES**

Conditions for `.docx` apply:
- All structure validators pass
- A section-level change summary is present (changed heading list + paragraph delta)
- No unacknowledged residual risk flags
- Original backed up before apply
- `--confirm` flag required

Exclusions: changes that delete or rename more than 30% of top-level headings are automatically downgraded to `propose` mode with a warning — this level of structural change warrants human review before in-place mutation.

---

### 4.2 Spreadsheets (`.xlsx` / `.csv`)

**Available validators:**
- Structure: sheet name preservation, column header presence, row count sanity bounds
- Reference: formula cell reference validity (referenced cells/named ranges must exist after change)
- No policy validators for numeric/business logic correctness

**Change summary capability:** Yes for data cells — Grain can report which sheets, columns, and row ranges changed. Formula changes are reported as "formula updated" without evaluating impact.

**Key risk:** Formula cascades. If a changed cell is referenced by a formula in another cell, the formula's output changes silently. Grain's validators check that formula references are syntactically valid but cannot evaluate all downstream cascading effects.

**Rollback:** Original copied to `.grain/backups/` before apply.

**Graduation verdict for v0.4.0: CONDITIONAL GRADUATION**

`.csv` files: Graduates unconditionally (no formula risk — plain data only).

`.xlsx` — data-only apply:
- Applies only if no formula columns are present in the changed range
- If a formula column is present in the changed range, Grain automatically downgrades to `propose` mode with a warning: `"Formula columns detected in change range — apply downgraded to propose"`
- Formula-free sheets graduate; formula-containing sheets remain propose-only

`.xlsx` — formula range changes: remain in `propose` mode in v0.4.0. Graduation criteria for formula-touching changes are deferred to v0.5.0 or a dedicated formula-safety phase.

---

### 4.3 Obsidian Vault Notes

**Available validators (when `obsidian_adapter` is active):**
- Wiki-link validator: all `[[linked-note]]` references in the changed note must resolve to existing notes
- Frontmatter schema validator: required frontmatter fields (as declared in vault configuration) must be present and correctly typed
- Tag consistency: tags added in the change must be consistent with the existing vault tag taxonomy (warning-only)

**Change summary capability:** Yes for structural changes — added/removed links, frontmatter field changes, added/removed headings.

**Remaining gaps:**
- Plugin-specific frontmatter fields (Obsidian plugins like Dataview, Tasks, etc.) may not be fully understood by Grain's validators
- Canvas files (`.canvas`) are not covered — vault note apply does not extend to canvases

**Graduation verdict for v0.4.0: GRADUATED for scoped changes**

Obsidian vault notes graduate for:
- Wiki-link repair changes (the primary `fix-vault-links` recipe target)
- Frontmatter field updates where all required fields are declared in the adapter config

Obsidian vault notes remain in `propose` mode for:
- Full note rewrites
- Changes involving plugin-specific frontmatter fields not listed in the adapter config
- Canvas files

---

### 4.4 PDF

**Verdict: NON-GOAL — remains read-only**

Grain treats PDFs as read-only context sources. Writing to PDFs requires parsing and regenerating the document structure, which is outside Grain's adapter scope. PDF write support is not planned for v0.4.0 or the next release.

---

## 5. Summary Table

| Artifact Type | v0.4.0 Status | Conditions |
|---------------|--------------|------------|
| `.docx` | **Graduates** | All structure validators pass; change summary present; <30% heading deletion; backup; `--confirm` |
| `.csv` | **Graduates** | Structure validators pass; change summary present; backup; `--confirm` |
| `.xlsx` (data-only) | **Conditional** | Graduates only when no formula columns in changed range |
| `.xlsx` (formula range) | Remains `propose` | Deferred to v0.5.0 |
| Obsidian notes (link/frontmatter) | **Conditional** | Wiki-link and declared frontmatter changes only; full rewrites remain `propose` |
| PDF | **Non-goal** | Read-only in perpetuity |

---

## 6. Implementation Notes for Execution Phases

Phase 35 implements this spec. Key work items:
1. Add `--mode apply` flag to office write commands that checks all R1–R6 requirements before proceeding
2. Implement `.grain/backups/` path and backup manifest
3. Implement `grain task restore --backup <task_id>` command
4. Wire the heading-deletion threshold check for `.docx`
5. Wire formula-column detection for `.xlsx`
6. Add `--accept-risk "<note>"` flag to allow operators to acknowledge residual risk flags
