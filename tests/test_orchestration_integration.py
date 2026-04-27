"""Integration tests across adapter/orchestrate commands and plan validation."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.validators.orchestrator_validator import validate_orchestrator_plan_dict


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_adapter_profiles(repo_root: Path) -> None:
    _write(
        repo_root / "docs" / "runtime" / "adapter_profiles.md",
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
- `test_or_validation_hints`:
  - run component tests
""",
    )


def test_orchestrate_plan_artifact_validates_against_known_adapters(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()

    adapter_list = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "adapter", "list"],
    )
    assert adapter_list.exit_code == 0, adapter_list.output
    adapter_payload = json.loads(adapter_list.output)
    known_adapter_ids = {
        profile["adapter_id"] for profile in adapter_payload["profiles"]
    }

    plan_result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "orchestrate",
            "plan",
            "--scope",
            "build react ui and python backend api",
        ],
    )
    assert plan_result.exit_code == 0, plan_result.output
    plan_payload = json.loads(plan_result.output)
    proposal_path = tmp_path / plan_payload["proposal_path"]
    assert proposal_path.exists()

    artifact = json.loads(proposal_path.read_text(encoding="utf-8"))
    errors = validate_orchestrator_plan_dict(
        artifact,
        known_adapter_ids=known_adapter_ids,
    )
    assert errors == []


def test_adapter_show_and_orchestrate_scope_align_on_adapter_id(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()

    show_result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "adapter",
            "show",
            "--id",
            "code_adapter",
        ],
    )
    assert show_result.exit_code == 0, show_result.output
    adapter_payload = json.loads(show_result.output)

    scope_result = runner.invoke(
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
    assert scope_result.exit_code == 0, scope_result.output
    scope_payload = json.loads(scope_result.output)
    analysis = scope_payload["scope_analysis"]

    assert adapter_payload["adapter"]["adapter_id"] == "code_adapter"
    assert analysis["active_adapters"] == ["code_adapter"]
