# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Knowledge graph builder service (Phase 10 Layer 3)."""

from __future__ import annotations

import dataclasses
import fnmatch
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from grain.domain.packets import parse_task_metadata
from grain.services.structural_intelligence_service import (
    StructuralExtraction,
    StructuralEntity,
    extract_structural_entities_for_files,
)

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover - exercised through fallback tests
    nx = None

if TYPE_CHECKING:
    from grain.cli.output import CommandResult


EDGE_CONFIDENCE_VALUES = {"EXTRACTED", "INFERRED", "AMBIGUOUS"}
_PROPOSALS_DIR = Path("docs/working/proposals/graphs")


@dataclass(frozen=True)
class GraphNode:
    id: str
    kind: str
    label: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    edge_type: str
    confidence: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class KnowledgeGraphArtifact:
    graph_id: str
    generated_at: str
    produced_by: str
    engine: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]

    def to_dict(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "generated_at": self.generated_at,
            "produced_by": self.produced_by,
            "engine": self.engine,
            "nodes": [dataclasses.asdict(node) for node in self.nodes],
            "edges": [dataclasses.asdict(edge) for edge in self.edges],
        }


def build_knowledge_graph(
    root: Path,
    source_paths: list[str],
    *,
    produced_by: str = "graph_service",
    graph_id: str | None = None,
) -> tuple[CommandResult, KnowledgeGraphArtifact | None]:
    """Build an inspectable knowledge graph artifact from source paths."""
    if not source_paths:
        return (
            _command_result(
                ok=False,
                command="graph build",
                errors=["source_paths is required"],
            ),
            None,
        )

    extractions = extract_structural_entities_for_files(root, source_paths)
    graph = _new_graph()
    _add_file_and_entity_nodes(root, graph, extractions)
    _add_static_repo_nodes(root, graph)
    _add_static_repo_edges(root, graph)

    nodes, edges = _graph_to_records(graph)
    artifact = KnowledgeGraphArtifact(
        graph_id=graph_id or _new_graph_id(),
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        produced_by=produced_by,
        engine="networkx" if nx is not None else "fallback",
        nodes=nodes,
        edges=edges,
    )
    return _command_result(ok=True, command="graph build", repo=str(root)), artifact


