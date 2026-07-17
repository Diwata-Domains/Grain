# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""CP-006 lockstep: Grain's ingest validator imports the shared crossing vocabulary,
threads `source_ticket_id`, and accepts the Assay-issued `VERIFY-####-NNN` id."""

import json

from click.testing import CliRunner

from grain.cli import main
from grain.services.verification_service import _validate_ingest_payload
from grain_contracts.verification import IssueType, Outcome, Severity

from tests.test_verify_submit_cmd import _base_repo


def _ingest(tmp_path, runner, payload):
    _base_repo(tmp_path)
    submit = runner.invoke(main, ["--repo", str(tmp_path), "verify", "submit", "--id", "TASK-0179"])
    assert submit.exit_code == 0, submit.output
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "ingest", "--verification-id", "VERIFY-0179-001", "--payload", str(payload_path)],
    )


def test_validator_accepts_every_shared_vocabulary_value():
    """The validator must accept exactly the contract's members — no inline copy that can drift."""
    for issue in IssueType:
        for severity in Severity:
            for outcome in Outcome:
                payload = {
                    "verification_id": "VERIFY-0179-001",
                    "task_id": "TASK-0179",
                    "issue_type": issue.value,
                    "severity": severity.value,
                    "outcome": outcome.value,
                    "summary": "ok",
                }
                assert _validate_ingest_payload(payload, "VERIFY-0179-001") == []


def test_validator_rejects_a_value_outside_the_contract():
    payload = {
        "verification_id": "VERIFY-0179-001",
        "task_id": "TASK-0179",
        "issue_type": "not_a_real_type",
        "severity": "error",
        "outcome": "pass",
        "summary": "ok",
    }
    errors = _validate_ingest_payload(payload, "VERIFY-0179-001")
    assert any("issue_type must be one of" in e for e in errors)
    assert all(member.value in errors[0] for member in IssueType)


def test_source_ticket_id_round_trips_through_ingest(tmp_path):
    runner = CliRunner()
    result = _ingest(
        tmp_path,
        runner,
        {
            "verification_id": "VERIFY-0179-001",
            "task_id": "TASK-0179",
            "source_ticket_id": "ASSAY-42",
            "issue_type": "test_failure",
            "severity": "error",
            "outcome": "pass",
            "summary": "Verification passed; propose closure.",
            "verified_at": "2026-07-17T16:00:00Z",
        },
    )

    assert result.exit_code == 0, result.output
    assert "source_ticket_id  ASSAY-42" in result.output
    result_payload = json.loads(
        (tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_result.json").read_text(encoding="utf-8")
    )
    assert result_payload["source_ticket_id"] == "ASSAY-42"
    assert result_payload["outcome"] == "pass"
    request_payload = json.loads(
        (tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_request.json").read_text(encoding="utf-8")
    )
    assert request_payload["source_ticket_id"] == "ASSAY-42"

    status = runner.invoke(
        main,
        ["--repo", str(tmp_path), "verify", "status", "--verification-id", "VERIFY-0179-001"],
    )
    assert status.exit_code == 0, status.output
    assert "source_ticket_id  ASSAY-42" in status.output


def test_source_ticket_id_optional_for_legacy_payloads(tmp_path):
    runner = CliRunner()
    result = _ingest(
        tmp_path,
        runner,
        {
            "verification_id": "VERIFY-0179-001",
            "task_id": "TASK-0179",
            "issue_type": "screenshot_evidence",
            "severity": "info",
            "outcome": "pass",
            "summary": "Legacy payload without a source ticket.",
        },
    )

    assert result.exit_code == 0, result.output
    result_payload = json.loads(
        (tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_result.json").read_text(encoding="utf-8")
    )
    assert result_payload["source_ticket_id"] == ""


def test_assay_threaded_verify_id_is_accepted(tmp_path):
    """The old foot-gun: a Grain-shaped VERIFY-####-NNN id (as Assay now threads) ingests cleanly."""
    runner = CliRunner()
    result = _ingest(
        tmp_path,
        runner,
        {
            "verification_id": "VERIFY-0179-001",
            "task_id": "TASK-0179",
            "source_ticket_id": "ASSAY-7",
            "issue_type": "bug_finding",
            "severity": "critical",
            "outcome": "fail",
            "summary": "Verification failed; reopen the same task.",
        },
    )

    assert result.exit_code == 0, result.output
    result_payload = json.loads(
        (tmp_path / "tasks" / "P28-T01-TASK-0179" / "verification_result.json").read_text(encoding="utf-8")
    )
    assert result_payload["verification_id"] == "VERIFY-0179-001"
    assert result_payload["outcome"] == "fail"
    assert result_payload["source_ticket_id"] == "ASSAY-7"
