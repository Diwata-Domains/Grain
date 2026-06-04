from pathlib import Path


from grain.validators.packet_validator import validate_closure

_REQUIRED_FILES = ("task.md", "context.md", "plan.md", "deliverable_spec.md")

_VALID_TASK_MD = """\
# Task: Test

## Metadata
- **ID:** TASK-0042
- **Status:** review
- **Phase:** Phase 3 — Task Packet System
- **Dependencies:** none

## Objective
Something.
"""

_RESULTS_CONTENT = """\
# Results: TASK-0042

## Summary
Work completed.

## User Review
- **State:** approved
- **Summary:** Work accepted.
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
- **Reason:** Ready for closure.

### Closure Blockers
- None
"""


def _make_closure_ready(tmp_path: Path) -> Path:
    """Write a packet that satisfies all closure requirements."""
    (tmp_path / "task.md").write_text(_VALID_TASK_MD)
    for name in ("context.md", "plan.md", "deliverable_spec.md"):
        (tmp_path / name).write_text(f"# {name}\n")
    (tmp_path / "results.md").write_text(_RESULTS_CONTENT)
    return tmp_path


def test_validate_closure_passes_ready_packet(tmp_path):
    _make_closure_ready(tmp_path)
    assert validate_closure(tmp_path) == []


def test_validate_closure_fails_missing_results_md(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "results.md").unlink()
    errors = validate_closure(tmp_path)
    assert any("results.md" in e for e in errors)


def test_validate_closure_fails_empty_results_md(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "results.md").write_text("   \n")
    errors = validate_closure(tmp_path)
    assert any("empty" in e for e in errors)


def test_validate_closure_fails_wrong_status(tmp_path):
    _make_closure_ready(tmp_path)
    task_md = tmp_path / "task.md"
    task_md.write_text(_VALID_TASK_MD.replace("review", "in_progress"))
    errors = validate_closure(tmp_path)
    assert any("in_progress" in e for e in errors)


def test_validate_closure_fails_draft_status(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "task.md").write_text(_VALID_TASK_MD.replace("review", "draft"))
    errors = validate_closure(tmp_path)
    assert any("draft" in e for e in errors)


def test_validate_closure_fails_missing_required_file(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "plan.md").unlink()
    errors = validate_closure(tmp_path)
    assert any("plan.md" in e for e in errors)


def test_validate_closure_accumulates_multiple_errors(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "results.md").unlink()
    (tmp_path / "task.md").write_text(_VALID_TASK_MD.replace("review", "draft"))
    errors = validate_closure(tmp_path)
    assert len(errors) >= 2


def test_validate_closure_tolerates_missing_task_md_status_check(tmp_path):
    # If task.md is absent, file validator catches it; status check is skipped gracefully
    for name in ("context.md", "plan.md", "deliverable_spec.md"):
        (tmp_path / name).write_text(f"# {name}\n")
    (tmp_path / "results.md").write_text(_RESULTS_CONTENT)
    errors = validate_closure(tmp_path)
    # Should report missing task.md from file validator, not crash
    assert any("task.md" in e for e in errors)


def test_validate_closure_fails_pending_verification(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "results.md").write_text(
        _RESULTS_CONTENT.replace("- **State:** not_run", "- **State:** pending"),
    )
    errors = validate_closure(tmp_path)
    assert any("verification state is 'pending'" in e for e in errors)


def test_validate_closure_fails_failed_verification(tmp_path):
    _make_closure_ready(tmp_path)
    (tmp_path / "results.md").write_text(
        _RESULTS_CONTENT.replace("- **State:** not_run", "- **State:** failed"),
    )
    errors = validate_closure(tmp_path)
    assert any("verification state is 'failed'" in e for e in errors)
