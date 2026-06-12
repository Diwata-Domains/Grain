"""Tests for upgrade_policy enforcement — version gate, grace period, bypass, ratchet."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from grain.cli import main


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(tmp_path: Path, *args: str, env: dict | None = None, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd, env=env or {}, catch_exceptions=False)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _manifest(tmp_path: Path, **upgrade_policy_kwargs) -> None:
    """Write a minimal manifest with an upgrade_policy block."""
    policy_lines = []
    for k, v in upgrade_policy_kwargs.items():
        if isinstance(v, bool):
            policy_lines.append(f"  {k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            policy_lines.append(f"  {k}: {v}")
        else:
            policy_lines.append(f'  {k}: "{v}"')

    policy_block = "upgrade_policy:\n" + "\n".join(policy_lines) + "\n" if policy_lines else ""
    _write(
        tmp_path / "docs/runtime/docs_manifest.yaml",
        f"version: 1\nproject:\n  name: Test\n{policy_block}canonical: []\nworking: []\nruntime: []\n",
    )


def _working_docs(tmp_path: Path) -> None:
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n")


# ── load_upgrade_policy ────────────────────────────────────────────────────────

def test_load_upgrade_policy_defaults_when_absent(tmp_path):
    from grain.adapters.manifest import load_upgrade_policy
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: T\ncanonical: []\nworking: []\nruntime: []\n")
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == ""
    assert p.enforce is False
    assert p.enforce_after_days == 0


def test_load_upgrade_policy_reads_fields(tmp_path):
    from grain.adapters.manifest import load_upgrade_policy
    _manifest(tmp_path, min_version="1.0.0", min_version_set_at="2026-01-01",
              enforce=True, enforce_after_days=7, message="Upgrade now")
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == "1.0.0"
    assert p.min_version_set_at == "2026-01-01"
    assert p.enforce is True
    assert p.enforce_after_days == 7
    assert p.message == "Upgrade now"


def test_load_upgrade_policy_empty_min_version(tmp_path):
    from grain.adapters.manifest import load_upgrade_policy
    _manifest(tmp_path, min_version="", enforce=False)
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == ""


def test_load_upgrade_policy_no_manifest(tmp_path):
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == ""
    assert p.enforce is False


# ── No check when min_version is empty ────────────────────────────────────────

def test_no_gate_when_min_version_empty(tmp_path):
    _manifest(tmp_path, min_version="", enforce=True)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0


def test_no_gate_when_upgrade_policy_absent(tmp_path):
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: T\ncanonical: []\nworking: []\nruntime: []\n")
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0


# ── No gate when version is current ───────────────────────────────────────────

def test_no_gate_when_version_current(tmp_path):
    from importlib.metadata import version as _v, PackageNotFoundError
    try:
        installed = _v("grain-kit")
    except PackageNotFoundError:
        pytest.skip("grain-kit not installed via importlib")
    _manifest(tmp_path, min_version=installed, enforce=True)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0


# ── Warn-only mode ─────────────────────────────────────────────────────────────

def test_warn_banner_when_enforce_false(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=False)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0
    # Banner appears in output (stdout+stderr mixed in CliRunner)
    assert "999.0.0" in result.output
    assert "grain upgrade" in result.output


def test_warn_suppressed_in_json_format(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=False)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    # Output must be parseable JSON (banner suppressed in json mode)
    data = json.loads(result.output)
    assert "run_at" in data or "phase" in data or "workflow" in data


# ── Enforce mode ───────────────────────────────────────────────────────────────

def test_enforce_mode_exits_2(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 2


def test_enforce_mode_message_in_output(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    output_lower = result.output.lower()
    assert "upgrade required" in output_lower or "upgrade" in output_lower
    assert "999.0.0" in result.output


def test_enforce_mode_json_output(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 2
    # JSON is written to stdout first line; stderr message may follow in mixed output
    first_line = result.output.splitlines()[0] if result.output.strip() else "{}"
    data = json.loads(first_line)
    assert data["error"] == "upgrade_required"
    assert data["required_version"] == "999.0.0"
    assert "installed_version" in data
    assert "upgrade_command" in data


def test_enforce_mode_custom_message_in_output(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True,
              enforce_after_days=0, message="Contact ops to upgrade")
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 2
    assert "Contact ops to upgrade" in result.output


# ── Grace period ───────────────────────────────────────────────────────────────

def test_grace_period_warns_not_blocks(tmp_path):
    from datetime import date
    today = date.today().isoformat()
    _manifest(tmp_path, min_version="999.0.0", enforce=True,
              enforce_after_days=7, min_version_set_at=today)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0  # warn-only during grace
    assert "999.0.0" in result.output


def test_grace_period_blocks_after_elapsed(tmp_path):
    from datetime import date, timedelta
    old_date = (date.today() - timedelta(days=10)).isoformat()
    _manifest(tmp_path, min_version="999.0.0", enforce=True,
              enforce_after_days=7, min_version_set_at=old_date)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 2


def test_grace_period_exactly_on_day_blocks(tmp_path):
    from datetime import date, timedelta
    boundary_date = (date.today() - timedelta(days=7)).isoformat()
    _manifest(tmp_path, min_version="999.0.0", enforce=True,
              enforce_after_days=7, min_version_set_at=boundary_date)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 2


# ── Allowed-command bypass ─────────────────────────────────────────────────────

def test_upgrade_bypasses_gate(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    result = _run(tmp_path, "upgrade", "--dry-run")
    assert result.exit_code != 2


def test_doctor_bypasses_gate(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    result = _run(tmp_path, "doctor")
    assert result.exit_code != 2


# ── GRAIN_SKIP_VERSION_CHECK escape hatch ─────────────────────────────────────

def test_skip_env_bypasses_enforce_mode(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    result = _run(tmp_path, "status", env={"GRAIN_SKIP_VERSION_CHECK": "1"})
    assert result.exit_code == 0


def test_skip_env_creates_tooling_notes(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    _run(tmp_path, "status", env={"GRAIN_SKIP_VERSION_CHECK": "1"})
    notes_path = tmp_path / "docs" / "working" / "tooling_notes.md"
    assert notes_path.exists()
    text = notes_path.read_text()
    assert "GRAIN_SKIP_VERSION_CHECK" in text
    assert "999.0.0" in text


def test_skip_env_appends_to_existing_notes(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=True, enforce_after_days=0)
    _working_docs(tmp_path)
    notes_path = tmp_path / "docs" / "working" / "tooling_notes.md"
    _write(notes_path,
           "# Tooling Notes\n\n| Date | Type | Severity | Command | Message | Status |\n"
           "|------|------|----------|---------|---------|--------|\n"
           "| 2026-01-01 | bug | low | grain init | existing note | open |\n")
    _run(tmp_path, "status", env={"GRAIN_SKIP_VERSION_CHECK": "1"})
    text = notes_path.read_text()
    assert "existing note" in text
    assert "GRAIN_SKIP_VERSION_CHECK" in text


def test_skip_env_logs_even_in_warn_mode(tmp_path):
    _manifest(tmp_path, min_version="999.0.0", enforce=False)
    _working_docs(tmp_path)
    _run(tmp_path, "status", env={"GRAIN_SKIP_VERSION_CHECK": "1"})
    notes_path = tmp_path / "docs" / "working" / "tooling_notes.md"
    assert notes_path.exists()
    assert "GRAIN_SKIP_VERSION_CHECK" in notes_path.read_text()


# ── write_upgrade_policy_min_version ──────────────────────────────────────────

def test_ratchet_updates_min_version(tmp_path):
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    _manifest(tmp_path, min_version="0.1.0", min_version_set_at="2025-01-01", enforce=False)
    write_upgrade_policy_min_version(tmp_path, "0.4.0")
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == "0.4.0"


def test_ratchet_updates_min_version_set_at(tmp_path):
    from datetime import date
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    _manifest(tmp_path, min_version="0.1.0", min_version_set_at="2025-01-01", enforce=False)
    write_upgrade_policy_min_version(tmp_path, "0.4.0")
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.min_version_set_at == date.today().isoformat()


def test_ratchet_preserves_enforce_flag(tmp_path):
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    _manifest(tmp_path, min_version="0.1.0", enforce=True, enforce_after_days=3)
    write_upgrade_policy_min_version(tmp_path, "0.4.0")
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.enforce is True
    assert p.enforce_after_days == 3


def test_ratchet_creates_block_when_absent(tmp_path):
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: T\ncanonical: []\nworking: []\nruntime: []\n")
    write_upgrade_policy_min_version(tmp_path, "0.4.0")
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == "0.4.0"
    assert p.enforce is False


def test_ratchet_no_manifest_returns_false(tmp_path):
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    result = write_upgrade_policy_min_version(tmp_path, "0.4.0")
    assert result is False


def test_ratchet_preserves_other_manifest_content(tmp_path):
    from grain.services.upgrade_service import write_upgrade_policy_min_version
    _manifest(tmp_path, min_version="0.1.0", enforce=False)
    write_upgrade_policy_min_version(tmp_path, "0.4.0")
    text = (tmp_path / "docs/runtime/docs_manifest.yaml").read_text()
    assert "canonical:" in text
    assert "working:" in text


# ── grain upgrade ratchets policy ─────────────────────────────────────────────

def test_grain_upgrade_dry_run_does_not_ratchet(tmp_path):
    _manifest(tmp_path, min_version="0.1.0", min_version_set_at="2025-01-01", enforce=False)
    _run(tmp_path, "upgrade", "--dry-run")
    from grain.adapters.manifest import load_upgrade_policy
    p = load_upgrade_policy(tmp_path)
    assert p.min_version == "0.1.0"
