# Task: Spec TUI extension for v0.4.0 command surface

## Metadata
- **ID:** TASK-0202
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T13
- **Packet Path:** tasks/P30-T13-TASK-0202/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Spec the extension of Grain's v0.3.0 TUI (Python + Textual) to surface the new v0.4.0 commands for direct terminal users. The TUI must remain a thin shell over the existing CLI — it calls Grain commands and reads their `--format json` output. No business logic lives in the TUI layer. The spec must define exactly which views and actions are in v0.4.0 scope vs. deferred.

## Why This Task Exists
v0.3.0 shipped the first TUI slice: workflow dashboard, task/phase view, backlog list, packet inspector, prompt preview, context bundle inspector. v0.4.0 is adding 6 new commands (`grain suggest`, `grain docs audit`, `grain archive`, `grain doctor`, `grain recipe`, `grain status`). Without TUI extension, direct terminal users must drop to the CLI for all new functionality — breaking the workflow they expected the TUI to provide.

The TUI also serves as a discoverability surface: users who don't know what commands are available see them as menu items and panels, not as man pages they have to read first.

## Scope

### Part 1 — TUI architecture constraint

The TUI is a presentation layer only. Every TUI action maps to a Grain CLI call. The TUI:
- Calls `grain <command> --format json` and renders the structured output
- Never reads `docs/working/` files directly
- Never calls Grain Python APIs directly — only the CLI

This constraint ensures the TUI always behaves identically to the CLI and that TUI tests verify the CLI contract, not a separate code path.

### Part 2 — New panels for v0.4.0 commands

**Suggestions panel** (`grain suggest` surface):
- Lists active proposals from `docs/working/proposals/` via `grain suggest list --format json`
- Each suggestion shown with type badge (PICK-UP / NEW-TASK), signal summary, and Accept / Dismiss action buttons
- Accept button calls `grain suggest accept <id>` and refreshes the workflow state panel
- Dismiss button calls `grain suggest dismiss <id>` and removes the item from the panel
- Panel is empty when no proposals are pending; shows a "Run grain suggest to generate suggestions" hint

**Workspace health panel** (`grain docs audit` surface):
- Shows a condensed audit summary via `grain docs audit --format json`
- Groups findings by severity: errors first, then warnings
- Each finding shows doc name, check ID, message, remediation hint
- Refreshes automatically when the user navigates to the panel (not a live watch — one call per navigation)

**Archive panel** (`grain archive` surface):
- Lists archives via `grain archive list --format json`
- Sections: Phases, Milestones, Snapshots
- "Create snapshot" button calls `grain archive snapshot` with an optional label prompt
- "Create milestone archive" button appears only when a milestone-archive suggestion is pending

**Doctor panel** (`grain doctor` surface):
- Shows `grain doctor --format json` output in a structured health card
- Highlights drift warnings in red; ok checks in green
- "Reinstall" hint shown when drift is detected (links to the reinstall command — does not run it)

**Recipe panel** (`grain recipe` surface):
- Lists available recipes via `grain recipe list --format json` with category filters
- "Run" button on each recipe calls `grain recipe run <name>` — opens a parameter form for required params
- Parameter form for `grain recipe run` is the one interactive TUI flow that doesn't map to a single CLI call: it collects params in the TUI, then calls `grain recipe run <name> --param k=v ...`

**Status bar extension:**
- The persistent status bar (always visible) shows current task, phase, and `grain status` summary
- Refreshes on every panel navigation

### Part 3 — v0.4.0 TUI scope boundaries

**In scope for v0.4.0:**
- All 5 new panels above
- Status bar showing `grain status` summary
- Keyboard shortcuts for the most common actions: `s` for suggest, `a` for audit, `r` for recipe list

**Explicitly deferred (not v0.4.0):**
- Embedded agent terminal in the TUI
- Multi-workspace navigation (one workspace per TUI session)
- Live file watching / auto-refresh
- Editing packet files or canonical docs within the TUI
- Diff/review UI for `grain upgrade --diff` within the TUI

### Part 4 — Keyboard navigation spec

All new panels must be keyboard-navigable (Textual's built-in key bindings). Minimum:
- Arrow keys / `j`/`k` to navigate lists
- `Enter` to select / activate
- `Esc` to close a panel or cancel an action
- `?` for in-panel help showing available actions

### Part 5 — TUI extension spec deliverable

The spec document should include:
- Panel inventory: which panels exist after v0.4.0, what CLI commands they call, what JSON fields they render
- Keyboard shortcut map
- Action → CLI command mapping table
- Deferred feature list with rationale

## Deliverable
`docs/working/tui_extension_spec.md` — full TUI extension spec.

## Constraints
- TUI never calls Grain Python APIs directly — CLI only
- No new business logic in the TUI layer
- All new panels must degrade gracefully when the underlying command fails (show error state, not crash)
- TUI must remain installable as a dependency-optional extra (`grain[tui]`) — base `grain` install has no TUI dependency
