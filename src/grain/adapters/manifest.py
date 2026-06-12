from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from grain.domain.completion_policy import CompletionPolicy
from grain.domain.embedding import (
    DEFAULT_LOCAL_EMBEDDING_MODEL,
    DEFAULT_OLLAMA_EMBEDDING_MODEL,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
)
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
    embedding_provider: Literal["none", "ollama", "local", "openai"] = "none"
    ollama_embedding_model: str = DEFAULT_OLLAMA_EMBEDDING_MODEL
    local_embedding_model: str = DEFAULT_LOCAL_EMBEDDING_MODEL
    openai_embedding_model: str = DEFAULT_OPENAI_EMBEDDING_MODEL


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
    _EMBEDDING = {"none", "ollama", "local", "openai"}

    def _pick(key: str, allowed: set, default: str) -> str:
        val = raw.get(key, default)
        return val if isinstance(val, str) and val in allowed else default

    def _pick_text(key: str, default: str) -> str:
        val = raw.get(key, default)
        return val.strip() if isinstance(val, str) and val.strip() else default

    return GrainConfig(
        default_supervision=_pick("default_supervision", _SUPERVISION, "gated"),  # type: ignore[arg-type]
        default_format=_pick("default_format", _FORMAT, "text"),  # type: ignore[arg-type]
        upgrade_check=_pick("upgrade_check", _UPGRADE, "silent"),  # type: ignore[arg-type]
        embedding_provider=_pick("embedding_provider", _EMBEDDING, "none"),  # type: ignore[arg-type]
        ollama_embedding_model=_pick_text("ollama_embedding_model", DEFAULT_OLLAMA_EMBEDDING_MODEL),
        local_embedding_model=_pick_text("local_embedding_model", DEFAULT_LOCAL_EMBEDDING_MODEL),
        openai_embedding_model=_pick_text("openai_embedding_model", DEFAULT_OPENAI_EMBEDDING_MODEL),
    )


@dataclass
class UpgradePolicy:
    """upgrade_policy block from docs_manifest.yaml."""

    min_version: str = ""
    min_version_set_at: str = ""
    enforce: bool = False
    enforce_after_days: int = 0
    message: str = ""


def load_upgrade_policy(root: Path) -> UpgradePolicy:
    """Read the optional ``upgrade_policy:`` block from docs_manifest.yaml.

    Returns an :class:`UpgradePolicy` with defaults for any field not present.
    Never raises.
    """
    try:
        manifest = load_manifest(root)
    except Exception:
        return UpgradePolicy()

    raw = manifest.get("upgrade_policy")
    if not isinstance(raw, dict):
        return UpgradePolicy()

    def _str(key: str) -> str:
        val = raw.get(key, "")
        return str(val).strip() if val is not None else ""

    def _bool_val(key: str) -> bool:
        val = raw.get(key, False)
        return val if isinstance(val, bool) else False

    def _int_val(key: str) -> int:
        val = raw.get(key, 0)
        try:
            return int(val)
        except (TypeError, ValueError):
            return 0

    return UpgradePolicy(
        min_version=_str("min_version"),
        min_version_set_at=_str("min_version_set_at"),
        enforce=_bool_val("enforce"),
        enforce_after_days=_int_val("enforce_after_days"),
        message=_str("message"),
    )


def load_completion_policy(root: Path) -> CompletionPolicy:
    try:
        manifest = load_manifest(root)
    except Exception:
        return CompletionPolicy()

    rules = manifest.get("rules")
    if not isinstance(rules, dict):
        return CompletionPolicy()

    raw = rules.get("completion_policy")
    if not isinstance(raw, dict):
        return CompletionPolicy()

    def _bool(key: str, default: bool) -> bool:
        value = raw.get(key, default)
        return value if isinstance(value, bool) else default

    return CompletionPolicy(
        require_defined_deliverable=_bool("require_defined_deliverable", True),
        require_results_recorded=_bool("require_results_recorded", True),
        require_rule_check=_bool("require_rule_check", True),
        require_user_approval=_bool("require_user_approval", True),
        require_verification_pass=_bool("require_verification_pass", False),
        allow_close_when_verification_not_run=_bool("allow_close_when_verification_not_run", True),
    )
