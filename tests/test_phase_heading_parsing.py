"""Regression: backlog phase headings use '## Phase N —' (no leading 'N.').

The phase/backlog parsers previously required a leading list number
('## 32. Phase 32 —'), so they silently found no tasks for the real backlog
format '## Phase 32 —', which blocked `grain phase close`. These tests pin the
real format (and keep the legacy numbered form working for back-compat).
"""
from grain.services.workflow_service import _read_phase_backlog_tasks

_REAL = """# Backlog

## Phase 32 — v0.4.0 Proactive Assistance

### P32-T01 — First task
- **Status:** done

### P32-T02 — Second task
- **Status:** done

## Backlog Maintenance Rules
"""

_LEGACY = """# Backlog

## 32. Phase 32 — v0.4.0 Proactive Assistance

### P32-T01 — First task
- **Status:** done

## Backlog Maintenance Rules
"""


def _write(tmp_path, text):
    p = tmp_path / "backlog.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_real_heading_format_finds_tasks(tmp_path):
    tasks = _read_phase_backlog_tasks(_write(tmp_path, _REAL), "32")
    assert [t.task_ref for t in tasks] == ["P32-T01", "P32-T02"]
    assert all(t.status == "done" for t in tasks)


def test_legacy_numbered_heading_still_supported(tmp_path):
    tasks = _read_phase_backlog_tasks(_write(tmp_path, _LEGACY), "32")
    assert [t.task_ref for t in tasks] == ["P32-T01"]


def test_unrelated_phase_returns_empty(tmp_path):
    assert _read_phase_backlog_tasks(_write(tmp_path, _REAL), "31") == []
