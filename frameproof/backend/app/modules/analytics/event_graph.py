"""FrameProof Cross-Camera Event Graph.

Purpose: Formulate an interactive causal and temporal graph correlating events across all camera feeds.
Inputs: Detected events, object trajectories, and camera locations.
Outputs: Directed acyclic graph (DAG) representing subject movement and incident progression.
Status: Stub
"""

from typing import Any

from app.core.models import Event


class EventGraphBuilder:
    """Builds spatiotemporal relationship graph between events (planned)."""

    def __init__(self) -> None:
        pass

    def build_graph(self, events: list[Event]) -> dict[str, Any]:
        """Construct graph nodes and edges from forensic events.

        Raises:
            NotImplementedError: Cross-camera event graph generation is planned.
        """
        raise NotImplementedError("planned: multi-camera spatiotemporal event correlation graph")
