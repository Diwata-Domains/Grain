# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""PDF extraction service for docs adapter context sources."""

from __future__ import annotations

from pathlib import Path


class PdfExtractor:
    """Extract readable text from PDF documents."""

    def extract(self, path: Path) -> str:
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                if not pdf.pages:
                    return (
                        f"[pdf_extractor: {path.name} - no extractable text "
                        "(may be image-only or layout-heavy)]"
                    )

                sections: list[str] = []
                has_text = False
                for idx, page in enumerate(pdf.pages, start=1):
                    text = (page.extract_text() or "").strip()
                    if text:
                        has_text = True
                        body = text
                    else:
                        body = f"[page {idx}: no extractable text]"
                    sections.append(f"--- Page {idx} ---\n\n{body}")

                if not has_text:
                    return (
                        f"[pdf_extractor: {path.name} - no extractable text "
                        "(may be image-only or layout-heavy)]"
                    )
                return "\n\n".join(sections)
        except Exception as exc:  # noqa: BLE001 - graceful degradation required
            return f"[pdf_extractor: could not read {path.name} - {exc}]"

