"""Tests for the handoff artifact service."""

from forge.services.handoff_service import (
    build_handoff_artifact,
    render_handoff_markdown,
    validate_handoff_markdown,
    write_handoff_markdown,
)
from forge.services.task_service import create_packet_directory


def _create_packet(packet_repo, phase=5, task_num=3):
    create_packet_directory(packet_repo, phase=phase, task_num=task_num)


def _packet_dir(packet_repo):
    return packet_repo / "tasks" / "P5-T03-TASK-0001"


def _make_results(packet_dir, status="review"):
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("draft", status, 1),
        encoding="utf-8",
    )
    (packet_dir / "results.md").write_text(
        """# Results: TASK-0001

## Packet State
- **Current Task Status:** review
- **Review Readiness:** ready
- **Recommended Next Status:** review

## Files Changed
- `src/forge/services/handoff_service.py` — added handoff support
- `tests/test_handoff_service.py` — added handoff coverage

## Summary
Implemented handoff support.

## Review Notes
- Verify generated handoff output.

## Review Intake
### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
""",
        encoding="utf-8",
    )


def test_handoff_service_builds_artifact_for_review_ready_packet(packet_repo):
    _create_packet(packet_repo)
    packet_dir = _packet_dir(packet_repo)
    _make_results(packet_dir, status="review")

    result, artifact = build_handoff_artifact(packet_repo, "TASK-0001")

    assert result.ok is True
    assert artifact is not None
    assert artifact.ready_for_handoff is True
    assert artifact.recommended_next_status == "review"
    assert artifact.summary == "Implemented handoff support."
    assert artifact.what_was_built


def test_handoff_service_builds_artifact_for_done_packet(packet_repo):
    _create_packet(packet_repo)
    packet_dir = _packet_dir(packet_repo)
    _make_results(packet_dir, status="done")
    (packet_dir / "task.md").write_text(
        (packet_dir / "task.md").read_text(encoding="utf-8").replace("review", "done", 1),
        encoding="utf-8",
    )

    result, artifact = build_handoff_artifact(packet_repo, "TASK-0001")

    assert result.ok is True
    assert artifact is not None
    assert artifact.recommended_next_status == "done"


def test_handoff_service_reports_missing_packet(packet_repo):
    result, artifact = build_handoff_artifact(packet_repo, "TASK-9999")

    assert result.ok is False
    assert artifact is None
    assert any("not found" in error for error in result.errors)


def test_handoff_service_reports_incomplete_packet(packet_repo):
    _create_packet(packet_repo)

    result, artifact = build_handoff_artifact(packet_repo, "TASK-0001")

    assert result.ok is False
    assert artifact is None
    assert any("results.md" in error for error in result.errors)


def test_handoff_render_and_write(packet_repo):
    _create_packet(packet_repo)
    packet_dir = _packet_dir(packet_repo)
    _make_results(packet_dir, status="review")

    result, artifact = build_handoff_artifact(packet_repo, "TASK-0001")
    assert result.ok is True
    assert artifact is not None

    content = render_handoff_markdown(packet_repo, artifact)
    assert "# Handoff: TASK-0001" in content
    assert "## What Was Built" in content
    assert "Implemented handoff support." in content
    assert validate_handoff_markdown(content) == []

    output_path = write_handoff_markdown(packet_repo, artifact)
    assert output_path == packet_dir / "handoff.md"
    assert output_path.exists()
    assert "# Handoff: TASK-0001" in output_path.read_text(encoding="utf-8")
