"""Tests for AGENTS.md generation via grain init and grain onboard."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.agents_md_service import (
    _MARKER_END,
    _MARKER_START,
    write_agents_md,
)


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


# ---------------------------------------------------------------------------
# agents_md_service unit tests
# ---------------------------------------------------------------------------


def test_creates_agents_md_when_absent(tmp_path: Path):
    result = write_agents_md(tmp_path)
    assert result.action == "created"
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert _MARKER_START in agents
    assert _MARKER_END in agents
    assert "grain workflow next" in agents
    assert "no packet exists on disk" in agents


def test_appends_block_to_existing_agents_md(tmp_path: Path):
    existing = "# My Project\n\nAlways use strict mode.\n"
    (tmp_path / "AGENTS.md").write_text(existing, encoding="utf-8")
    result = write_agents_md(tmp_path)
    assert result.action == "appended"
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    # User content preserved above
    assert "Always use strict mode." in content
    # Grain block appended below
    assert _MARKER_START in content
    assert content.index("Always use strict mode.") < content.index(_MARKER_START)


def test_updates_grain_block_in_place(tmp_path: Path):
    original_block = f"{_MARKER_START}\nOLD CONTENT\n{_MARKER_END}"
    full_content = f"# My Project\n\nCustom rule here.\n\n{original_block}\n\nMore user content.\n"
    (tmp_path / "AGENTS.md").write_text(full_content, encoding="utf-8")
    result = write_agents_md(tmp_path)
    assert result.action == "updated"
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    # User content before and after is preserved
    assert "Custom rule here." in content
    assert "More user content." in content
    # Old block replaced
    assert "OLD CONTENT" not in content
    # New block present
    assert "grain workflow next" in content


def test_skipped_when_block_already_current(tmp_path: Path):
    # Write, then write again — second should skip
    write_agents_md(tmp_path)
    result = write_agents_md(tmp_path)
    assert result.action == "skipped"


def test_dry_run_does_not_write(tmp_path: Path):
    result = write_agents_md(tmp_path, dry_run=True)
    assert result.action == "created"
    assert result.dry_run is True
    assert not (tmp_path / "AGENTS.md").exists()


def test_dry_run_append_does_not_write(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Existing\n", encoding="utf-8")
    result = write_agents_md(tmp_path, dry_run=True)
    assert result.action == "appended"
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert _MARKER_START not in content  # not written


def test_detects_claude_md_exists(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Claude instructions\n", encoding="utf-8")
    result = write_agents_md(tmp_path)
    assert result.claude_md_exists is True


def test_claude_md_absent_flag_false(tmp_path: Path):
    result = write_agents_md(tmp_path)
    assert result.claude_md_exists is False


def test_user_content_outside_markers_never_rewritten(tmp_path: Path):
    user_content = "# My Rules\n\nNever break prod.\n"
    (tmp_path / "AGENTS.md").write_text(
        user_content + f"\n{_MARKER_START}\nOLD\n{_MARKER_END}\n\nTrailing note.\n",
        encoding="utf-8",
    )
    write_agents_md(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "Never break prod." in content
    assert "Trailing note." in content
    assert "OLD" not in content


# ---------------------------------------------------------------------------
# grain init --update-agents
# ---------------------------------------------------------------------------


def test_init_creates_agents_md(tmp_path: Path):
    result = _run(tmp_path, "init")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "AGENTS.md").exists()
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert _MARKER_START in content
    assert "grain workflow next" in content


def test_init_update_agents_only(tmp_path: Path):
    # Seed an AGENTS.md with stale grain block
    old_block = f"{_MARKER_START}\nOLD GRAIN CONTENT\n{_MARKER_END}"
    (tmp_path / "AGENTS.md").write_text(f"# Existing\n\n{old_block}\n", encoding="utf-8")
    result = _run(tmp_path, "init", "--update-agents")
    assert result.exit_code == 0, result.output
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "OLD GRAIN CONTENT" not in content
    assert "grain workflow next" in content
    assert "Existing" in content  # user content preserved


def test_init_warns_when_claude_md_present(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
    result = _run(tmp_path, "init")
    assert result.exit_code == 0, result.output
    assert "CLAUDE.md" in result.output


def test_init_dry_run_does_not_create_agents_md(tmp_path: Path):
    result = _run(tmp_path, "init", "--dry-run")
    assert result.exit_code == 0, result.output
    assert not (tmp_path / "AGENTS.md").exists()


# ---------------------------------------------------------------------------
# grain onboard
# ---------------------------------------------------------------------------


def test_onboard_creates_agents_md(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert (tmp_path / "AGENTS.md").exists()
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "grain workflow next" in content


def test_onboard_appends_to_existing_agents_md(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert "existing AGENTS.md" in result.output or "appended" in result.output
    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "Existing project rules" in content
    assert "grain workflow next" in content


def test_onboard_json_includes_agents_md_fields(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "onboard", str(tmp_path), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "agents_md_action" in data
    assert data["agents_md_action"] in {"created", "updated", "appended", "skipped"}
    assert "claude_md_exists" in data
