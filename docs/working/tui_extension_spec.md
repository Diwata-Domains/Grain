# Grain TUI Extension Spec — v0.4.0

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0202)
**Implementation phase:** Phase 31 (DX Hardening) — TUI panels for new commands

---

## 1. Architecture Constraint

The TUI is a presentation layer only. Every TUI action maps to a Grain CLI call with `--format json`. The TUI:
- Never reads `docs/working/` files directly
- Never calls Grain Python APIs — CLI only
- Renders structured JSON output from CLI commands

This constraint ensures the TUI always behaves identically to the CLI and that tests can verify the CLI contract independently of the TUI.

TUI remains an optional install: `grain[tui]` extra. Base `grain` has no TUI dependency.

---

## 2. Existing TUI Surface (v0.3.0)

Already shipped in v0.3.0:
- Workflow dashboard
- Current task and phase view
- Backlog-by-phase list
- Packet artifact inspector
- Prompt preview
- Context bundle inspector

These panels are not modified in v0.4.0 except to add the status bar extension (§3.6).

---

## 3. New Panels for v0.4.0

### 3.1 Suggestions Panel

CLI backing: `grain suggest list --format json`, `grain suggest accept <id>`, `grain suggest dismiss <id>`

**Layout:**
- Header: "Suggestions" + count badge
- List of proposal cards, each showing:
  - Type badge: `PICK-UP` or `NEW-TASK` (color-coded)
  - Signal summary (one line)
  - Accept button → calls `grain suggest accept <id>`; on success, refreshes workflow dashboard
  - Dismiss button → calls `grain suggest dismiss <id>`; removes card from list
- Empty state: "No pending suggestions. Run grain suggest to generate." with a `[Run]` button that calls `grain suggest`

**Keyboard:** `a` = accept highlighted item, `d` = dismiss highlighted item, `Enter` = show full detail

### 3.2 Workspace Health Panel

CLI backing: `grain docs audit --format json`

**Layout:**
- Header: "Workspace Health" + overall status badge (OK / WARNINGS / ERROR)
- Findings grouped by severity: errors first, then warnings
- Each finding: doc name | check_id | message | `→ remediation hint`
- Empty state: "No findings. Workspace docs are healthy." (green)
- Refresh button → re-runs `grain docs audit --format json`

**Keyboard:** `f` = apply auto-fix for highlighted finding (calls `grain docs audit --fix --no-confirm` for that check), `r` = refresh

### 3.3 Archive Panel

CLI backing: `grain archive list --format json`, `grain archive snapshot`, `grain archive milestone`

**Layout:**
- Sections: Phases | Milestones | Snapshots
- Each section: list of archive entries with date and type
- "Create Snapshot" button → prompts for optional label, calls `grain archive snapshot --label <label>`
- "Create Milestone Archive" button → visible only when a `milestone-archive` suggestion is pending; calls `grain archive milestone <version>`

**Keyboard:** `s` = create snapshot, `Enter` on item = `grain archive show <target>` inline view

### 3.4 Doctor Panel

CLI backing: `grain doctor --format json`

**Layout:**
- Health card showing all `grain doctor` check results
- Each check: symbol (✓ / ✗ / ⚠) + check name + value
- Drift warning shown in red with "Run: pip install -e ." hint (displayed, not executed)
- Refresh button → re-runs `grain doctor --format json`

No actions beyond refresh — the Doctor panel is read-only. Remediation commands are shown but not executed from the TUI.

### 3.5 Recipe Panel

CLI backing: `grain recipe list --format json`, `grain recipe run <name> --param k=v ...`

**Layout:**
- Category filter bar (All | docs | code | data | office | vault)
- List of recipes with: name, category badge, description, source (bundled/local)
- "Run" button on each recipe → opens parameter form

**Parameter form (the one interactive TUI flow that spans multiple CLI calls):**
1. TUI collects required parameter values from the operator via form fields
2. On submit, calls `grain recipe run <name> --param k1=v1 --param k2=v2 ...`
3. Shows the rendered prompt in a scrollable panel
4. Operator copies the prompt and runs it in their agent CLI (the TUI doesn't execute it)

**Keyboard:** `Enter` = open parameter form for highlighted recipe, `/` = search recipes

### 3.6 Status Bar Extension

The persistent status bar (always visible at the bottom of the TUI) is updated to show:

```
Phase 30 (in_progress) · TASK-0202 in_progress · ⚠ 1 doc health warning · grain 0.4.0 (editable)
```

The status bar reads from `.grain/last_workflow_state.json` and `.grain/last_docs_audit.json` (written by post-checkout hook) for fast rendering. Falls back to live `grain status --format json` if cached files are absent.

---

## 4. Keyboard Shortcut Map (Full)

| Key | Context | Action |
|-----|---------|--------|
| `s` | Global | Open Suggestions panel |
| `h` | Global | Open Workspace Health panel |
| `a` | Global | Open Archive panel |
| `d` | Global | Open Doctor panel |
| `r` | Global | Open Recipe panel |
| `w` | Global | Open Workflow dashboard (existing) |
| `t` | Global | Open Current Task view (existing) |
| `b` | Global | Open Backlog view (existing) |
| `?` | Any panel | Show panel help |
| `Esc` | Any panel | Close panel / cancel action |
| `Enter` | List item | Select / activate |
| `j` / `↓` | List | Move down |
| `k` / `↑` | List | Move up |
| `q` | Global | Quit TUI |

---

## 5. V0.4.0 TUI Scope vs. Deferred

**In v0.4.0:**
- Suggestions panel
- Workspace health panel
- Archive panel
- Doctor panel
- Recipe panel (with parameter form)
- Status bar extension

**Deferred (not v0.4.0):**
- Embedded agent terminal in the TUI
- Multi-workspace navigation (one workspace per session)
- Live file watching / auto-refresh (manual refresh only)
- Editing packet files or canonical docs within the TUI
- Diff/review UI for `grain upgrade --diff`
- `grain workflow guard` violations panel
- TUI-native packet creation flow (use `grain task create` from terminal)

---

## 6. Panel Action → CLI Command Map

| Panel | Action | CLI Command |
|-------|--------|-------------|
| Suggestions | Accept | `grain suggest accept <id>` |
| Suggestions | Dismiss | `grain suggest dismiss <id>` |
| Suggestions | Run suggest | `grain suggest --format json` |
| Health | Refresh | `grain docs audit --format json` |
| Health | Auto-fix | `grain docs audit --fix --no-confirm --check <id>` |
| Archive | Create snapshot | `grain archive snapshot --label <label>` |
| Archive | Create milestone | `grain archive milestone <version>` |
| Archive | Show archive | `grain archive show <target>` |
| Doctor | Refresh | `grain doctor --format json` |
| Recipe | List | `grain recipe list --format json` |
| Recipe | Run | `grain recipe run <name> --param k=v ...` |
| Status bar | State | Reads `.grain/last_workflow_state.json` or `grain status --format json` |
