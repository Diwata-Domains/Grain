"""Domain models for existing-project codebase scan output."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanResult:
    """Structured output from CodebaseScanner."""

    root: str
    primary_languages: list[str] = field(default_factory=list)
    language_counts: dict[str, int] = field(default_factory=dict)
    applicable_adapters: list[str] = field(default_factory=list)
    key_files: list[str] = field(default_factory=list)
    ci_configs: list[str] = field(default_factory=list)
    documentation_files: list[str] = field(default_factory=list)
    custom_adapter_hints: list[str] = field(default_factory=list)

