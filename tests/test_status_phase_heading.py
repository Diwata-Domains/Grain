# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Backlog phase headings parse in both the numbered and unnumbered forms.

The canonical backlog form is `## Phase N — Title`. A numbered variant
(`## N. Phase N — Title`) appears in older scaffolds. Every parser must accept
both, or it silently reports zero tasks for the active phase.
"""

from pathlib import Path

from grain.cli.status import _count_tasks

UNNUMBERED = """# Backlog

## Phase 36 — Release Readiness

### P36-T01 — Ship it
- **Status:** done

### P36-T02 — Fix it
- **Status:** ready

### P36-T03 — Block it
- **Status:** blocked
"""

NUMBERED = UNNUMBERED.replace("## Phase 36 —", "## 36. Phase 36 —")

OTHER_PHASE = """# Backlog

## Phase 35 — Deferred

### P35-T01 — Not counted
- **Status:** done

## Phase 36 — Release Readiness

### P36-T01 — Counted
- **Status:** done
"""


def _backlog(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "docs" / "working" / "backlog.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return tmp_path


def test_count_tasks_reads_unnumbered_phase_heading(tmp_path):
    root = _backlog(tmp_path, UNNUMBERED)
    counts = _count_tasks(root, "36")

    assert counts["total"] == 3
    assert counts["done"] == 1
    assert counts["ready"] == 1
    assert counts["blocked"] == 1


def test_count_tasks_reads_numbered_phase_heading(tmp_path):
    root = _backlog(tmp_path, NUMBERED)
    counts = _count_tasks(root, "36")

    assert counts["total"] == 3
    assert counts["done"] == 1


def test_count_tasks_scopes_to_the_active_phase(tmp_path):
    root = _backlog(tmp_path, OTHER_PHASE)
    counts = _count_tasks(root, "36")

    assert counts["total"] == 1
    assert counts["done"] == 1
