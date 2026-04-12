"""Domain models for existing-project onboarding scaffold."""

from dataclasses import dataclass, field


@dataclass
class ScaffoldManifest:
    """Scaffold results for onboard command."""

    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    root: str = ""
