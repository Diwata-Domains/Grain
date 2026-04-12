"""Tests for `grain orchestrate scope/plan` commands."""

import json

from click.testing import CliRunner

from grain.cli import main


def _write_adapter_profiles(repo_root):
    path = repo_root / "docs" / "runtime" / "adapter_profiles.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
  - backend
  - cli
- `context_priority_rules`:
  - prioritize changed modules

### frontend_adapter
- `adapter_id`: `frontend_adapter`
- `domain_type`: `frontend`
- `applies_to`:
  - react
  - ui
  - browser
- `test_or_validation_hints`:
  - run component tests
""",
        encoding="utf-8",
    )


def test_orchestrate_scope_text_output(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "orchestrate", "scope", "--scope", "add python cli command"],
    )

    assert result.exit_code == 0, result.output
    assert "orchestrate scope: ok" in result.output
    assert "active_adapters" in result.output
    assert "code_adapter" in result.output


def test_orchestrate_scope_json_output_with_adapter_filter(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "orchestrate",
            "scope",
            "--scope",
            "add python cli command",
            "--adapter",
            "code_adapter",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "orchestration scope-signals"
    analysis = data["scope_analysis"]
    assert analysis["adapter_filter"] == ["code_adapter"]
    assert analysis["active_adapters"] == ["code_adapter"]


def test_orchestrate_scope_unknown_adapter_fails(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "orchestrate",
            "scope",
            "--scope",
            "add python cli command",
            "--adapter",
            "missing_adapter",
        ],
    )

    assert result.exit_code == 1
    assert "orchestrate scope failed" in result.output


def test_orchestrate_plan_writes_proposal_artifact(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "orchestrate",
            "plan",
            "--scope",
            "build react ui and python backend api",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "orchestrate plan: ok" in result.output
    proposals_dir = tmp_path / "docs" / "working" / "proposals"
    proposal_files = list(proposals_dir.glob("OP-*.json"))
    assert len(proposal_files) == 1
    payload = json.loads(proposal_files[0].read_text(encoding="utf-8"))
    assert payload["status"] == "draft"
    assert payload["scope_summary"] == "build react ui and python backend api"


def test_orchestrate_plan_json_output_reports_artifact(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "orchestrate",
            "plan",
            "--scope",
            "phase replan for checkout",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["plan_mode"] == "phase"
    assert data["proposal_path"].endswith(".json")
    assert data["orchestrator_plan"]["status"] == "draft"


def test_orchestrate_accept_marks_plan_as_accepted(tmp_path):
    _write_adapter_profiles(tmp_path)
    proposals_dir = tmp_path / "docs" / "working" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal = proposals_dir / "OP-TEST1234.json"
    proposal.write_text(
        json.dumps(
            {
                "plan_id": "OP-TEST1234",
                "status": "draft",
                "packet_candidates": [],
            }
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "orchestrate", "accept", "--plan", "OP-TEST1234"],
    )

    assert result.exit_code == 0, result.output
    assert "orchestrate accept: ok" in result.output
    payload = json.loads(proposal.read_text(encoding="utf-8"))
    assert payload["status"] == "accepted"


def test_orchestrate_accept_fails_for_missing_plan(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "orchestrate", "accept", "--plan", "OP-MISSING"],
    )

    assert result.exit_code == 1
    assert "plan proposal not found" in result.output
