# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Unit tests for the grain capture inbox service."""

from __future__ import annotations

import pytest

from grain.services import capture_service as cs


def test_capture_returns_monotonic_ids(packet_repo):
    a = cs.capture(packet_repo, "first", today="2026-07-17")
    b = cs.capture(packet_repo, "second", kind="edit", today="2026-07-17")
    assert a == "CAP-0001"
    assert b == "CAP-0002"


def test_capture_rejects_empty_title(packet_repo):
    with pytest.raises(cs.CaptureError):
        cs.capture(packet_repo, "   ")


def test_capture_rejects_bad_kind(packet_repo):
    with pytest.raises(cs.CaptureError):
        cs.capture(packet_repo, "x", kind="banana")


def test_list_and_filter(packet_repo):
    cs.capture(packet_repo, "one", today="2026-07-17")
    cs.capture(packet_repo, "two", today="2026-07-17")
    caps = cs.list_captures(packet_repo)
    assert [c.id for c in caps] == ["CAP-0001", "CAP-0002"]
    assert [c.title for c in caps] == ["one", "two"]
    assert all(c.status == "new" for c in caps)
    assert cs.list_captures(packet_repo, status="dropped") == []


def test_pipe_in_title_is_sanitized(packet_repo):
    cs.capture(packet_repo, "a | b", note="x | y", today="2026-07-17")
    cap = cs.list_captures(packet_repo)[0]
    assert cap.title == "a / b"
    assert cap.note == "x / y"


def test_drop_marks_dropped(packet_repo):
    cid = cs.capture(packet_repo, "toss", today="2026-07-17")
    cs.drop(packet_repo, cid)
    dropped = cs.list_captures(packet_repo, status="dropped")
    assert [c.id for c in dropped] == [cid]


def test_promote_scaffolds_packet_and_backlog_entry(packet_repo):
    backlog = packet_repo / "docs" / "working" / "backlog.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text("# Backlog\n\n## Phase 3 — Things\n")
    cid = cs.capture(packet_repo, "Dark mode toggle", kind="feature", today="2026-07-17")

    result = cs.promote(packet_repo, cid, phase=3)

    assert result.task_id.startswith("TASK-")
    assert result.simple is False  # feature → full packet
    packets = list((packet_repo / "tasks").glob(f"P3-T*-{result.task_id}"))
    assert len(packets) == 1
    promoted = cs.list_captures(packet_repo, status="promoted")
    assert promoted[0].id == cid
    assert promoted[0].task == result.task_id
    text = backlog.read_text()
    assert "### P3-T01 — Dark mode toggle" in text
    assert "- **Status:** draft" in text


def test_promote_tier_derived_from_kind(packet_repo):
    cid = cs.capture(packet_repo, "rename a var", kind="edit", today="2026-07-17")
    result = cs.promote(packet_repo, cid, phase=3)
    assert result.simple is True  # edit → simple packet


def test_promote_simple_override(packet_repo):
    cid = cs.capture(packet_repo, "big feature", kind="feature", today="2026-07-17")
    result = cs.promote(packet_repo, cid, phase=3, simple=True)
    assert result.simple is True  # explicit override wins over the feature default


def test_promote_depends_on_lands_in_backlog(packet_repo):
    backlog = packet_repo / "docs" / "working" / "backlog.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text("# Backlog\n\n## Phase 3 — Things\n")
    cid = cs.capture(packet_repo, "needs the API", today="2026-07-17")
    cs.promote(packet_repo, cid, phase=3, depends_on="P3-T01")
    assert "- **Dependencies:** P3-T01" in backlog.read_text()


def test_promote_unknown_capture_raises(packet_repo):
    with pytest.raises(cs.CaptureError):
        cs.promote(packet_repo, "CAP-9999", phase=3)


def test_promote_twice_raises(packet_repo):
    cid = cs.capture(packet_repo, "once", today="2026-07-17")
    cs.promote(packet_repo, cid, phase=3)
    with pytest.raises(cs.CaptureError):
        cs.promote(packet_repo, cid, phase=3)


def test_mcp_capture_branch(packet_repo):
    """The MCP `capture` tool (DAEMON's in-process seam) files an inbox item."""
    from grain.services.mcp_service import handle_request

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "capture", "arguments": {"title": "via mcp", "kind": "feature"}},
    }
    response = handle_request(packet_repo, request)
    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["cap_id"] == "CAP-0001"
    assert cs.list_captures(packet_repo)[0].title == "via mcp"


def test_mcp_capture_bad_kind_is_error(packet_repo):
    from grain.services.mcp_service import handle_request

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "capture", "arguments": {"title": "x", "kind": "banana"}},
    }
    result = handle_request(packet_repo, request)["result"]
    assert result["isError"] is True
