"""Tests for the review validation service."""

from grain.services.review_service import (
    build_packet_review_summary,
    check_packet_review_readiness,
)
from grain.services.task_service import create_packet_directory


def _create_review_packet(packet_repo, phase=5, task_num=1):
    return create_packet_directory(packet_repo, phase=phase, task_num=task_num)


def _packet_dir(packet_repo):
    return packet_repo / "tasks" / "P5-T01-TASK-0001"


_APPROVED_RESULTS = """# Results: TASK-0001

## Summary
Implemented review-ready task.

## User Review
- **State:** approved
- **Summary:** Ready to close.
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
- **Reason:** Awaiting close command.

### Closure Blockers
- None
"""


def test_review_service_reports_ready_packet(packet_repo):
    _create_review_packet(packet_repo)
    packet_dir = _packet_dir(packet_repo)
    (packet_dir / "task.md").write_text(
        (packet_dir / "task.md").read_text(encoding="utf-8").replace("draft", "review", 1),
        encoding="utf-8",
    )
    (packet_dir / "results.md").write_text(_APPROVED_RESULTS, encoding="utf-8")

    result, report = check_packet_review_readiness(packet_repo, "TASK-0001")

    assert result.ok is True
    assert report is not None
    assert report.review_ready is True
    assert report.completion_ready is True
    assert report.blockers == []
    assert result.status == "review"


def test_review_service_reports_missing_packet(packet_repo):
    result, report = check_packet_review_readiness(packet_repo, "TASK-9999")

    assert result.ok is False
    assert report is None
    assert any("not found" in error for error in result.errors)


def test_review_service_reports_incomplete_packet(packet_repo):
    _create_review_packet(packet_repo)

    result, report = check_packet_review_readiness(packet_repo, "TASK-0001")

    assert result.ok is False
    assert report is not None
    assert report.review_ready is False
    assert report.completion_ready is False
    assert any("results.md" in error for error in report.blockers)
    assert any("review" in warning for warning in report.warnings)


def test_review_service_builds_summary_for_ready_packet(packet_repo):
    _create_review_packet(packet_repo)
    packet_dir = _packet_dir(packet_repo)
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("draft", "review", 1),
        encoding="utf-8",
    )
    (packet_dir / "results.md").write_text(
        """# Results: TASK-0001

## Packet State
- **Current Task Status:** review
- **Review Readiness:** ready
- **Recommended Next Status:** review

## Files Changed
- `tests/test_review_service.py` — added review summary coverage

## Summary
Implemented review summary support.

## Review Notes
- Verify summary output and next actions.

## User Review
- **State:** approved
- **Summary:** Review accepted.
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
- **Reason:** Awaiting close.

### Closure Blockers
- None
""",
        encoding="utf-8",
    )

    result, summary = build_packet_review_summary(packet_repo, "TASK-0001")

    assert result.ok is True
    assert summary is not None
    assert summary.review_ready is True
    assert summary.completion_ready is True
    assert summary.recommended_next_status == "done"
    assert "Implemented review summary support." in summary.packet_summary
    assert summary.next_actions


def test_review_service_summary_reports_blockers(packet_repo):
    _create_review_packet(packet_repo)

    result, summary = build_packet_review_summary(packet_repo, "TASK-0001")

    assert result.ok is True
    assert summary is not None
    assert summary.review_ready is False
    assert summary.validation_findings
    assert any("results.md" in finding for finding in summary.validation_findings)
