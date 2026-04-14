from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from grain.domain.errors import ConfigError, MissingPathError

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


@dataclass
class GrainConfig:
    """Project-level Grain configuration read from the ``grain:`` block in docs_manifest.yaml."""

    default_supervision: Literal["supervised", "gated", "autonomous"] = "gated"
    default_format: Literal["text", "json"] = "text"
    upgrade_check: Literal["warn", "silent"] = "silent"
    embedding_provider: Literal["none", "local", "openai"] = "none"


def load_grain_config(root: Path) -> GrainConfig:
    """Read the optional ``grain:`` config block from docs_manifest.yaml.

    Returns a :class:`GrainConfig` with defaults for any field not present.
    Never raises — if the manifest is missing or the block is absent, defaults apply.
    """
    try:
        manifest = load_manifest(root)
    except Exception:
        return GrainConfig()

    raw = manifest.get("grain")
    if not isinstance(raw, dict):
        return GrainConfig()

    _SUPERVISION = {"supervised", "gated", "autonomous"}
    _FORMAT = {"text", "json"}
    _UPGRADE = {"warn", "silent"}
    _EMBEDDING = {"none", "local", "openai"}

    def _pick(key: str, allowed: set, default: str) -> str:
        val = raw.get(key, default)
        return val if isinstance(val, str) and val in allowed else default

    return GrainConfig(
        default_supervision=_pick("default_supervision", _SUPERVISION, "gated"),  # type: ignore[arg-type]
        default_format=_pick("default_format", _FORMAT, "text"),  # type: ignore[arg-type]
        upgrade_check=_pick("upgrade_check", _UPGRADE, "silent"),  # type: ignore[arg-type]
        embedding_provider=_pick("embedding_provider", _EMBEDDING, "none"),  # type: ignore[arg-type]
    )
