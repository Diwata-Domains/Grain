# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Legacy-packet validation escape hatch (P38-T09).

Covers two paths for a partially-migrated legacy packet that has task.md +
context.md but is missing plan.md / deliverable_spec.md:

1. An explicit ``- **Mode:** simple`` declaration in task.md exempts the packet
   from the planning-file requirement regardless of which planning files exist.
2. ``grain task backfill`` seeds the missing planning files from templates so a
   legacy packet can be migrated forward, refusing to overwrite existing files.
"""

from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.validators.packet_validator import validate_packet_files

_SIMPLE_TASK_MD = """\
# Task: Legacy

## Metadata
- **ID:** TASK-0001
- **Status:** draft
- **Mode:** simple
- **Phase:** Phase 3 — Legacy
"""

_PLAIN_TASK_MD = """\
# Task: Legacy

## Metadata
- **ID:** TASK-0001
- **Status:** draft
- **Phase:** Phase 3 — Legacy
"""


def _partial_legacy_packet(packet_dir: Path, task_md: str) -> None:
    """Write task.md + context.md only (missing plan.md, deliverable_spec.md)."""
    packet_dir.mkdir(parents=True, exist_ok=True)
    (packet_dir / "task.md").write_text(task_md, encoding="utf-8")
    (packet_dir / "context.md").write_text("# context\n", encoding="utf-8")


# --- Mode: simple escape hatch ---


def test_mode_simple_exempts_partial_legacy_packet(tmp_path):
    # task.md + context.md present, plan.md/deliverable_spec.md missing, but
    # the packet declares Mode: simple -> exempt.
    _partial_legacy_packet(tmp_path, _SIMPLE_TASK_MD)
    assert validate_packet_files(tmp_path) == []


def test_mode_simple_is_case_insensitive(tmp_path):
    _partial_legacy_packet(tmp_path, _SIMPLE_TASK_MD.replace("simple", "Simple"))
    assert validate_packet_files(tmp_path) == []


def test_partial_legacy_packet_without_mode_still_fails(tmp_path):
    # No Mode field and a planning file present -> full set required.
    _partial_legacy_packet(tmp_path, _PLAIN_TASK_MD)
    errors = validate_packet_files(tmp_path)
    assert any("plan.md" in e for e in errors)
    assert any("deliverable_spec.md" in e for e in errors)


# --- grain task backfill ---


def _create_packet(root: Path, phase=1, task_num=1) -> Path:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(root), "task", "create", "--phase", str(phase), "--task-num", str(task_num)],
    )
    assert result.exit_code == 0, result.output
    return next((root / "tasks").glob(f"P{phase}-T{task_num:02d}-TASK-*"))


def test_backfill_seeds_missing_planning_files_then_validates(packet_repo):
    runner = CliRunner()
    packet_dir = _create_packet(packet_repo)
    (packet_dir / "plan.md").unlink()
    (packet_dir / "deliverable_spec.md").unlink()

    # Legacy packet with a planning file present but incomplete -> validate fails.
    failing = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate", "--all"])
    assert failing.exit_code != 0, failing.output
    assert "missing required file: plan.md" in failing.output

    backfill = runner.invoke(main, ["--repo", str(packet_repo), "task", "backfill", "--id", "TASK-0001"])
    assert backfill.exit_code == 0, backfill.output
    assert (packet_dir / "plan.md").exists()
    assert (packet_dir / "deliverable_spec.md").exists()

    passing = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate", "--all"])
    assert passing.exit_code == 0, passing.output


def test_backfill_refuses_to_overwrite_existing_file(packet_repo):
    runner = CliRunner()
    packet_dir = _create_packet(packet_repo)
    (packet_dir / "plan.md").write_text("MY OWN PLAN\n", encoding="utf-8")
    (packet_dir / "deliverable_spec.md").unlink()

    backfill = runner.invoke(main, ["--repo", str(packet_repo), "task", "backfill", "TASK-0001"])
    assert backfill.exit_code == 0, backfill.output

    # Existing plan.md left untouched; missing deliverable_spec.md created.
    assert (packet_dir / "plan.md").read_text(encoding="utf-8") == "MY OWN PLAN\n"
    assert "skipped" in backfill.output
    assert (packet_dir / "deliverable_spec.md").exists()


def test_backfill_unknown_packet_errors(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "backfill", "--id", "TASK-9999"])
    assert result.exit_code != 0
    assert "not found" in result.output
