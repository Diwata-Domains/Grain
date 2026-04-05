"""Export adapter for context bundle outputs."""

from pathlib import Path

from forge.domain.context import ContextBundle


def render_context_markdown_export(root: Path, bundle: ContextBundle) -> str:
    """Render a single assembled markdown export for a ContextBundle."""
    generated_at = bundle.export_metadata.get("generated_at", "")
    sources = bundle.export_metadata.get("sources", [])

    lines: list[str] = [
        "# Context Export",
        "",
        f"Task ID: {bundle.task_id}",
        f"Generated At: {generated_at}",
        "",
        "## Sources",
    ]
    for source in sources:
        lines.append(f"- `{source}`")

    for source in sources:
        source_path = root / source
        lines.append("")
        lines.append(f"## Source: `{source}`")
        if not source_path.exists():
            lines.append("")
            lines.append("_Missing source file on disk._")
            continue
        lines.append("")
        lines.append("```md")
        lines.append(source_path.read_text(encoding="utf-8"))
        lines.append("```")

    return "\n".join(lines).strip() + "\n"


def write_context_markdown_export(
    root: Path,
    bundle: ContextBundle,
    output_path: Path | None = None,
) -> Path:
    """Write markdown export to disk and return the output path."""
    if output_path is None:
        resolved = bundle.packet_dir / "context_export.md"
    elif output_path.is_absolute():
        resolved = output_path
    else:
        resolved = root / output_path

    resolved.parent.mkdir(parents=True, exist_ok=True)
    content = render_context_markdown_export(root, bundle)
    resolved.write_text(content, encoding="utf-8")
    return resolved
