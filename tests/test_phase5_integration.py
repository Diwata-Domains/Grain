"""End-to-end integration tests for Phase 5 core flows."""

from pathlib import Path

from click.testing import CliRunner

from grain.cli import main

_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "phase5"


def _write_manifest(repo_root):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text((_FIXTURES_DIR / "docs_manifest.yaml").read_text(encoding="utf-8"), encoding="utf-8")

    workflow_doc = repo_root / "docs" / "canonical" / "workflow_spec.md"
    workflow_doc.parent.mkdir(parents=True, exist_ok=True)
    workflow_doc.write_text((_FIXTURES_DIR / "workflow_spec.md").read_text(encoding="utf-8"), encoding="utf-8")


def test_phase5_core_flow_happy_path(packet_repo):
    runner = CliRunner()

    result = runner.invoke(main, ["--repo", str(packet_repo), "init"])
    assert result.exit_code == 0, result.output

    _write_manifest(packet_repo)

    result = runner.invoke(main, ["--repo", str(packet_repo), "docs", "validate"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "5", "--task-num", "6"],
    )
    assert result.exit_code == 0, result.output

    packet_dir = packet_repo / "tasks" / "P5-T06-TASK-0001"
    assert packet_dir.exists()

    result = runner.invoke(main, ["--repo", str(packet_repo), "context", "export", "--id", "TASK-0001"])
    assert result.exit_code == 0, result.output
    export_path = packet_dir / "context_export.md"
    assert export_path.exists()
    assert "workflow_spec.md" in export_path.read_text(encoding="utf-8")

    for status in ("ready", "in_progress", "review"):
        result = runner.invoke(
            main,
            ["--repo", str(packet_repo), "task", "status", "--id", "TASK-0001", "--status", status],
        )
        assert result.exit_code == 0, result.output

    (packet_dir / "results.md").write_text(
        (_FIXTURES_DIR / "review_results.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = runner.invoke(main, ["--repo", str(packet_repo), "review", "check", "--id", "TASK-0001"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(main, ["--repo", str(packet_repo), "review", "handoff", "--id", "TASK-0001"])
    assert result.exit_code == 0, result.output
    assert (packet_dir / "handoff.md").exists()

    result = runner.invoke(main, ["--repo", str(packet_repo), "review", "summary", "--id", "TASK-0001"])
    assert result.exit_code == 0, result.output
    assert "next_actions" in result.output
