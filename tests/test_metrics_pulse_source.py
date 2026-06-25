"""Tests for ``grain metrics --source pulse`` (Pulse readback, P3-T04).

The HTTP GET is mocked end-to-end — these tests never hit a real Pulse. They
assert: (1) ``--source pulse`` renders Pulse-returned phases/stop-reasons in both
text and JSON; (2) a clear, non-zero error (no stack trace) when the endpoint is
unset or unreachable; (3) endpoint resolution from both env vars; (4) the default
``--source local`` path is byte-identical to today.
"""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest
from click.testing import CliRunner

from grain.cli import main
from grain.services import pulse_readback

# ── Pulse-shaped fixtures (match pulse.services.metrics_service shapes) ──────────

_PHASES_DOC = {
    "since": None,
    "phase_count": 2,
    "total_tasks_done": 16,
    "unsupported_versions": 0,
    "phases": [
        {
            "phase": "5",
            "closes": 1,
            "tasks_done": 9,
            "task_closes": 9,
            "first_closed_at": "2026-01-10T00:00:00+00:00",
            "last_closed_at": "2026-01-10T00:00:00+00:00",
        },
        {
            "phase": "6",
            "closes": 1,
            "tasks_done": 7,
            "task_closes": 7,
            "first_closed_at": "2026-01-20T00:00:00+00:00",
            "last_closed_at": "2026-01-20T00:00:00+00:00",
        },
    ],
}

_STOP_DOC = {
    "since": None,
    "total": 3,
    "unsupported_versions": 0,
    "stop_reasons": [
        {"reason": "packet_required", "count": 2},
        {"reason": "clean_tree", "count": 1},
    ],
}


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _fake_urlopen(by_path: dict[str, dict]):
    """Build a urlopen replacement that returns canned JSON keyed by URL suffix."""

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.close()
            return False

    def _open(request, timeout=None):  # noqa: ARG001 — signature must match urlopen
        url = request.full_url
        for suffix, doc in by_path.items():
            if url.endswith(suffix):
                return _Resp(json.dumps(doc).encode("utf-8"))
        raise AssertionError(f"unexpected URL requested: {url}")

    return _open


@pytest.fixture
def pulse_ok(monkeypatch):
    """Point at a Pulse endpoint and stub the GETs with the canned docs."""
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://127.0.0.1:8006")
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        _fake_urlopen({
            "/v1/metrics/phases": _PHASES_DOC,
            "/v1/metrics/stop-reasons": _STOP_DOC,
        }),
    )


# ── Endpoint resolution ──────────────────────────────────────────────────────────

def test_resolve_endpoint_prefers_dedicated_var(monkeypatch):
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://pulse.local:8006/")
    monkeypatch.setenv("GRAIN_TELEMETRY_ENDPOINT", "http://other:9/v1/events")
    assert pulse_readback.resolve_endpoint() == "http://pulse.local:8006"


def test_resolve_endpoint_derives_from_telemetry(monkeypatch):
    monkeypatch.delenv("GRAIN_PULSE_ENDPOINT", raising=False)
    monkeypatch.setenv("GRAIN_TELEMETRY_ENDPOINT", "http://127.0.0.1:8006/v1/events")
    assert pulse_readback.resolve_endpoint() == "http://127.0.0.1:8006"


def test_resolve_endpoint_none_when_unset(monkeypatch):
    monkeypatch.delenv("GRAIN_PULSE_ENDPOINT", raising=False)
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)
    assert pulse_readback.resolve_endpoint() is None


# ── Pulse readback rendering (text + JSON) ──────────────────────────────────────

