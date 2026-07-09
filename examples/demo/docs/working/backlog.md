# Backlog

## 1. Purpose

Execution inventory for Northwind Internal. Grouped by phase.

Status values: `draft` | `ready` | `in_progress` | `blocked` | `review` | `done`

NOTE: This file must use heading+bullet format (not tables) for `grain workflow next` to parse it correctly.

---

## 2. Phase 1 — Q3 Readiness

> **Status:** not_started

### P1-T01 — Add /health endpoint to the status service
- **Status:** draft
- **Description:** `services/api/app.py` has no liveness check. Add a `health()` returning `{"status": "ok"}`, plus a test.

### P1-T02 — Revise the Q3 budget headcount
- **Status:** draft
- **Description:** `company/q3-budget.xlsx` still carries the Q2 engineering headcount.

### P1-T03 — Refresh the handbook's remote-work section
- **Status:** draft
- **Description:** `company/handbook.docx` predates the current remote-work policy.
