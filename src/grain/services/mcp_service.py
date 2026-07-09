# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Thin local MCP wrapper over existing Grain read-oriented services."""

from __future__ import annotations

import dataclasses
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from grain.domain.packets import find_packet_dir

MCP_PROTOCOL_VERSION = "2025-06-18"
MCP_SERVER_INFO = {"name": "grain", "version": "0.3.0-dev"}


@dataclass(frozen=True)
class McpTool:
    name: str
    title: str
    description: str
    input_schema: dict


TOOLS: tuple[McpTool, ...] = (
    McpTool(
        name="workflow_next",
        title="Workflow Next",
        description="Return Grain's next legal workflow action and blockers for the current repository state.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    McpTool(
        name="prompt_show",
        title="Prompt Show",
        description="Return the recommended Grain prompt entrypoint for the current workflow state.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    McpTool(
        name="review_summary",
        title="Review Summary",
        description="Return the structured review summary for a Grain task packet.",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Packet ID in TASK-#### form.",
                }
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    ),
    McpTool(
        name="office_review_show",
        title="Office Review Show",
        description="Read the persisted office review artifact for a Grain task packet.",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Packet ID in TASK-#### form.",
                }
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    ),
    McpTool(
        name="create_task",
        title="Create Task",
        description=(
            "Create a new Grain task packet: allocate the next TASK-#### id and scaffold the "
            "packet files. A write action — callers should confirm before invoking."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "phase": {"type": "integer", "description": "Phase number (e.g. 3)."},
                "task_num": {"type": "integer", "description": "Task number within the phase (e.g. 4)."},
                "title": {"type": "string", "description": "Task title (optional)."},
                "simple": {
                    "type": "boolean",
                    "description": "Minimal packet: task.md + results.md only.",
                    "default": False,
                },
            },
            "required": ["phase", "task_num"],
            "additionalProperties": False,
        },
    ),
)


def build_manifest(repo_root: Path, server_name: str = "grain") -> dict:
    return {
        "mcpServers": {
            server_name: {
                "command": "grain",
                "args": ["mcp", "serve", "--repo", str(repo_root)],
            }
        }
    }


def serve_stdio(root: Path, stdin: TextIO | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> None:
    in_stream = stdin or sys.stdin
    out_stream = stdout or sys.stdout
    err_stream = stderr or sys.stderr

    for raw_line in in_stream:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_response(
                out_stream,
                _error_response(None, -32700, f"invalid JSON: {exc.msg}"),
            )
            continue

        responses = _handle_payload(root, payload, err_stream)
        for response in responses:
            if response is not None:
                _write_response(out_stream, response)


def _handle_payload(root: Path, payload: object, err_stream: TextIO) -> list[dict | None]:
    if isinstance(payload, list):
        responses: list[dict | None] = []
        for item in payload:
            responses.append(handle_request(root, item, err_stream))
        return responses
    return [handle_request(root, payload, err_stream)]


def handle_request(root: Path, request: object, err_stream: TextIO | None = None) -> dict | None:
    if not isinstance(request, dict):
        return _error_response(None, -32600, "request must be a JSON object")

    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    if not isinstance(method, str):
        return _error_response(request_id, -32600, "request method must be a string")
    if not isinstance(params, dict):
        return _error_response(request_id, -32602, "request params must be an object")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": MCP_SERVER_INFO,
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": tool.name,
                        "title": tool.title,
                        "description": tool.description,
                        "inputSchema": tool.input_schema,
                    }
                    for tool in TOOLS
                ]
            },
        }

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str):
            return _error_response(request_id, -32602, "tools/call requires a string tool name")
        if not isinstance(arguments, dict):
            return _error_response(request_id, -32602, "tools/call arguments must be an object")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": _call_tool(root, name, arguments),
        }

    if err_stream is not None:
        err_stream.write(f"Unsupported MCP method: {method}\n")
    return _error_response(request_id, -32601, f"method not found: {method}")


def _call_tool(root: Path, name: str, arguments: dict) -> dict:
    try:
        if name == "workflow_next":
            from grain.services.workflow_service import evaluate_workflow_state, evaluation_to_dict

            result, evaluation = evaluate_workflow_state(root)
            if evaluation is None:
                return _tool_error({"errors": result.errors or ["workflow evaluation failed"]})
            payload = {"ok": evaluation.ok, "evaluation": evaluation_to_dict(evaluation)}
            return _tool_success(payload)

        if name == "prompt_show":
            from grain.services.prompt_service import show_prompt

            result, payload = show_prompt(root)
            if payload is None:
                return _tool_error({"errors": result.errors or ["prompt resolution failed"]})
            return _tool_success({"ok": result.ok, "prompt": payload})

        if name == "review_summary":
            from grain.services.review_service import build_packet_review_summary

            task_id = _required_task_id(arguments)
            result, summary = build_packet_review_summary(root, task_id)
            if summary is None:
                return _tool_error({"errors": result.errors or [f"packet '{task_id}' not found"]})
            payload = dataclasses.asdict(result)
            summary_payload = dataclasses.asdict(summary)
            summary_payload["packet_dir"] = str(summary.packet_dir)
            payload["summary"] = summary_payload
            return _tool_success(payload)

        if name == "office_review_show":
            task_id = _required_task_id(arguments)
            packet_dir = find_packet_dir(root / "tasks", task_id)
            if packet_dir is None:
                return _tool_error({"errors": [f"packet '{task_id}' not found"]})
            review_path = packet_dir / "office_review.json"
            if not review_path.exists():
                return _tool_error({"errors": [f"office review artifact not found: {review_path.relative_to(root)}"]})
            payload = json.loads(review_path.read_text(encoding="utf-8"))
            return _tool_success(
                {
                    "task_id": task_id,
                    "review_path": str(review_path.relative_to(root)),
                    "office_review": payload,
                }
            )

        if name == "create_task":
            from grain.services.task_service import create_packet_directory

            phase = arguments.get("phase")
            task_num = arguments.get("task_num")
            if not isinstance(phase, int) or isinstance(phase, bool):
                raise ValueError("create_task requires an integer 'phase'")
            if not isinstance(task_num, int) or isinstance(task_num, bool):
                raise ValueError("create_task requires an integer 'task_num'")
            title = arguments.get("title") or ""
            simple = bool(arguments.get("simple", False))
            result = create_packet_directory(root, phase, task_num, title=title, simple=simple)
            if not result.ok:
                return _tool_error({"errors": result.errors or ["task creation failed"]})
            return _tool_success(
                {
                    "ok": True,
                    "task_id": result.task_id,
                    "packet_dir": result.files_created[0] if result.files_created else "",
                    "files_created": result.files_created,
                }
            )
    except ValueError as exc:
        return _tool_error({"errors": [str(exc)]})

    return _tool_error({"errors": [f"unknown tool: {name}"]})


def _required_task_id(arguments: dict) -> str:
    task_id = arguments.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    return task_id.strip()


def _tool_success(payload: dict) -> dict:
    text = json.dumps(payload, indent=2, sort_keys=True)
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": payload,
        "isError": False,
    }


def _tool_error(payload: dict) -> dict:
    text = json.dumps(payload, indent=2, sort_keys=True)
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": payload,
        "isError": True,
    }


def _error_response(request_id: object, code: int, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _write_response(stream: TextIO, payload: dict) -> None:
    stream.write(json.dumps(payload, separators=(",", ":")) + "\n")
    stream.flush()