def persist_knowledge_graph(
    root: Path,
    artifact: KnowledgeGraphArtifact,
    *,
    output_path: Path | None = None,
) -> tuple[CommandResult, Path]:
    """Persist a knowledge graph artifact as JSON on disk."""
    path = output_path or (root / _PROPOSALS_DIR / f"{artifact.graph_id}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact.to_dict(), indent=2) + "\n", encoding="utf-8")
    return (
        _command_result(
            ok=True,
            command="graph persist",
            repo=str(root),
            files_created=[str(path)],
        ),
        path,
    )


def build_and_persist_knowledge_graph(
    root: Path,
    source_paths: list[str],
    *,
    produced_by: str = "graph_service",
) -> tuple[CommandResult, dict[str, object] | None]:
    """Build and persist one knowledge graph artifact in a single call."""
    result, artifact = build_knowledge_graph(root, source_paths, produced_by=produced_by)
    if artifact is None:
        return result, None

    persist_result, path = persist_knowledge_graph(root, artifact)
    payload = {
        "artifact_path": str(path),
        "graph": artifact.to_dict(),
    }
    return (
        _command_result(
            ok=True,
            command="graph build",
            repo=str(root),
            files_created=persist_result.files_created,
        ),
        payload,
    )


def _command_result(**kwargs):
    from grain.cli.output import CommandResult

    return CommandResult(**kwargs)


def _new_graph_id() -> str:
    return f"KG-{uuid4().hex[:8].upper()}"


def _new_graph():
    return nx.DiGraph() if nx is not None else _FallbackDiGraph()


def _add_file_and_entity_nodes(root: Path, graph, extractions: list[StructuralExtraction]) -> None:
    for extraction in extractions:
        abs_path = Path(extraction.file_path)
        rel_path = str(abs_path.relative_to(root))
        file_node = _file_node_id(rel_path)
        _add_node(
            graph,
            file_node,
            kind="file",
            label=rel_path,
            metadata={"path": rel_path, "language": extraction.language},
        )
        for entity in extraction.entities:
            entity_node = _entity_node_id(rel_path, entity)
            _add_node(
                graph,
                entity_node,
                kind=entity.entity_type,
                label=entity.name,
                metadata={
                    "path": rel_path,
                    "line": entity.line,
                    "language": entity.language,
                    **entity.metadata,
                },
            )
            _add_edge(
                graph,
                file_node,
                entity_node,
                edge_type="contains",
                confidence="EXTRACTED",
                metadata={},
            )
            _add_entity_relation_edges(graph, rel_path, entity_node, entity)


def _add_entity_relation_edges(graph, rel_path: str, entity_node: str, entity: StructuralEntity) -> None:
    if entity.entity_type == "import":
        module_node = f"module::{entity.name}"
        _add_node(
            graph,
            module_node,
            kind="module",
            label=entity.name,
            metadata={},
        )
        _add_edge(
            graph,
            entity_node,
            module_node,
            edge_type="imports",
            confidence="EXTRACTED",
            metadata={"path": rel_path},
        )
    elif entity.entity_type == "call_site":
        symbol_node = f"symbol::{entity.name}"
        _add_node(graph, symbol_node, kind="symbol", label=entity.name, metadata={})
        _add_edge(
            graph,
            entity_node,
            symbol_node,
            edge_type="calls",
            confidence="INFERRED",
            metadata={"path": rel_path},
        )
    elif entity.entity_type == "dependency":
        dep_node = f"dependency::{entity.name}"
        _add_node(graph, dep_node, kind="dependency", label=entity.name, metadata={})
        _add_edge(
            graph,
            entity_node,
            dep_node,
            edge_type="depends_on",
            confidence="EXTRACTED",
            metadata={"path": rel_path},
        )
    elif entity.entity_type == "link":
        link_node = f"link::{entity.name}"
        _add_node(graph, link_node, kind="link_target", label=entity.name, metadata={})
        _add_edge(
            graph,
            entity_node,
            link_node,
            edge_type="references",
            confidence="INFERRED",
            metadata={"path": rel_path},
        )


def _add_static_repo_nodes(root: Path, graph) -> None:
    _add_doc_nodes(root, graph, "docs/canonical", "canonical_doc")
    _add_doc_nodes(root, graph, "docs/runtime", "runtime_doc")
    _add_task_packet_nodes(root, graph)
    _add_adapter_nodes(root, graph)


def _add_doc_nodes(root: Path, graph, rel_dir: str, kind: str) -> None:
    base = root / rel_dir
    if not base.exists():
        return
    for file_path in sorted(base.rglob("*.md")):
        rel_path = str(file_path.relative_to(root))
        node_id = _file_node_id(rel_path)
        _add_node(
            graph,
            node_id,
            kind=kind,
            label=rel_path,
            metadata={"path": rel_path},
        )


def _add_task_packet_nodes(root: Path, graph) -> None:
    tasks_root = root / "tasks"
    if not tasks_root.exists():
        return
    for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
        task_md = task_dir / "task.md"
        if not task_md.exists():
            continue
        metadata = parse_task_metadata(task_md)
        task_id = metadata.get("id", task_dir.name)
        node_id = f"task_packet::{task_id}"
        _add_node(
            graph,
            node_id,
            kind="task_packet",
            label=task_id,
            metadata={
                "path": str(task_dir.relative_to(root)),
                "status": metadata.get("status", ""),
                "primary_adapter": metadata.get("primary_adapter", ""),
            },
        )


def _add_adapter_nodes(root: Path, graph) -> None:
    from grain.adapters.adapter_config import load_adapter_profiles

    try:
        profiles = load_adapter_profiles(root)
    except Exception:
        return

    for profile in profiles:
        node_id = f"adapter::{profile.adapter_id}"
        _add_node(
            graph,
            node_id,
            kind="adapter",
            label=profile.adapter_id,
            metadata={"domain_type": profile.domain_type, "applies_to": profile.applies_to},
        )


def _add_static_repo_edges(root: Path, graph) -> None:
    file_nodes = [node_id for node_id, data in _iter_nodes(graph) if data.get("kind") == "file"]

    for node_id, data in _iter_nodes(graph):
        if data.get("kind") != "task_packet":
            continue
        packet_path = data.get("metadata", {}).get("path", "")
        if not isinstance(packet_path, str):
            continue
        for file_node in file_nodes:
            file_path = _node_path(graph, file_node)
            if file_path and file_path.startswith(packet_path + "/"):
                _add_edge(
                    graph,
                    node_id,
                    file_node,
                    edge_type="contains",
                    confidence="EXTRACTED",
                    metadata={},
                )
        primary_adapter = data.get("metadata", {}).get("primary_adapter", "")
        if isinstance(primary_adapter, str) and primary_adapter:
            adapter_node = f"adapter::{primary_adapter}"
            _add_edge(
                graph,
                node_id,
                adapter_node,
                edge_type="uses_adapter",
                confidence="EXTRACTED",
                metadata={},
            )

    adapter_nodes = [
        (node_id, data) for node_id, data in _iter_nodes(graph) if data.get("kind") == "adapter"
    ]
    for adapter_node, adapter_data in adapter_nodes:
        patterns = _adapter_patterns(adapter_data)
        if not patterns:
            continue
        for file_node in file_nodes:
            file_path = _node_path(graph, file_node)
            if not file_path:
                continue
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns):
                _add_edge(
                    graph,
                    adapter_node,
                    file_node,
                    edge_type="applies_to",
                    confidence="INFERRED",
                    metadata={"matched_patterns": patterns},
                )


