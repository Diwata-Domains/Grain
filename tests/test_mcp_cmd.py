from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.mcp_service import MCP_PROTOCOL_VERSION, handle_request, serve_stdio


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo: Path) -> None:
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        (
            "# Current Focus\n\n"
            "## Current Phase\n"
            "Phase 24 — Desktop Integrations and Obsidian Support\n\n"
            "Phase 23 closed: 2026-05-05 — 6 tasks done (grain-verified)\n"
        ),
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )


def _ready_backlog(repo: Path) -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 27. Phase 24 — Desktop Integrations and Obsidian Support\n\n"
            "### P24-T01 — Local MCP wrapper scaffold for desktop invocation\n"
            "- **Status:** ready\n"
        ),
    )


def test_mcp_manifest_reports_local_stdio_config(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "mcp", "manifest"])
    assert result.exit_code == 0, result.output
    assert "mcp manifest: ok" in result.output
    assert "grain" in result.output
    assert "mcp" in result.output
    assert "serve" in result.output


def test_mcp_manifest_json_output(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "--format", "json", "mcp", "manifest"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mcpServers"]["grain"]["command"] == "grain"
    assert payload["mcpServers"]["grain"]["args"][-1] == str(tmp_path)


def test_mcp_initialize_and_list_tools(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    init = handle_request(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        },
    )
    assert init is not None
    assert init["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
    assert init["result"]["capabilities"]["tools"]["listChanged"] is False

    listed = handle_request(tmp_path, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert listed is not None
    tool_names = [tool["name"] for tool in listed["result"]["tools"]]
    assert tool_names == ["workflow_next", "prompt_show", "review_summary", "office_review_show"]


def test_mcp_workflow_next_tool_returns_structured_content(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)

    response = handle_request(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "workflow_next", "arguments": {}},
        },
    )

    assert response is not None
    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["evaluation"]["next_action"] == "task_execute"
    assert result["structuredContent"]["evaluation"]["candidate_tasks"][0]["task_ref"] == "P24-T01"


def test_mcp_prompt_show_tool_returns_recommended_prompt(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    _write(tmp_path / "prompts" / "task.execute.md", "# Execute\n")

    response = handle_request(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "prompt_show", "arguments": {}},
        },
    )

    assert response is not None
    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["prompt"]["recommended_prompt"] == "prompts/task.execute.md"


def test_mcp_serve_stdio_handles_initialize_and_tool_call(tmp_path: Path) -> None:
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)

    request_stream = StringIO(
        "\n".join(
            [
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": MCP_PROTOCOL_VERSION,
                            "capabilities": {},
                            "clientInfo": {"name": "test-client", "version": "1.0"},
                        },
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": "workflow_next", "arguments": {}},
                    }
                ),
            ]
        )
        + "\n"
    )
    output_stream = StringIO()

    serve_stdio(tmp_path, stdin=request_stream, stdout=output_stream, stderr=StringIO())

    lines = [json.loads(line) for line in output_stream.getvalue().splitlines()]
    assert len(lines) == 2
    assert lines[0]["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
    assert lines[1]["result"]["structuredContent"]["evaluation"]["next_action"] == "task_execute"
