"""Tests for spreadsheet extraction and context export wiring."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml
from openpyxl import Workbook

from grain.adapters.export import render_context_markdown_export
from grain.services.context_service import build_context_bundle
from grain.services.spreadsheet_extractor import SpreadsheetExtractor
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


def _write_spreadsheet_adapter_profile(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### spreadsheet_adapter
- `adapter_id`: `spreadsheet_adapter`
- `domain_type`: `data`
- `applies_to`:
  - spreadsheets
- `relevant_file_patterns`:
  - `**/*.xlsx`
  - `**/*.xls`
  - `**/*.csv`
- `context_priority_rules`:
  - prioritize sheets with explicit headers first
- `test_or_validation_hints`:
  - confirm header and row-count expectations
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


def _create_xlsx(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Revenue"
    ws.append(["month", "amount"])
    ws.append(["Jan", 12])
    ws.append(["Feb", 30])
    wb.save(path)


def _create_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["region", "sales"])
        writer.writerow(["east", "10"])
        writer.writerow(["west", "14"])


def test_extract_xlsx_includes_sheet_headers_and_rows(tmp_path: Path):
    sheet = tmp_path / "data" / "report.xlsx"
    _create_xlsx(sheet)

    text = SpreadsheetExtractor().extract(sheet)

    assert "# Spreadsheet: report.xlsx" in text
    assert "## Sheet: Revenue" in text
    assert "- Columns: month, amount" in text
    assert "1. Jan, 12" in text


def test_extract_csv_includes_headers_and_rows(tmp_path: Path):
    sheet = tmp_path / "data" / "report.csv"
    _create_csv(sheet)

    text = SpreadsheetExtractor().extract(sheet)

    assert "# Spreadsheet: report.csv" in text
    assert "## Sheet: CSV" in text
    assert "- Columns: region, sales" in text
    assert "1. east, 10" in text


def test_extract_empty_csv_returns_empty_marker(tmp_path: Path):
    path = tmp_path / "data" / "empty.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")

    text = SpreadsheetExtractor().extract(path)
    assert "is empty" in text


def test_extract_unreadable_csv_returns_warning(tmp_path: Path):
    text = SpreadsheetExtractor().extract(tmp_path / "missing.csv")
    assert "could not read missing.csv" in text


def test_extract_xls_returns_graceful_warning_when_unreadable(tmp_path: Path):
    path = tmp_path / "legacy.xls"
    path.write_text("not-a-real-binary-xls", encoding="utf-8")

    text = SpreadsheetExtractor().extract(path)
    assert "could not read legacy.xls" in text


def test_context_bundle_selects_spreadsheet_sources_with_adapter(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_spreadsheet_adapter_profile(packet_repo)
    _create_csv(packet_repo / "data" / "table.csv")
    _create_xlsx(packet_repo / "data" / "table.xlsx")
    create_packet_directory(packet_repo, phase=14, task_num=1)
    _set_primary_adapter(packet_repo, "P14-T01-TASK-0001", "spreadsheet_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    sources = bundle.export_metadata["sources"]
    assert "data/table.csv" in sources
    assert "data/table.xlsx" in sources
    adapter_context = bundle.export_metadata["adapter_context"]
    assert adapter_context["primary_adapter"] == "spreadsheet_adapter"
    assert adapter_context["applied"] is True


def test_context_export_renders_extracted_csv_content(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_spreadsheet_adapter_profile(packet_repo)
    _create_csv(packet_repo / "data" / "table.csv")
    create_packet_directory(packet_repo, phase=14, task_num=1)
    _set_primary_adapter(packet_repo, "P14-T01-TASK-0001", "spreadsheet_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)
    assert "## Source: `data/table.csv`" in content
    assert "Columns: region, sales" in content
    assert "east, 10" in content


def test_context_export_renders_extracted_xlsx_content(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_spreadsheet_adapter_profile(packet_repo)
    _create_xlsx(packet_repo / "data" / "table.xlsx")
    create_packet_directory(packet_repo, phase=14, task_num=1)
    _set_primary_adapter(packet_repo, "P14-T01-TASK-0001", "spreadsheet_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)
    assert "## Source: `data/table.xlsx`" in content
    assert "## Sheet: Revenue" in content
    assert "Jan, 12" in content