def _adapter_patterns(adapter_data: dict[str, object]) -> list[str]:
    metadata = adapter_data.get("metadata", {})
    if not isinstance(metadata, dict):
        return []
    applies_to = metadata.get("applies_to", [])
    patterns = []
    if isinstance(applies_to, list):
        for item in applies_to:
            text = str(item).lower()
            if "python" in text or "backend" in text or "cli" in text:
                patterns.extend(["src/*.py", "src/**/*.py", "tests/*.py", "tests/**/*.py"])
            if "react" in text or "typescript" in text or "javascript" in text:
                patterns.extend(
                    [
                        "src/*.ts",
                        "src/**/*.ts",
                        "src/*.tsx",
                        "src/**/*.tsx",
                        "src/*.js",
                        "src/**/*.js",
                        "src/*.jsx",
                        "src/**/*.jsx",
                    ]
                )
            if "markdown" in text:
                patterns.extend(["docs/**/*.md"])
    return sorted(set(patterns))


def _graph_to_records(graph) -> tuple[list[GraphNode], list[GraphEdge]]:
    nodes: list[GraphNode] = []
    for node_id, data in sorted(_iter_nodes(graph), key=lambda item: item[0]):
        nodes.append(
            GraphNode(
                id=node_id,
                kind=str(data.get("kind", "unknown")),
                label=str(data.get("label", node_id)),
                metadata=dict(data.get("metadata", {})),
            )
        )

    edges: list[GraphEdge] = []
    for source, target, data in sorted(_iter_edges(graph), key=lambda item: (item[0], item[1], item[2].get("edge_type", ""))):
        confidence = str(data.get("confidence", "INFERRED"))
        if confidence not in EDGE_CONFIDENCE_VALUES:
            confidence = "INFERRED"
        edges.append(
            GraphEdge(
                source=source,
                target=target,
                edge_type=str(data.get("edge_type", "related_to")),
                confidence=confidence,
                metadata=dict(data.get("metadata", {})),
            )
        )
    return nodes, edges


def _file_node_id(rel_path: str) -> str:
    return f"file::{rel_path}"


def _entity_node_id(rel_path: str, entity: StructuralEntity) -> str:
    return f"entity::{rel_path}::{entity.entity_type}::{entity.name}::{entity.line}"


def _node_path(graph, node_id: str) -> str:
    data = _node_data(graph, node_id)
    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        path = metadata.get("path", "")
        if isinstance(path, str):
            return path
    return ""


def _node_data(graph, node_id: str) -> dict[str, object]:
    if nx is not None:
        return dict(graph.nodes[node_id])
    return dict(graph.node_data(node_id))


def _add_node(graph, node_id: str, *, kind: str, label: str, metadata: dict[str, object]) -> None:
    payload = {"kind": kind, "label": label, "metadata": metadata}
    if nx is not None:
        if graph.has_node(node_id):
            return
        graph.add_node(node_id, **payload)
        return
    graph.add_node(node_id, payload)


def _add_edge(
    graph,
    source: str,
    target: str,
    *,
    edge_type: str,
    confidence: str,
    metadata: dict[str, object],
) -> None:
    payload = {"edge_type": edge_type, "confidence": confidence, "metadata": metadata}
    if nx is not None:
        graph.add_edge(source, target, **payload)
        return
    graph.add_edge(source, target, payload)


def _iter_nodes(graph):
    if nx is not None:
        return graph.nodes(data=True)
    return graph.nodes()


def _iter_edges(graph):
    if nx is not None:
        return graph.edges(data=True)
    return graph.edges()


class _FallbackDiGraph:
    """Small deterministic fallback graph when NetworkX is unavailable."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, object]] = {}
        self._edges: dict[tuple[str, str], dict[str, object]] = {}

    def add_node(self, node_id: str, data: dict[str, object]) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = data

    def add_edge(self, source: str, target: str, data: dict[str, object]) -> None:
        if source not in self._nodes:
            self._nodes[source] = {"kind": "unknown", "label": source, "metadata": {}}
        if target not in self._nodes:
            self._nodes[target] = {"kind": "unknown", "label": target, "metadata": {}}
        self._edges[(source, target)] = data

    def nodes(self):
        return [(node_id, data) for node_id, data in self._nodes.items()]

    def edges(self):
        return [(source, target, data) for (source, target), data in self._edges.items()]

    def node_data(self, node_id: str) -> dict[str, object]:
        return self._nodes[node_id]
