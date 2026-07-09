# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for `grain intake pull` — importing promoted Assay tickets as task packets.

Assay (a separate service) exposes ``GET /promotions`` and
``POST /promotions/{vid}/ack`` guarded by an ``X-Assay-Key`` header. HTTP is
funneled through the injectable ``intake_service._urllib_get`` /
``_urllib_post`` module functions (same pattern as ``github_service``'s
``_urllib_post``), so tests monkeypatch those rather than touching the network
or pulling in a new HTTP-mocking dependency.
"""

from __future__ import annotations

import json
import re

from click.testing import CliRunner

from grain.cli import main
from grain.services import intake_service, task_service

_PROMOTION_V1 = {
    "verification_id": "v1",
    "url": "https://x.test",
    "summary": "Button broken",
    "severity": "error",
    "priority": "high",
    "user_comment": "cant click",
    "kind": "report",
    "screenshot_ref": "/out/v1.png",
    "remediation": "fix handler",
}


def _fake_get(promotions):
    captured = {}

    def fake(url, headers):
        captured["get_url"] = url
        captured["get_headers"] = dict(headers)
        return {"promotions": promotions}

    return fake, captured


def _fake_post():
    captured = {"post_calls": []}

    def fake(url, headers):
        captured["post_calls"].append(url)
        captured["post_headers"] = dict(headers)
        return {"ok": True}

    return fake, captured


def _set_env(monkeypatch):
    monkeypatch.setenv("GRAIN_ASSAY_ENDPOINT", "https://assay.test")
    monkeypatch.setenv("GRAIN_ASSAY_KEY", "k")


# ── pull creates a packet + acks ───────────────────────────────────────────────

def test_pull_creates_packet_and_acks(packet_repo, monkeypatch):
    root = packet_repo
    _set_env(monkeypatch)

    get_fake, get_captured = _fake_get([_PROMOTION_V1])
    post_fake, post_captured = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    result = CliRunner().invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])
    assert result.exit_code == 0, result.output

    packets = list((root / "tasks").glob("P20-*-TASK-*"))
    assert len(packets) == 1
    task_md = (packets[0] / "task.md").read_text(encoding="utf-8")
    assert "assay_vid: v1" in task_md
    assert "Button broken" in task_md
    assert "Reported: cant click" in task_md
    assert "Remediation: fix handler" in task_md
    assert "Screenshot: /out/v1.png" in task_md

    assert get_captured["get_url"] == "https://assay.test/promotions"
    assert get_captured["get_headers"]["X-Assay-Key"] == "k"
    assert post_captured["post_calls"] == ["https://assay.test/promotions/v1/ack"]
    assert post_captured["post_headers"]["X-Assay-Key"] == "k"


def test_pull_json_output_reports_imported_ticket(packet_repo, monkeypatch):
    root = packet_repo
    _set_env(monkeypatch)
    get_fake, _ = _fake_get([_PROMOTION_V1])
    post_fake, _ = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    result = CliRunner().invoke(
        main, ["--repo", str(root), "--format", "json", "intake", "pull", "--phase", "20"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["imported"][0]["assay_vid"] == "v1"
    assert data["imported"][0]["task_id"] == "TASK-0001"


# ── idempotency by assay_vid ───────────────────────────────────────────────────

def test_pull_is_idempotent_by_assay_vid(packet_repo, monkeypatch):
    root = packet_repo
    _set_env(monkeypatch)
    get_fake, _ = _fake_get([_PROMOTION_V1])
    post_fake, post_captured = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    runner = CliRunner()
    first = runner.invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])
    assert first.exit_code == 0, first.output
    assert len(list((root / "tasks").glob("P20-*-TASK-*"))) == 1

    second = runner.invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])
    assert second.exit_code == 0, second.output
    assert len(list((root / "tasks").glob("P20-*-TASK-*"))) == 1  # no duplicate

    # No second packet is created for the dedup-skipped vid, but the ack is
    # retried on every pull that still sees it as `promoted` — it's the only
    # way a ticket whose first ack silently failed ever gets un-stuck.
    assert post_captured["post_calls"] == [
        "https://assay.test/promotions/v1/ack",
        "https://assay.test/promotions/v1/ack",
    ]


def test_pull_reconciles_stuck_ack_on_dedup_skip(packet_repo, monkeypatch):
    """A ticket whose packet exists but whose first ack failed (network/5xx)
    must not be stuck forever: the *next* pull still sees it via GET
    /promotions (Assay only stops returning it once acked) and must retry the
    ack for that already-on-disk vid, without minting a second packet.
    """
    root = packet_repo
    _set_env(monkeypatch)
    get_fake, _ = _fake_get([_PROMOTION_V1])
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)

    # First pull: ack fails outright (simulating a network/5xx error).
    failing_post_calls = []

    def failing_post(url, headers):
        failing_post_calls.append(url)
        raise OSError("simulated network failure")

    monkeypatch.setattr(intake_service, "_urllib_post", failing_post)

    runner = CliRunner()
    first = runner.invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])
    assert first.exit_code != 0  # the ack failure surfaces as a failed run
    packets = list((root / "tasks").glob("P20-*-TASK-*"))
    assert len(packets) == 1  # the packet was still created on disk
    assert failing_post_calls == ["https://assay.test/promotions/v1/ack"]

    # Second pull: same ticket still comes back from GET /promotions (Assay
    # never saw a successful ack, so it's still `promoted`); this time the
    # ack succeeds.
    post_fake, post_captured = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    second = runner.invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])
    assert second.exit_code == 0, second.output

    # No duplicate packet was minted for the dedup-skipped vid...
    packets = list((root / "tasks").glob("P20-*-TASK-*"))
    assert len(packets) == 1
    # ...but the ack WAS retried (reconciled) on this second run.
    assert post_captured["post_calls"] == ["https://assay.test/promotions/v1/ack"]


# ── multiple tickets in one pull increment task_num ────────────────────────────

def test_pull_multiple_tickets_increment_task_num(packet_repo, monkeypatch):
    root = packet_repo
    _set_env(monkeypatch)
    ticket2 = dict(_PROMOTION_V1, verification_id="v2", summary="Second issue")
    get_fake, _ = _fake_get([_PROMOTION_V1, ticket2])
    post_fake, post_captured = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    result = CliRunner().invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "5"])
    assert result.exit_code == 0, result.output

    packets = sorted((root / "tasks").glob("P5-*-TASK-*"))
    assert len(packets) == 2
    assert "P5-T01-" in packets[0].name
    assert "P5-T02-" in packets[1].name
    assert len(post_captured["post_calls"]) == 2


# ── missing env vars fail clearly ──────────────────────────────────────────────

def test_pull_missing_endpoint_env_fails_clearly(packet_repo, monkeypatch):
    monkeypatch.delenv("GRAIN_ASSAY_ENDPOINT", raising=False)
    monkeypatch.delenv("GRAIN_ASSAY_KEY", raising=False)

    result = CliRunner().invoke(main, ["--repo", str(packet_repo), "intake", "pull", "--phase", "20"])
    assert result.exit_code != 0
    combined = str(result.output) + str(result.exception)
    assert "GRAIN_ASSAY_ENDPOINT" in combined


def test_pull_missing_key_env_fails_clearly(packet_repo, monkeypatch):
    monkeypatch.setenv("GRAIN_ASSAY_ENDPOINT", "https://assay.test")
    monkeypatch.delenv("GRAIN_ASSAY_KEY", raising=False)

    result = CliRunner().invoke(main, ["--repo", str(packet_repo), "intake", "pull", "--phase", "20"])
    assert result.exit_code != 0
    combined = str(result.output) + str(result.exception)
    assert "GRAIN_ASSAY_KEY" in combined


# ── seeded packet still passes `grain task validate` ───────────────────────────

def test_seeded_packet_passes_task_validate(packet_repo, monkeypatch):
    root = packet_repo
    _set_env(monkeypatch)
    get_fake, _ = _fake_get([_PROMOTION_V1])
    post_fake, _ = _fake_post()
    monkeypatch.setattr(intake_service, "_urllib_get", get_fake)
    monkeypatch.setattr(intake_service, "_urllib_post", post_fake)

    CliRunner().invoke(main, ["--repo", str(root), "intake", "pull", "--phase", "20"])

    packet_dir = next((root / "tasks").glob("P20-*-TASK-*"))
    task_id = re.search(r"(TASK-\d{4})", packet_dir.name).group(1)

    validate_result = task_service.validate_one_packet(root, task_id)
    assert validate_result.ok, validate_result.errors

    cli_result = CliRunner().invoke(
        main, ["--repo", str(root), "task", "validate", "--id", task_id]
    )
    assert cli_result.exit_code == 0, cli_result.output
