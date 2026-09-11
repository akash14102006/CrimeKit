"""
Provenance tracking for CrimeKit blockchain anchoring.

Tracks the lineage of evidence-derived artifacts through processing operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProvenanceNode:
    """A single node in the provenance graph."""
    artifact_id: str
    artifact_hash: str
    operation_type: str
    parent_artifact_id: Optional[str] = None
    tool_name: Optional[str] = None
    tool_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "committed"

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProvenanceTracker:
    """
    In-memory provenance graph for tracking evidence lineage.

    Builds a DAG (directed acyclic graph) of artifacts from original
    evidence through all derived forms.
    """

    def __init__(self):
        self._nodes: Dict[str, ProvenanceNode] = {}
        self._children: Dict[str, List[str]] = {}
        self._root_artifact_id: Optional[str] = None

    @property
    def root_artifact_id(self) -> Optional[str]:
        return self._root_artifact_id

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def register(
        self,
        artifact_id: str,
        artifact_hash: str,
        operation_type: str,
        parent_artifact_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceNode:
        """Register an artifact in the provenance graph."""
        node = ProvenanceNode(
            artifact_id=artifact_id,
            artifact_hash=artifact_hash,
            operation_type=operation_type,
            parent_artifact_id=parent_artifact_id,
            tool_name=tool_name,
            tool_version=tool_version,
            metadata=metadata or {},
        )
        self._nodes[artifact_id] = node

        if parent_artifact_id and parent_artifact_id in self._children:
            self._children[parent_artifact_id].append(artifact_id)
        elif parent_artifact_id:
            self._children[parent_artifact_id] = [artifact_id]

        if parent_artifact_id is None and self._root_artifact_id is None:
            self._root_artifact_id = artifact_id

        return node

    def get_node(self, artifact_id: str) -> Optional[ProvenanceNode]:
        return self._nodes.get(artifact_id)

    def get_children(self, artifact_id: str) -> List[ProvenanceNode]:
        child_ids = self._children.get(artifact_id, [])
        return [self._nodes[cid] for cid in child_ids if cid in self._nodes]

    def get_derived_artifacts(self, root_id: str) -> List[ProvenanceNode]:
        """Get all artifacts derived (transitively) from the given root."""
        result = []
        visited = set()
        queue = [root_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for child_id in self._children.get(current, []):
                if child_id in self._nodes:
                    result.append(self._nodes[child_id])
                    queue.append(child_id)
        return result

    def get_lineage(self, artifact_id: str) -> List[ProvenanceNode]:
        """Get the full lineage from root to this artifact."""
        lineage = []
        current = artifact_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            node = self._nodes.get(current)
            if node:
                lineage.append(node)
                current = node.parent_artifact_id
            else:
                break
        lineage.reverse()
        return lineage

    def build_graph(self, evidence_id: str) -> Dict[str, Any]:
        """Build a complete graph representation for the evidence."""
        root = self._root_artifact_id
        all_nodes = list(self._nodes.values())
        return {
            "evidence_id": evidence_id,
            "root_artifact_id": root,
            "nodes": [
                {
                    "artifact_id": n.artifact_id,
                    "artifact_hash": n.artifact_hash,
                    "operation_type": n.operation_type,
                    "parent_artifact_id": n.parent_artifact_id,
                    "tool_name": n.tool_name,
                    "tool_version": n.tool_version,
                    "status": n.status,
                }
                for n in all_nodes
            ],
            "depth": self._compute_depth(root),
        }

    def _compute_depth(self, root_id: Optional[str]) -> int:
        """Compute max depth from root."""
        if not root_id or root_id not in self._nodes:
            return 0
        max_depth = 0
        visited = set()
        stack = [(root_id, 0)]
        while stack:
            node_id, depth = stack.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            max_depth = max(max_depth, depth)
            for child_id in self._children.get(node_id, []):
                if child_id in self._nodes:
                    stack.append((child_id, depth + 1))
        return max_depth
