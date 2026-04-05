from pathlib import Path

import yaml

from forge.domain.errors import ConfigError, MissingPathError

MANIFEST_PATH = "docs/runtime/docs_manifest.yaml"


def load_manifest(root: Path) -> dict:
    """Load and parse docs_manifest.yaml from the repository root.

    Args:
        root: Repository root path.

    Returns:
        Parsed manifest contents as a dict.

    Raises:
        MissingPathError: If the manifest file does not exist.
        ConfigError: If the file exists but contains invalid YAML.
    """
    manifest_file = root / MANIFEST_PATH
    if not manifest_file.exists():
        raise MissingPathError(
            f"Manifest not found: {MANIFEST_PATH}",
            detail=str(manifest_file),
        )
    try:
        with manifest_file.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(
            f"Manifest is not valid YAML: {MANIFEST_PATH}",
            detail=str(exc),
        ) from exc
