"""Document registry domain model.

Provides DocumentRecord, DocumentRegistry, and build_registry() for
representing and querying the manifest's document entries in memory.
No filesystem access — operates on an already-parsed manifest dict.
"""

from dataclasses import dataclass, field


@dataclass
class DocumentRecord:
    """Represents one known project document from the manifest."""

    id: str
    path: str
    layer: str
    purpose: str
    authority: str
    editable_by_agents: bool
    read_when: list[str]


class DocumentRegistry:
    """In-memory registry of document records with layer-aware lookup."""

    def __init__(self, records: list[DocumentRecord]) -> None:
        self._records = records

    def all(self) -> list[DocumentRecord]:
        """Return all registered document records."""
        return list(self._records)

    def by_id(self, id: str) -> DocumentRecord | None:
        """Return the record with the given ID, or None if not found."""
        for record in self._records:
            if record.id == id:
                return record
        return None

    def by_layer(self, layer: str) -> list[DocumentRecord]:
        """Return all records belonging to the given layer."""
        return [r for r in self._records if r.layer == layer]


_DOC_LAYERS = ["canonical", "working", "runtime"]


def build_registry(manifest: dict) -> DocumentRegistry:
    """Build a DocumentRegistry from a parsed (and validated) manifest dict.

    Iterates over the canonical, working, and runtime sections and creates
    a DocumentRecord for each entry. Skips sections that are absent or
    non-list without raising.

    Args:
        manifest: Parsed manifest dict from load_manifest().

    Returns:
        A populated DocumentRegistry.
    """
    records: list[DocumentRecord] = []
    for layer in _DOC_LAYERS:
        entries = manifest.get(layer)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            records.append(
                DocumentRecord(
                    id=entry.get("id", ""),
                    path=entry.get("path", ""),
                    layer=layer,
                    purpose=entry.get("purpose", ""),
                    authority=entry.get("authority", ""),
                    editable_by_agents=bool(entry.get("editable_by_agents", False)),
                    read_when=entry.get("read_when") or [],
                )
            )
    return DocumentRegistry(records)
