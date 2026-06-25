# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for the surface-only suggestion in `grain workflow next` (P32-T05)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo: Path) -> None:
    # Phase 8 is below the phase-close enforcement floor (grandfathered), so the
    # workflow does not stop on previous_phase_not_closed.
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 8 — Build\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def _run(repo: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(repo)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += ["workflow", "next", *args]
    return runner.invoke(main, cmd)


def test_suggestion_surfaced_when_no_next_task(tmp_path):
    """An empty active phase (phase_has_no_tasks) surfaces a new-task suggestion from a blocking OQ."""
    _base_repo(tmp_path)
    # Active phase has no tasks → stop_reason phase_has_no_tasks.
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n## 1. Phase 8 — Build\n\n",
    )
    # A blocking open question gives the engine a new-task signal to surface.
    _write(
        tmp_path / "docs" / "working" / "open_questions.md",
        "# Open Questions\n\n### Decide architecture?\n- **ID:** OQ-9\n- **Status:** blocking\n",
    )

    result = _run(tmp_path)
    assert result.exit_code == 0, result.output
    assert "stop_reason       phase_has_no_tasks" in result.output
    assert "suggestion" in result.output
    assert "new-task" in result.output
    # Surface-only: nothing persisted.
    proposals_dir = tmp_path / "docs" / "working" / "proposals"
    assert not proposals_dir.exists() or list(proposals_dir.glob("SUG-*.md")) == []


def test_suggestion_surfaced_pickup_when_phase_has_no_tasks(tmp_path):
    """phase_has_no_tasks → surface a pick-up from the next-blocked phase."""
    _base_repo(tmp_path)
    # Active phase 30 has no tasks; phase 31 (next-blocked) has a ready task.
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n"
        "## 1. Phase 8 — Build\n\n"
        "## 2. Phase 9 — Next\n\n"
        "### P9-T01 — Ready in next phase\n- **Status:** ready\n",
    )
    result = _run(tmp_path)
    assert result.exit_code == 0, result.output
    assert "stop_reason       phase_has_no_tasks" in result.output
    assert "suggestion" in result.output
    assert "pick-up" in result.output
    assert "P9-T01" in result.output


def test_no_suggestion_when_task_ready(tmp_path):
    """A single ready task in the active phase → packet_required, no suggestion block."""
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n## 1. Phase 8 — Build\n\n"
        "### P8-T01 — Ready\n- **Status:** ready\n",
    )
    result = _run(tmp_path)
    assert result.exit_code == 0, result.output
    assert "stop_reason       packet_required" in result.output
    # No suggestion block for a normal ready-task state.
    assert "  suggestion" not in result.output


def test_suggestion_json_field_present(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n## 1. Phase 8 — Build\n\n",
    )
    _write(
        tmp_path / "docs" / "working" / "open_questions.md",
        "# Open Questions\n\n### Decide architecture?\n- **ID:** OQ-9\n- **Status:** blocking\n",
    )
    result = _run(tmp_path, fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "suggestion" in data
    assert data["suggestion"] is not None
    assert data["suggestion"]["kind"] == "new-task"
    assert data["suggestion"]["signal_ref"] == "OQ-9"


def test_suggestion_json_null_when_task_ready(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n## 1. Phase 8 — Build\n\n"
        "### P8-T01 — Ready\n- **Status:** ready\n",
    )
    result = _run(tmp_path, fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["suggestion"] is None


def test_suggestion_is_surface_only_no_writes(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "# Backlog\n\n"
        "## 1. Phase 8 — Build\n\n"
        "## 2. Phase 9 — Next\n\n"
        "### P9-T01 — Ready in next phase\n- **Status:** ready\n",
    )
    backlog_before = (tmp_path / "docs/working/backlog.md").read_text()
    current_before = (tmp_path / "docs/working/current_task.md").read_text()

    _run(tmp_path)

    assert (tmp_path / "docs/working/backlog.md").read_text() == backlog_before
    assert (tmp_path / "docs/working/current_task.md").read_text() == current_before
    proposals_dir = tmp_path / "docs/working/proposals"
    assert not proposals_dir.exists() or list(proposals_dir.glob("SUG-*.md")) == []
