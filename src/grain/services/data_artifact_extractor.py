# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Metadata-only extraction service for data and model artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


class DataArtifactExtractor:
    """Render deterministic metadata summaries for data and model artifact files."""

    _DATASET_TYPES = {
        ".parquet": "parquet dataset",
        ".feather": "feather dataset",
        ".arrow": "arrow dataset",
        ".h5": "hdf5 dataset",
        ".hdf5": "hdf5 dataset",
    }
    _MODEL_TYPES = {
        ".pkl": "pickle model artifact",
        ".joblib": "joblib model artifact",
        ".pt": "torch model artifact",
        ".onnx": "onnx model artifact",
    }

    def extract(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix not in self._DATASET_TYPES and suffix not in self._MODEL_TYPES:
            return f"[data_artifact_extractor: unsupported file type {path.suffix or '(none)'}]"

        try:
            stat = path.stat()
        except Exception as exc:  # noqa: BLE001 - graceful degradation required
            return f"[data_artifact_extractor: could not read {path.name} - {exc}]"

        lines = [
            f"# Data Artifact: {path.name}",
            f"- Type: {self._artifact_kind(suffix)}",
            f"- Size bytes: {stat.st_size}",
            f"- Modified at: {self._iso8601(stat.st_mtime)}",
            "- Content policy: metadata-only",
        ]

        schema_hints = self._schema_hints(path)
        if schema_hints:
            lines.append("## Schema Hints")
            lines.extend(f"- {hint}" for hint in schema_hints)
        else:
            lines.append("## Schema Hints")
            lines.append("- None available")

        lines.append("## Notes")
        lines.extend(f"- {note}" for note in self._notes_for_suffix(suffix))
        return "\n".join(lines)

    def _artifact_kind(self, suffix: str) -> str:
        return self._DATASET_TYPES.get(suffix) or self._MODEL_TYPES.get(suffix) or "unknown artifact"

    def _schema_hints(self, path: Path) -> list[str]:
        suffix = path.suffix.lower()
        if suffix == ".parquet":
            return self._parquet_hints(path)
        if suffix in {".feather", ".arrow"}:
            return self._arrow_hints(path)
        if suffix in {".h5", ".hdf5"}:
            return self._hdf5_hints(path)
        return []

    def _parquet_hints(self, path: Path) -> list[str]:
        module = self._import_pyarrow_parquet()
        if module is None:
            return ["pyarrow not installed; file metadata only"]

        parquet_file = module.ParquetFile(path)
        hints = [
            f"Rows: {parquet_file.metadata.num_rows}",
            f"Columns: {parquet_file.metadata.num_columns}",
        ]
        names = list(getattr(parquet_file.schema, "names", []) or [])
        if names:
            hints.append(f"Schema fields: {', '.join(names)}")
        return hints

    def _arrow_hints(self, path: Path) -> list[str]:
        ipc = self._import_pyarrow_ipc()
        if ipc is None:
            return ["pyarrow not installed; file metadata only"]

        with ipc.open_file(path) as reader:
            hints = [f"Record batches: {reader.num_record_batches}"]
            schema = getattr(reader, "schema", None)
            names = list(getattr(schema, "names", []) or [])
            if names:
                hints.append(f"Schema fields: {', '.join(names)}")
            return hints

    def _hdf5_hints(self, path: Path) -> list[str]:
        module = self._import_h5py()
        if module is None:
            return ["h5py not installed; file metadata only"]

        with module.File(path, "r") as handle:
            top_level = list(handle.keys())
            hints = [f"Top-level entries: {len(top_level)}"]
            if top_level:
                hints.append(f"Top-level names: {', '.join(top_level[:10])}")
            return hints

    def _notes_for_suffix(self, suffix: str) -> list[str]:
        if suffix in self._MODEL_TYPES:
            return [
                "Model artifacts are not deserialized or inspected in Phase 18.",
                "Use surrounding notebooks or pipeline config for behavioral context.",
            ]
        return [
            "Dataset contents are not sampled or inlined in Phase 18.",
            "Schema hints are optional and only emitted when a local reader is available.",
        ]

    def _import_pyarrow_parquet(self):
        try:
            import pyarrow.parquet as parquet
        except Exception:  # noqa: BLE001 - dependency is optional
            return None
        return parquet

    def _import_pyarrow_ipc(self):
        try:
            import pyarrow.ipc as ipc
        except Exception:  # noqa: BLE001 - dependency is optional
            return None
        return ipc

    def _import_h5py(self):
        try:
            import h5py
        except Exception:  # noqa: BLE001 - dependency is optional
            return None
        return h5py

    def _iso8601(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat().replace("+00:00", "Z")
