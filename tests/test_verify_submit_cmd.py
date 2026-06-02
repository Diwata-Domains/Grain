import json

from click.testing import CliRunner

from grain.cli import main


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 28 — Assay Verification Integration\nPhase 27 closed: 2026-05-06 — 3 tasks done (grain-verified)\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: TASK-0179\nTask Path: tasks/P28-T01-TASK-0179/\nStatus: review\n",
    )
    _write(
        repo / "docs" / "working" / "backlog.md",
        "## 31. Phase 28 — Assay Verification Integration\n\n### P28-T01 — Implement `grain verify submit` bridge command\n- **Status:** review\n",
    )
    packet_dir = repo / "tasks" / "P28-T01-TASK-0179"
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Verify submit\n\n## Metadata\n"
            "- **ID:** TASK-0179\n"
            "- **Status:** review\n"
            "- **Phase:** Phase 28 — Assay Verification Integration\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")
    _write(
        packet_dir / "results.md",
        """# Results: TASK-0179

## Summary
Implemented verify submit.

## User Review
- **State:** approved
- **Summary:** Ready for verification.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Verification Review
- **State:** not_run
- **Summary:** No verifier configured.

### Findings
- None

## Closure Decision
- **Decision:** pending
- **Reason:** Awaiting verify submit.

### Closure Blockers
- None
""",
    )


def test_verify_submit_creates_request_artifact_and_updates_results(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])

    assert result.exit_code == 0, result.output
    request_path = tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_request.json"
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    assert payload["task_id"] == "TASK-0179"
    assert payload["provider"] == "assay"
    assert payload["status"] == "pending"
    assert payload["verification_id"].startswith("VERIFY-0179-")
    results_text = (tmp_path / "tasks" / "P28-T01-TASK-0179" / "results.md").read_text(encoding="utf-8")
    assert "- **State:** pending" in results_text
    assert "Pending Assay verification request" in results_text


def test_verify_submit_json_output_includes_request_payload(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "verify", "submit", "--id", "TASK-0179"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["verification_request"]["task_id"] == "TASK-0179"
    assert data["verification_request"]["provider"] == "assay"


def test_verify_submit_rejects_unsupported_provider(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179", "--provider", "unknown"],
    )

    assert result.exit_code == 1
    assert "unsupported verification provider" in result.output


def test_verify_submit_requires_review_ready_packet(tmp_path):
    _base_repo(tmp_path)
    task_md = tmp_path / "tasks" / "P28-T01-TASK-0179" / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("- **Status:** review", "- **Status:** in_progress"),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])

    assert result.exit_code == 1
    assert "packet must be in review or done status" in result.output


def test_verify_status_reads_existing_request(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()
    submit = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])
    assert submit.exit_code == 0, submit.output

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "status", "--verification-id", "VERIFY-0179-001"],
    )

    assert result.exit_code == 0, result.output
    assert "verify status: ok" in result.output
    assert "status            pending" in result.output


def test_verify_status_json_output_includes_request_payload(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()
    submit = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])
    assert submit.exit_code == 0, submit.output

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "verify", "status", "--verification-id", "VERIFY-0179-001"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["verification_request"]["verification_id"] == "VERIFY-0179-001"
    assert data["verification_request"]["status"] == "pending"


def test_verify_status_fails_for_unknown_request(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "status", "--verification-id", "VERIFY-9999-001"],
    )

    assert result.exit_code == 1
    assert "verification request 'VERIFY-9999-001' not found" in result.output


def test_verify_ingest_persists_result_and_updates_request_and_results(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()
    submit = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])
    assert submit.exit_code == 0, submit.output

    payload_path = tmp_path / "payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "verification_id": "VERIFY-0179-001",
                "task_id": "TASK-0179",
                "issue_type": "test_failure",
                "severity": "error",
                "outcome": "fail",
                "summary": "Focused verification failed on a packet-level assertion.",
                "artifact_refs": ["artifacts/report.txt"],
                "followup_candidates": [{"title": "Fix packet assertion", "description": "Resolve the failing assertion."}],
                "verified_at": "2026-05-06T16:00:00Z",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "ingest", "--verification-id", "VERIFY-0179-001", "--payload", str(payload_path)],
    )

    assert result.exit_code == 0, result.output
    request_payload = json.loads((tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_request.json").read_text(encoding="utf-8"))
    assert request_payload["status"] == "failed"
    result_payload = json.loads((tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_result.json").read_text(encoding="utf-8"))
    assert result_payload["outcome"] == "fail"
    results_text = (tmp_path / "tasks" / "P28-T01-TASK-0179" / "results.md").read_text(encoding="utf-8")
    assert "- **State:** failed" in results_text
    assert "Focused verification failed on a packet-level assertion." in results_text


def test_verify_ingest_rejects_invalid_payload(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()
    submit = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])
    assert submit.exit_code == 0, submit.output

    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"verification_id": "VERIFY-0179-001"}), encoding="utf-8")

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "ingest", "--verification-id", "VERIFY-0179-001", "--payload", str(payload_path)],
    )

    assert result.exit_code == 1
    assert "payload missing required field: task_id" in result.output
