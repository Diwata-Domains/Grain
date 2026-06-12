"""Tests for branch_policy enforcement — workflow next and guard integration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

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


def _manifest(tmp_path: Path, **branch_policy_kwargs) -> None:
    policy_lines = []
    for k, v in branch_policy_kwargs.items():
        if isinstance(v, bool):
            policy_lines.append(f"  {k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            policy_lines.append(f"  {k}: {v}")
        else:
            policy_lines.append(f'  {k}: "{v}"')

    policy_block = "branch_policy:\n" + "\n".join(policy_lines) + "\n" if policy_lines else ""
    _write(
        tmp_path / "docs/runtime/docs_manifest.yaml",
        f"version: 1\nproject:\n  name: Test\n{policy_block}canonical: []\nworking: []\nruntime: []\n",
    )


def _base(tmp_path: Path, phase: int = 1) -> None:
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: none\n")
    _write(tmp_path / "docs/working/backlog.md",
           f"# Backlog\n\n## 2. Phase {phase} — Test\n\n"
           f"### P{phase}-T01 — Task\n- **Status:** done\n")
    _write(tmp_path / "docs/working/current_focus.md",
           f"# Current Focus\n\n## Current Phase\nPhase {phase} — Test Phase\n")


# ── load_branch_policy ─────────────────────────────────────────────────────────

def test_load_branch_policy_defaults_when_absent(tmp_path):
    from grain.adapters.manifest import load_branch_policy
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: T\ncanonical: []\nworking: []\nruntime: []\n")
    p = load_branch_policy(tmp_path)
    assert p.mode == "off"
    assert p.enforce is False
    assert p.pattern == ""


def test_load_branch_policy_reads_fields(tmp_path):
    from grain.adapters.manifest import load_branch_policy
    _manifest(tmp_path, mode="phase", pattern="*-P{phase}-*", enforce=True, message="Wrong branch")
    p = load_branch_policy(tmp_path)
    assert p.mode == "phase"
    assert p.pattern == "*-P{phase}-*"
    assert p.enforce is True
    assert p.message == "Wrong branch"


def test_load_branch_policy_invalid_mode_falls_back_to_off(tmp_path):
    from grain.adapters.manifest import load_branch_policy
    _manifest(tmp_path, mode="invalid_value")
    p = load_branch_policy(tmp_path)
    assert p.mode == "off"


# ── _branch_matches ────────────────────────────────────────────────────────────

def test_branch_matches_phase_mode_with_phase_token(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("feature/P31-work", "phase", "", "31", "") is True


def test_branch_matches_phase_mode_without_phase_token(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("main", "phase", "", "31", "") is False


def test_branch_matches_task_mode_with_task_id(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("feature/TASK-0211-work", "task", "", "31", "TASK-0211") is True


def test_branch_matches_task_mode_with_phase(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("feature/P31-T08-work", "task", "", "31", "TASK-0211") is True


def test_branch_matches_task_mode_no_match(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("main", "task", "", "31", "TASK-0211") is False


def test_branch_matches_task_mode_no_active_task(tmp_path):
    from grain.services.workflow_service import _branch_matches
    # No active task — can't check task ID; return True to avoid false positives
    assert _branch_matches("main", "task", "", "31", "none") is True


def test_branch_matches_custom_pattern(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("release/P31", "phase", "release/P{phase}", "31", "") is True
    assert _branch_matches("feature/P31", "phase", "release/P{phase}", "31", "") is False


def test_branch_matches_empty_branch_returns_false(tmp_path):
    from grain.services.workflow_service import _branch_matches
    assert _branch_matches("", "phase", "", "31", "") is False


# ── mode: off ─────────────────────────────────────────────────────────────────

def test_mode_off_no_check_runs(tmp_path):
    _manifest(tmp_path, mode="off")
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch") as mock_branch:
        result = _run(tmp_path, "workflow", "next")
        mock_branch.assert_not_called()
    assert result.exit_code == 0


def test_mode_off_default_when_block_absent(tmp_path):
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: T\ncanonical: []\nworking: []\nruntime: []\n")
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch") as mock_branch:
        result = _run(tmp_path, "workflow", "next")
        mock_branch.assert_not_called()
    assert result.exit_code == 0


# ── mode: phase, branch matches ───────────────────────────────────────────────

def test_phase_mode_matching_branch_ok(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="feature/P1-work"):
        result = _run(tmp_path, "workflow", "next")
    # No wrong_branch in output
    assert "wrong_branch" not in result.output


# ── mode: phase, branch mismatches, enforce: false (warn) ─────────────────────

def test_phase_mode_mismatch_warn_only(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=False)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "next")
    # Command proceeds (exit 0); warning emitted somewhere in combined output
    assert result.exit_code == 0
    assert "branch" in result.output.lower()


def test_phase_mode_mismatch_warn_json_has_warning(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=False)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "next", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    # Warning should appear in evaluation.warnings
    warnings = data.get("evaluation", {}).get("warnings", [])
    assert any("branch" in w.lower() for w in warnings)


# ── mode: phase, branch mismatches, enforce: true ─────────────────────────────

def test_phase_mode_mismatch_enforce_returns_wrong_branch(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "next", fmt="json")
    data = json.loads(result.output)
    evaluation = data.get("evaluation", {})
    assert evaluation.get("stop_reason") == "wrong_branch"
    assert evaluation.get("ok") is False


def test_phase_mode_mismatch_enforce_suggested_branch_in_json(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "next", fmt="json")
    data = json.loads(result.output)
    evaluation = data.get("evaluation", {})
    assert "suggested_branch" in evaluation
    assert "P1" in evaluation["suggested_branch"]


# ── mode: task, branch matches task ID ────────────────────────────────────────

def test_task_mode_matching_task_id_ok(tmp_path):
    _manifest(tmp_path, mode="task", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="feature/TASK-0211-work"):
        # active_task_id is "none" in base (no active task), so task mode won't fail
        result = _run(tmp_path, "workflow", "next")
    assert "wrong_branch" not in result.output


# ── GRAIN_SKIP_BRANCH_CHECK escape hatch ──────────────────────────────────────

def test_skip_env_bypasses_enforce(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "next",
                      env={"GRAIN_SKIP_BRANCH_CHECK": "1"})
    assert result.exit_code == 0


def test_skip_env_creates_tooling_notes(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        _run(tmp_path, "workflow", "next", env={"GRAIN_SKIP_BRANCH_CHECK": "1"})
    notes = tmp_path / "docs" / "working" / "tooling_notes.md"
    assert notes.exists()
    text = notes.read_text()
    assert "GRAIN_SKIP_BRANCH_CHECK" in text


def test_skip_env_warn_mode_still_logs(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=False)
    _base(tmp_path)
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        _run(tmp_path, "workflow", "next", env={"GRAIN_SKIP_BRANCH_CHECK": "1"})
    notes = tmp_path / "docs" / "working" / "tooling_notes.md"
    assert notes.exists()
    assert "GRAIN_SKIP_BRANCH_CHECK" in notes.read_text()


# ── WorkflowEvaluation.suggested_branch field ─────────────────────────────────

def test_workflow_evaluation_has_suggested_branch_field():
    from grain.domain.workflow import WorkflowEvaluation
    e = WorkflowEvaluation(ok=True, suggested_branch="feature/P31-work")
    assert e.suggested_branch == "feature/P31-work"


def test_workflow_evaluation_suggested_branch_default_empty():
    from grain.domain.workflow import WorkflowEvaluation
    e = WorkflowEvaluation(ok=True)
    assert e.suggested_branch == ""


# ── _suggest_branch ────────────────────────────────────────────────────────────

def test_suggest_branch_phase_mode():
    from grain.services.workflow_service import _suggest_branch
    assert _suggest_branch("phase", "1", "") == "feature/P1-work"


def test_suggest_branch_task_mode_with_task():
    from grain.services.workflow_service import _suggest_branch
    assert _suggest_branch("task", "31", "TASK-0211") == "feature/TASK-0211-work"


def test_suggest_branch_task_mode_no_active_task():
    from grain.services.workflow_service import _suggest_branch
    assert _suggest_branch("task", "31", "none") == "feature/P31-work"


# ── guard integration ──────────────────────────────────────────────────────────

def test_guard_branch_policy_pass_when_off(tmp_path):
    _manifest(tmp_path, mode="off")
    _base(tmp_path)
    # current_task must be set for guard to run
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: none\n")
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "guard", fmt="json")
    data = json.loads(result.output)
    branch_check = next((c for c in data.get("checks", []) if c["id"] == "branch_policy"), None)
    assert branch_check is not None
    assert branch_check["result"] == "pass"


def test_guard_branch_policy_warn_when_mismatch(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=False)
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: none\n")
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "guard", fmt="json")
    data = json.loads(result.output)
    branch_check = next((c for c in data.get("checks", []) if c["id"] == "branch_policy"), None)
    assert branch_check is not None
    assert branch_check["result"] == "warn"


def test_guard_branch_policy_fail_when_enforce(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: none\n")
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "guard", fmt="json")
    data = json.loads(result.output)
    branch_check = next((c for c in data.get("checks", []) if c["id"] == "branch_policy"), None)
    assert branch_check is not None
    assert branch_check["result"] == "fail"
    assert "remediation" in branch_check


def test_guard_branch_policy_remediation_has_git_command(tmp_path):
    _manifest(tmp_path, mode="phase", enforce=True)
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: none\n")
    with patch("grain.services.workflow_service._read_current_branch", return_value="main"):
        result = _run(tmp_path, "workflow", "guard", fmt="json")
    data = json.loads(result.output)
    branch_check = next((c for c in data.get("checks", []) if c["id"] == "branch_policy"), None)
    assert "git checkout" in branch_check.get("remediation", "")