def test_pulse_summary_text(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse")
    assert result.exit_code == 0, result.output
    assert "grain metrics" in result.output
    assert "phases        2" in result.output
    assert "tasks_done    16" in result.output
    # Stop reasons from Pulse render through the same block.
    assert "packet_required" in result.output
    assert "clean_tree" in result.output
    # Phase rows show the Pulse-derived closed-at dates.
    assert "2026-01-10" in result.output
    assert "2026-01-20" in result.output
    # The source note flags this as the cross-machine view.
    assert "source: pulse" in result.output


def test_pulse_summary_json(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["phase_count"] == 2
    assert data["total_tasks_done"] == 16
    assert {"reason": "packet_required", "count": 2} in data["stop_reasons"]
    phases = {p["phase"]: p for p in data["phases"]}
    assert phases[6]["tasks_done"] == 7
    assert phases[6]["closed_at"] == "2026-01-20T00:00:00+00:00"
    # Pulse has no backlog totals / version → these stay empty, coverage partial.
    assert phases[6]["tasks_total"] is None
    assert phases[6]["closure_rate"] is None
    assert phases[6]["coverage"] == "partial"


def test_pulse_single_phase_detail_text(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse", "--phase", "6")
    assert result.exit_code == 0, result.output
    assert "phase 6" in result.output
    assert "tasks_done    7" in result.output


def test_pulse_single_phase_json(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse", "--phase", "6", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["phase"] == 6
    assert data["tasks_done"] == 7


def test_pulse_phase_not_found_json(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse", "--phase", "99", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["phase"] == 99


def test_pulse_phase_not_found_text_exits_two(tmp_path, pulse_ok):
    result = _run(tmp_path, "metrics", "--source", "pulse", "--phase", "99")
    assert result.exit_code == 2, result.output


# ── Clear errors (no stack trace, non-zero, local path untouched) ───────────────

def test_pulse_unconfigured_endpoint_errors_cleanly(tmp_path, monkeypatch):
    monkeypatch.delenv("GRAIN_PULSE_ENDPOINT", raising=False)
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)
    result = _run(tmp_path, "metrics", "--source", "pulse")
    assert result.exit_code != 0
    assert "no Pulse endpoint configured" in result.output
    assert "GRAIN_PULSE_ENDPOINT" in result.output
    # No stack trace leaked.
    assert "Traceback" not in result.output


def test_pulse_unreachable_errors_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://127.0.0.1:8006")
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)

    def _boom(request, timeout=None):  # noqa: ARG001
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    result = _run(tmp_path, "metrics", "--source", "pulse")
    assert result.exit_code != 0
    assert "could not reach Pulse" in result.output
    assert "Traceback" not in result.output


def test_pulse_http_error_errors_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://127.0.0.1:8006")
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)

    def _http_500(request, timeout=None):  # noqa: ARG001
        raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", _http_500)
    result = _run(tmp_path, "metrics", "--source", "pulse")
    assert result.exit_code != 0
    assert "HTTP 500" in result.output
    assert "Traceback" not in result.output


def test_pulse_bad_json_errors_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://127.0.0.1:8006")
    monkeypatch.delenv("GRAIN_TELEMETRY_ENDPOINT", raising=False)

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.close()
            return False

    def _garbage(request, timeout=None):  # noqa: ARG001
        return _Resp(b"<html>not json</html>")

    monkeypatch.setattr(urllib.request, "urlopen", _garbage)
    result = _run(tmp_path, "metrics", "--source", "pulse")
    assert result.exit_code != 0
    assert "not valid JSON" in result.output
    assert "Traceback" not in result.output


# ── Default local path is unchanged ──────────────────────────────────────────────

def _seed_local(tmp_path: Path) -> None:
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    _write(
        tmp_path / "docs/archive/phases/phase-5/metadata.json",
        json.dumps({"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"}),
    )
    _write(
        tmp_path / "docs/archive/phases/phase-6/metadata.json",
        json.dumps({"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"}),
    )
    _write(
        tmp_path / ".grain/last_workflow_state.json",
        json.dumps({"evaluation": {"stop_reason": "packet_required"}}),
    )


def test_explicit_source_local_matches_default(tmp_path, monkeypatch):
    # Even with a Pulse endpoint configured, --source local (and the default) must
    # never touch the network and must be byte-identical to each other.
    monkeypatch.setenv("GRAIN_PULSE_ENDPOINT", "http://127.0.0.1:8006")

    def _no_network(*args, **kwargs):
        raise AssertionError("local path must not perform any HTTP request")

    monkeypatch.setattr(urllib.request, "urlopen", _no_network)
    _seed_local(tmp_path)

    # --no-cache so neither run is served the cache the other wrote (same repo).
    default_out = _run(tmp_path, "metrics", "--no-cache", fmt="json").output
    explicit_out = _run(tmp_path, "metrics", "--source", "local", "--no-cache", fmt="json").output
    assert default_out == explicit_out
    data = json.loads(default_out)
    assert data["phase_count"] == 2
    assert data["total_tasks_done"] == 16


def test_invalid_source_rejected(tmp_path):
    result = _run(tmp_path, "metrics", "--source", "nope")
    assert result.exit_code != 0
    assert "Invalid value" in result.output or "nope" in result.output
