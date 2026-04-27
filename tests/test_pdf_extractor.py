"""Tests for PDF extraction and docs-adapter PDF wiring."""

from __future__ import annotations

from pathlib import Path

import yaml

from grain.adapters.export import render_context_markdown_export
from grain.services.context_service import build_context_bundle
from grain.services.pdf_extractor import PdfExtractor
from grain.services.task_service import create_packet_directory


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_manifest(root: Path) -> None:
    manifest = {
        "canonical": [
            {
                "id": "workflow_spec",
                "path": "docs/canonical/workflow_spec.md",
                "purpose": "workflow",
                "authority": "highest",
                "editable_by_agents": False,
                "read_when": ["running_tasks"],
            }
        ],
        "working": [],
        "runtime": [],
        "tasks": {},
        "rules": {},
    }
    path = root / "docs" / "runtime" / "docs_manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(manifest), encoding="utf-8")
    _write(root / "docs" / "canonical" / "workflow_spec.md", "# Workflow Spec\n")


def _write_docs_adapter_profile(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### docs_adapter
- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - markdown
  - docx
  - pdf
- `relevant_file_patterns`:
  - `**/*.md`
  - `**/*.docx`
  - `**/*.pdf`
- `context_priority_rules`:
  - prioritize canonical docs first
- `test_or_validation_hints`:
  - validate key headings
""",
    )


def _set_primary_adapter(root: Path, packet_dir_name: str, adapter_id: str) -> None:
    task_md = root / "tasks" / packet_dir_name / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            f"- **Primary Adapter:** {adapter_id}",
        ),
        encoding="utf-8",
    )


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(pages: list[str | None]) -> bytes:
    objects: list[str] = []
    kids: list[str] = []

    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append("2 0 obj\n<< /Type /Pages /Count {count} /Kids [{kids}] >>\nendobj\n")
    objects.append("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    obj_id = 4
    for page_text in pages:
        page_obj = obj_id
        content_obj = obj_id + 1
        kids.append(f"{page_obj} 0 R")

        page = (
            f"{page_obj} 0 obj\n"
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj} 0 R >>\n"
            "endobj\n"
        )
        if page_text is None:
            stream_text = ""
        else:
            escaped = _escape_pdf_text(page_text)
            stream_text = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
        content = (
            f"{content_obj} 0 obj\n"
            f"<< /Length {len(stream_text.encode('latin-1'))} >>\n"
            "stream\n"
            f"{stream_text}\n"
            "endstream\n"
            "endobj\n"
        )
        objects.append(page)
        objects.append(content)
        obj_id += 2

    objects[1] = objects[1].format(count=len(pages), kids=" ".join(kids))

    data = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(data))
        data += obj.encode("latin-1")

    xref_pos = len(data)
    data += f"xref\n0 {len(offsets)}\n".encode("latin-1")
    data += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        data += f"{off:010d} 00000 n \n".encode("latin-1")
    data += (
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("latin-1")
    return data


def _write_pdf(path: Path, pages: list[str | None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_build_pdf(pages))


def test_extract_text_layer_pdf_returns_page_text(tmp_path: Path):
    path = tmp_path / "docs" / "sample.pdf"
    _write_pdf(path, ["Hello from page one"])

    text = PdfExtractor().extract(path)

    assert "--- Page 1 ---" in text
    assert "Hello from page one" in text


def test_extract_multi_page_pdf_includes_separators(tmp_path: Path):
    path = tmp_path / "docs" / "sample.pdf"
    _write_pdf(path, ["First page", "Second page"])

    text = PdfExtractor().extract(path)

    assert "--- Page 1 ---" in text
    assert "--- Page 2 ---" in text
    assert "Second page" in text


def test_extract_layout_heavy_or_no_text_pdf_returns_degradation_marker(tmp_path: Path):
    path = tmp_path / "docs" / "blank.pdf"
    _write_pdf(path, [None])

    text = PdfExtractor().extract(path)
    assert "no extractable text" in text


def test_extract_unreadable_path_returns_error_marker(tmp_path: Path):
    text = PdfExtractor().extract(tmp_path / "missing.pdf")
    assert "could not read missing.pdf" in text


def test_extract_mixed_pages_marks_no_text_pages(tmp_path: Path):
    path = tmp_path / "docs" / "mixed.pdf"
    _write_pdf(path, ["Text page", None])

    text = PdfExtractor().extract(path)
    assert "Text page" in text
    assert "[page 2: no extractable text]" in text


def test_context_bundle_selects_pdf_sources_with_docs_adapter(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_docs_adapter_profile(packet_repo)
    _write_pdf(packet_repo / "docs" / "sample.pdf", ["Context PDF"])
    create_packet_directory(packet_repo, phase=14, task_num=3)
    _set_primary_adapter(packet_repo, "P14-T03-TASK-0001", "docs_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None
    assert "docs/sample.pdf" in bundle.export_metadata["sources"]


def test_context_export_renders_pdf_extracted_text(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_docs_adapter_profile(packet_repo)
    _write_pdf(packet_repo / "docs" / "sample.pdf", ["Exported PDF Text"])
    create_packet_directory(packet_repo, phase=14, task_num=3)
    _set_primary_adapter(packet_repo, "P14-T03-TASK-0001", "docs_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)
    assert "## Source: `docs/sample.pdf`" in content
    assert "Exported PDF Text" in content


def test_corrupt_pdf_returns_error_marker(tmp_path: Path):
    path = tmp_path / "docs" / "corrupt.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"not a real pdf")

    text = PdfExtractor().extract(path)
    assert "could not read corrupt.pdf" in text

