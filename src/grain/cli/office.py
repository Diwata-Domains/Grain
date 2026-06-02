from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import CommandResult, print_result
from grain.domain.errors import GeneralError
from grain.domain.office_writes import OfficeArtifactRef, OfficeWriteRequest
from grain.domain.packets import find_packet_dir
from grain.services.docx_write_service import DocxTextReplacement, DocxWriteService
from grain.services.office_artifact_review_service import OfficeArtifactReviewService
from grain.services.spreadsheet_write_service import (
    SpreadsheetCellUpdate,
    SpreadsheetWriteService,
)


@click.group("office")
def office_group():
    """Mutate and inspect writable office artifacts through packet-safe commands."""


@office_group.group("docx")
def office_docx_group():
    """Run `.docx` office artifact commands."""


@office_group.group("spreadsheet")
def office_spreadsheet_group():
    """Run spreadsheet office artifact commands."""


@office_group.group("review")
def office_review_group():
    """Inspect persisted office review artifacts."""


@office_docx_group.command("propose")
@click.option("--source", "source_path", required=True, metavar="PATH", help="Source `.docx` path relative to repo root.")
@click.option("--replace", "replacements", multiple=True, metavar="OLD=NEW", help="Text replacement to apply. Repeat as needed.")
@click.option("--output", "output_path", default=None, metavar="PATH", help="Output path relative to repo root (default: active packet proposal path).")
@click.option("--task-id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.pass_context
def office_docx_propose(ctx, source_path, replacements, output_path, task_id):
    _run_docx_command(ctx, task_id=task_id, source_path=source_path, replacements=replacements, output_path=output_path, mode="propose")


@office_docx_group.command("export")
@click.option("--source", "source_path", required=True, metavar="PATH", help="Source `.docx` path relative to repo root.")
@click.option("--replace", "replacements", multiple=True, metavar="OLD=NEW", help="Text replacement to apply. Repeat as needed.")
@click.option("--output", "output_path", default=None, metavar="PATH", help="Output path relative to repo root (default: active packet review path).")
@click.option("--task-id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.pass_context
def office_docx_export(ctx, source_path, replacements, output_path, task_id):
    _run_docx_command(ctx, task_id=task_id, source_path=source_path, replacements=replacements, output_path=output_path, mode="export-as-new-file")


@office_spreadsheet_group.command("propose")
@click.option("--source", "source_path", required=True, metavar="PATH", help="Source spreadsheet path relative to repo root.")
@click.option("--set", "updates", multiple=True, metavar="SHEET!CELL=VALUE", help="Cell update to apply. Repeat as needed.")
@click.option("--output", "output_path", default=None, metavar="PATH", help="Output path relative to repo root (default: active packet proposal path).")
@click.option("--task-id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.pass_context
def office_spreadsheet_propose(ctx, source_path, updates, output_path, task_id):
    _run_spreadsheet_command(ctx, task_id=task_id, source_path=source_path, updates=updates, output_path=output_path, mode="propose")


@office_spreadsheet_group.command("export")
@click.option("--source", "source_path", required=True, metavar="PATH", help="Source spreadsheet path relative to repo root.")
@click.option("--set", "updates", multiple=True, metavar="SHEET!CELL=VALUE", help="Cell update to apply. Repeat as needed.")
@click.option("--output", "output_path", default=None, metavar="PATH", help="Output path relative to repo root (default: active packet review path).")
@click.option("--task-id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.pass_context
def office_spreadsheet_export(ctx, source_path, updates, output_path, task_id):
    _run_spreadsheet_command(ctx, task_id=task_id, source_path=source_path, updates=updates, output_path=output_path, mode="export-as-new-file")


@office_review_group.command("show")
@click.option("--task-id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.pass_context
def office_review_show(ctx, task_id):
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)
    resolved_task_id, packet_dir = _resolve_packet_context(root, task_id)
    review_path = packet_dir / "office_review.json"

    if not review_path.exists():
        result = CommandResult(
            ok=False,
            command="office review show",
            repo=str(root),
            task_id=resolved_task_id,
            errors=[f"office review artifact not found: {review_path.relative_to(root)}"],
        )
        if fmt == "json":
            print_result(result, fmt=fmt)
        else:
            print_result(result, fmt=fmt)
        raise GeneralError("office review show failed", detail="; ".join(result.errors))

    payload = json.loads(review_path.read_text(encoding="utf-8"))
    result = CommandResult(
        ok=True,
        command="office review show",
        repo=str(root),
        task_id=resolved_task_id,
        files_updated=[str(review_path.relative_to(root))],
    )

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["office_review"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    print_result(result, fmt=fmt)
    click.echo(f"  operation_mode   {payload['review_bundle']['operation_mode']}")
    click.echo("  artifact_paths")
    for path in payload["review_bundle"]["artifact_paths"]:
        click.echo(f"    - {path}")
    click.echo("  validator_results")
    for item in payload["validator_results"]:
        click.echo(f"    - {item['validator_id']} [{item['category']}] {item['state']}: {item['summary']}")
    click.echo("  residual_risks")
    risks = payload["review_bundle"]["residual_risks"] or ["None"]
    for risk in risks:
        click.echo(f"    - {risk}")


def _run_docx_command(ctx, *, task_id: str | None, source_path: str, replacements: tuple[str, ...], output_path: str | None, mode: str) -> None:
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)
    resolved_task_id, packet_dir = _resolve_packet_context(root, task_id)
    parsed_replacements = [_parse_docx_replacement(item) for item in replacements]
    output_rel = output_path or _default_output_path(packet_dir, source_path, mode)

    service = DocxWriteService()
    review_service = OfficeArtifactReviewService()
    write_result = service.write_document(
        root=root,
        request=OfficeWriteRequest(
            packet_id=resolved_task_id,
            artifact=OfficeArtifactRef("docx", source_path, output_path=output_rel),
            requested_mode=mode,
        ),
        replacements=parsed_replacements,
    )
    review_result = review_service.build_docx_review_result(
        root=root,
        packet_id=resolved_task_id,
        result=write_result,
    )
    review_path = _write_office_review_artifact(packet_dir, review_result)

    result = CommandResult(
        ok=True,
        command="office docx propose" if mode == "propose" else "office docx export",
        repo=str(root),
        task_id=resolved_task_id,
        status="review",
        files_created=[write_result.output_path, str(review_path.relative_to(root))],
    )
    _print_office_command(result, fmt, write_result.output_path, review_result)


def _run_spreadsheet_command(ctx, *, task_id: str | None, source_path: str, updates: tuple[str, ...], output_path: str | None, mode: str) -> None:
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)
    resolved_task_id, packet_dir = _resolve_packet_context(root, task_id)
    parsed_updates = [_parse_spreadsheet_update(item) for item in updates]
    output_rel = output_path or _default_output_path(packet_dir, source_path, mode)

    service = SpreadsheetWriteService()
    review_service = OfficeArtifactReviewService()
    write_result = service.write_workbook(
        root=root,
        request=OfficeWriteRequest(
            packet_id=resolved_task_id,
            artifact=OfficeArtifactRef("spreadsheet", source_path, output_path=output_rel),
            requested_mode=mode,
        ),
        updates=parsed_updates,
    )
    review_result = review_service.build_spreadsheet_review_result(
        root=root,
        packet_id=resolved_task_id,
        result=write_result,
    )
    review_path = _write_office_review_artifact(packet_dir, review_result)

    result = CommandResult(
        ok=True,
        command="office spreadsheet propose" if mode == "propose" else "office spreadsheet export",
        repo=str(root),
        task_id=resolved_task_id,
        status="review",
        files_created=[write_result.output_path, str(review_path.relative_to(root))],
    )
    _print_office_command(result, fmt, write_result.output_path, review_result)


def _print_office_command(result: CommandResult, fmt: str, output_path: str, review_result) -> None:
    if fmt == "json":
        data = dataclasses.asdict(result)
        data["output_path"] = output_path
        data["office_review"] = dataclasses.asdict(review_result)
        click.echo(json.dumps(data, indent=2))
        return

    print_result(result, fmt=fmt)
    click.echo(f"  output_path      {output_path}")
    click.echo(f"  operation_mode   {review_result.review_bundle.operation_mode}")
    click.echo("  validator_results")
    for item in review_result.validator_results:
        click.echo(f"    - {item.validator_id} [{item.category}] {item.state}: {item.summary}")
    click.echo("  residual_risks")
    risks = review_result.review_bundle.residual_risks or ["None"]
    for risk in risks:
        click.echo(f"    - {risk}")


def _resolve_packet_context(root: Path, task_id: str | None) -> tuple[str, Path]:
    resolved_task_id = task_id or _read_active_task_id(root)
    if not resolved_task_id or resolved_task_id == "none":
        raise GeneralError("office command requires an active or explicit task", detail="set docs/working/current_task.md or pass --task-id")
    packet_dir = find_packet_dir(root / "tasks", resolved_task_id)
    if packet_dir is None:
        raise GeneralError("office command failed", detail=f"packet '{resolved_task_id}' not found")
    return resolved_task_id, packet_dir


def _read_active_task_id(root: Path) -> str:
    current_task_path = root / "docs" / "working" / "current_task.md"
    if not current_task_path.exists():
        return ""
    for line in current_task_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID:"):
            return line.split(":", 1)[1].strip()
    return ""


def _default_output_path(packet_dir: Path, source_path: str, mode: str) -> str:
    source = Path(source_path)
    suffix = ".proposed" if mode == "propose" else ".review"
    name = f"{source.stem}{suffix}{source.suffix}"
    return str((packet_dir / name).relative_to(packet_dir.parent.parent))


def _parse_docx_replacement(raw: str) -> DocxTextReplacement:
    if "=" not in raw:
        raise click.UsageError("replacement must use OLD=NEW format")
    old, new = raw.split("=", 1)
    return DocxTextReplacement(old, new)


def _parse_spreadsheet_update(raw: str) -> SpreadsheetCellUpdate:
    if "!" not in raw or "=" not in raw:
        raise click.UsageError("update must use SHEET!CELL=VALUE format")
    location, value = raw.split("=", 1)
    sheet_name, cell_ref = location.split("!", 1)
    return SpreadsheetCellUpdate(sheet_name, cell_ref, _coerce_value(value))


def _coerce_value(raw: str):
    stripped = raw.strip()
    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if stripped.isdigit() or (stripped.startswith("-") and stripped[1:].isdigit()):
        return int(stripped)
    try:
        if "." in stripped:
            return float(stripped)
    except ValueError:
        pass
    return stripped


def _write_office_review_artifact(packet_dir: Path, review_result) -> Path:
    path = packet_dir / "office_review.json"
    path.write_text(json.dumps(dataclasses.asdict(review_result), indent=2), encoding="utf-8")
    return path
