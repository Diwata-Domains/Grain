from __future__ import annotations

from pathlib import Path

from grain.services.data_artifact_extractor import DataArtifactExtractor


def test_extract_rejects_unsupported_suffix(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    text = DataArtifactExtractor().extract(path)

    assert "unsupported file type .txt" in text


def test_extract_reports_generic_model_artifact_metadata(tmp_path: Path):
    path = tmp_path / "model.onnx"
    path.write_bytes(b"\x08\x01fake")

    text = DataArtifactExtractor().extract(path)

    assert "# Data Artifact: model.onnx" in text
    assert "- Type: onnx model artifact" in text
    assert "- Content policy: metadata-only" in text
    assert "Model artifacts are not deserialized or inspected in Phase 18." in text
    assert "Schema Hints" in text


def test_extract_reports_parquet_fallback_when_pyarrow_missing(tmp_path: Path, monkeypatch):
    path = tmp_path / "dataset.parquet"
    path.write_bytes(b"PAR1")

    extractor = DataArtifactExtractor()
    monkeypatch.setattr(extractor, "_import_pyarrow_parquet", lambda: None)

    text = extractor.extract(path)

    assert "- Type: parquet dataset" in text
    assert "pyarrow not installed; file metadata only" in text
    assert "Dataset contents are not sampled or inlined in Phase 18." in text


def test_extract_uses_fake_parquet_reader_for_schema_hints(tmp_path: Path, monkeypatch):
    path = tmp_path / "dataset.parquet"
    path.write_bytes(b"PAR1")

    class FakeMetadata:
        num_rows = 42
        num_columns = 3

    class FakeSchema:
        names = ["id", "score", "label"]

    class FakeParquetFile:
        def __init__(self, _path):
            self.metadata = FakeMetadata()
            self.schema = FakeSchema()

    class FakeParquetModule:
        ParquetFile = FakeParquetFile

    extractor = DataArtifactExtractor()
    monkeypatch.setattr(extractor, "_import_pyarrow_parquet", lambda: FakeParquetModule())

    text = extractor.extract(path)

    assert "Rows: 42" in text
    assert "Columns: 3" in text
    assert "Schema fields: id, score, label" in text


def test_extract_uses_fake_hdf5_reader_for_schema_hints(tmp_path: Path, monkeypatch):
    path = tmp_path / "dataset.h5"
    path.write_bytes(b"HDF5")

    class FakeHandle:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def keys(self):
            return ["train", "labels"]

    class FakeH5Module:
        def File(self, _path, _mode):
            return FakeHandle()

    extractor = DataArtifactExtractor()
    monkeypatch.setattr(extractor, "_import_h5py", lambda: FakeH5Module())

    text = extractor.extract(path)

    assert "Top-level entries: 2" in text
    assert "Top-level names: train, labels" in text


def test_extract_reports_missing_file_as_read_error(tmp_path: Path):
    text = DataArtifactExtractor().extract(tmp_path / "missing.parquet")

    assert "could not read missing.parquet" in text
