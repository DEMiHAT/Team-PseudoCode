"""
Deterministic Graph ADT Implementation.
Supports adjacency list representation, vertex/edge insertions,
and Breadth-First Search (BFS) / Depth-First Search (DFS) traversals with frontier tracing.
"""

from collections import deque
from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class DeterministicGraph(BaseDataStructure):
    """
    Adjacency List Graph with discrete traversal frontier tracking.
    """

    def __init__(self):
        super().__init__(category=DSACategory.GRAPH)
        self.adj_list: Dict[str, List[str]] = {}
        self._initial_state = self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "vertices": list(self.adj_list.keys()),
            "adjacency_list": {k: list(v) for k, v in self.adj_list.items()},
            "vertex_count": len(self.adj_list),
        }

    def reset(self) -> None:
        self.adj_list = {}
        self.steps = []
        self._initial_state = self.snapshot()

    def add_vertex(self, vertex: str) -> None:
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def add_edge(self, u: str, v: str, bidirectional: bool = True) -> None:
        prev = self.snapshot()
        self.add_vertex(u)
        self.add_vertex(v)
        if v not in self.adj_list[u]:
            self.adj_list[u].append(v)
        if bidirectional and u not in self.adj_list[v]:
            self.adj_list[v].append(u)

        curr = self.snapshot()
        self.record_step(
            operation=f"ADD_EDGE({u}, {v})",
            description=f"Connected edge between vertex '{u}' and vertex '{v}'.",
            variables={"u": u, "v": v, "bidirectional": bidirectional},
            prev_state=prev,
            updated_state=curr,
            status=TraceStepStatus.SUCCESS,
        )

    def bfs(self, start_vertex: str) -> List[str]:
        """Breadth-First Search traversal with FIFO queue frontier tracking."""
        if start_vertex not in self.adj_list:
            return []

        visited = set([start_vertex])
        queue = deque([start_vertex])
        order: List[str] = []

        self.record_step(
            operation=f"BFS_START({start_vertex})",
            description=f"Initialized BFS queue with starting vertex '{start_vertex}'.",
            variables={"queue": list(queue), "visited": list(visited)},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            status=TraceStepStatus.SUCCESS,
        )

        while queue:
            curr = queue.popleft()
            order.append(curr)

            self.record_step(
                operation=f"BFS_VISIT({curr})",
                description=f"Dequeued and visited vertex '{curr}'. Inspecting adjacent neighbors.",
                variables={"current": curr, "order": list(order), "queue": list(queue)},
                prev_state=self.snapshot(),
                updated_state=self.snapshot(),
                status=TraceStepStatus.SUCCESS,
            )

            for neighbor in self.adj_list.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    self.record_step(
                        operation=f"BFS_ENQUEUE({neighbor})",
                        description=f"Discovered unvisited neighbor '{neighbor}' from '{curr}'; enqueued into BFS frontier.",
                        variables={"neighbor": neighbor, "queue": list(queue), "visited": list(visited)},
                        prev_state=self.snapshot(),
                        updated_state=self.snapshot(),
                        status=TraceStepStatus.SUCCESS,
                    )

        return order
