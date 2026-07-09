# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Machine-readable reporting fidelity for upgrade and phase-close (P38-T03).

Regression tests for four bugs where Grain's reported state disagreed with what
it actually did on disk:

1. ``--add-missing`` wrote seeded files but reported ``Added: (none)``.
2. A file skipped because the user customized it was counted as "out of date"
   forever by the staleness hint.
3. The staleness hint printed to stderr even under ``--format json``.
4. ``phase close --dry-run`` guard paths reported ``dry_run: false``.
"""

from __future__ import annotations

from pathlib import Path

from grain.cli import _maybe_warn_if_upgrade_needed
from grain.services.phase_close_service import close_phase
from grain.services.upgrade_service import upgrade_repo

_MANIFEST_WARN = "grain:\n  upgrade_check: warn\n  default_format: text\n"


def _write_warn_manifest(root: Path) -> None:
    p = root / "docs" / "runtime" / "docs_manifest.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_MANIFEST_WARN, encoding="utf-8")


# --- Bug 1: --add-missing must report seeded files as added ---

def test_add_missing_reports_seeded_files_as_added(tmp_path: Path):
    # roadmap.md is a seed-only file (not in _UPGRADE_TARGETS/_ADDITIVE_TARGETS),
    # so it is written by _scan_absent_seeded_files rather than the main loops.
    result = upgrade_repo(tmp_path, add_missing=True)

    assert (tmp_path / "docs" / "working" / "roadmap.md").exists()
    assert "docs/working/roadmap.md" in result.added


def test_add_missing_dry_run_does_not_falsely_report_added(tmp_path: Path):
    # Dry-run must not claim it added a file it never wrote.
    result = upgrade_repo(tmp_path, add_missing=True, dry_run=True)

    assert not (tmp_path / "docs" / "working" / "roadmap.md").exists()
    assert "docs/working/roadmap.md" not in result.added
    assert "docs/working/roadmap.md" in result.absent


# --- Bug 2: customized-and-skipped files are not "out of date" ---

def test_customized_skip_not_counted_as_stale(tmp_path: Path, capsys):
    upgrade_repo(tmp_path)  # seed everything at the current bundled version
    _write_warn_manifest(tmp_path)

    prompt = tmp_path / "prompts" / "task.execute.md"
    prompt.write_text(
        prompt.read_text(encoding="utf-8") + "\nLOCAL CUSTOMIZATION\n",
        encoding="utf-8",
    )

    # Sanity: the file is stale and flagged as customized (thus skipped).
    dry = upgrade_repo(tmp_path, dry_run=True)
    assert "prompts/task.execute.md" in dry.updated
    assert "prompts/task.execute.md" in dry.skipped_customized

    _maybe_warn_if_upgrade_needed(tmp_path, "status", "text")
    assert "out of date" not in capsys.readouterr().err


# --- Bug 3: no free-text hint under --format json ---

def test_json_format_suppresses_stale_hint(tmp_path: Path, capsys):
    upgrade_repo(tmp_path)
    _write_warn_manifest(tmp_path)

    # Make a genuinely stale, non-customized file (bundled has extra trailing lines).
    review = tmp_path / "prompts" / "task.review.md"
    lines = review.read_text(encoding="utf-8").splitlines(keepends=True)
    review.write_text("".join(lines[:-2]), encoding="utf-8")

    stale = upgrade_repo(tmp_path, dry_run=True)
    assert "prompts/task.review.md" in stale.updated
    assert "prompts/task.review.md" not in stale.skipped_customized

    # json: hint suppressed even though a file is genuinely stale.
    _maybe_warn_if_upgrade_needed(tmp_path, "status", "json")
    assert "out of date" not in capsys.readouterr().err

    # text: hint still surfaces.
    _maybe_warn_if_upgrade_needed(tmp_path, "status", "text")
    assert "out of date" in capsys.readouterr().err


# --- Bug 4: phase close guard paths preserve dry_run ---

def _seed_phase_repo(root: Path, phase: str = "1") -> None:
    working = root / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)
    (working / "current_focus.md").write_text(
        f"## Current Phase\nPhase {phase} — Test Phase — Not Started\n",
        encoding="utf-8",
    )
    (working / "current_task.md").write_text(
        "Task ID: none\nTask Path: none\nStatus: unset\n", encoding="utf-8"
    )
    (working / "backlog.md").write_text(
        f"## 1. Phase {phase} — Test Phase\n\n"
        f"### P{phase}-T01 — A task\n- **Status:** done\n\n",
        encoding="utf-8",
    )


def test_phase_close_dry_run_preserved_on_mismatch_guard(tmp_path: Path):
    _seed_phase_repo(tmp_path, phase="1")

    result = close_phase(tmp_path, dry_run=True, phase_override="999")

    assert result.ok is False
    assert result.dry_run is True


def test_phase_close_dry_run_preserved_on_missing_doc_guard(tmp_path: Path):
    # No docs at all — hits the earliest guard return.
    result = close_phase(tmp_path, dry_run=True)

    assert result.ok is False
    assert result.dry_run is True
