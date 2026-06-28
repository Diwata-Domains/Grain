# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Jupyter notebook extraction service for code adapter context assembly."""

from __future__ import annotations

import json
from pathlib import Path


class NotebookExtractor:
    """Extract readable text from Jupyter notebook (.ipynb) files."""

    def extract(self, path: Path) -> str:
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception as exc:  # noqa: BLE001 - graceful degradation required
            return f"[notebook_extractor: could not read {path.name} - {exc}]"

        cells = data.get("cells", [])
        if not cells:
            return f"[notebook_extractor: {path.name} is empty]"

        lines: list[str] = [f"# Notebook: {path.name}"]
        has_content = False

        for index, cell in enumerate(cells, start=1):
            cell_type = cell.get("cell_type", "unknown")
            source = self._join_source(cell.get("source", []))
            if not source.strip():
                continue

            has_content = True
            if cell_type == "markdown":
                lines.append("")
                lines.append(source)
            elif cell_type == "code":
                lines.append("")
                lines.append(f"## Cell {index} [code]")
                lines.append("```python")
                lines.append(source)
                lines.append("```")
                outputs = self._extract_outputs(cell.get("outputs", []))
                if outputs:
                    lines.append("")
                    lines.append("**Output:**")
                    lines.append("```")
                    lines.append(outputs)
                    lines.append("```")
            elif cell_type == "raw":
                lines.append("")
                lines.append(f"## Cell {index} [raw]")
                lines.append(source)

        if not has_content:
            return f"[notebook_extractor: {path.name} is empty]"
        return "\n".join(lines)

    def _join_source(self, source: object) -> str:
        if isinstance(source, list):
            return "".join(str(s) for s in source)
        return str(source) if source else ""

    def _extract_outputs(self, outputs: list) -> str:
        parts: list[str] = []
        for output in outputs:
            output_type = output.get("output_type", "")
            if output_type == "stream":
                text = output.get("text", [])
                parts.append(self._join_source(text).strip())
            elif output_type in {"execute_result", "display_data"}:
                data = output.get("data", {})
                text = data.get("text/plain", [])
                if text:
                    parts.append(self._join_source(text).strip())
            elif output_type == "error":
                ename = output.get("ename", "")
                evalue = output.get("evalue", "")
                parts.append(f"{ename}: {evalue}")
        return "\n".join(p for p in parts if p)
