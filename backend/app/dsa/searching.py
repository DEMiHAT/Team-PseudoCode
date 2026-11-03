"""
Deterministic Searching Algorithms.
Linear Search and Binary Search with step-by-step pointer state (low, mid, high)
and comparison highlights.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus, VisualizationTrace


class DeterministicSearching(BaseDataStructure):
    """
    Searching algorithms engine emitting discrete inspection steps.
    """

    def __init__(self, array: List[int]):
        super().__init__(category=DSACategory.SEARCHING)
        self.array = list(array)
        self._initial_state = self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "array": list(self.array),
            "size": len(self.array),
        }

    def reset(self) -> None:
        self.steps = []
        self._initial_state = self.snapshot()

    def linear_search(self, target: int) -> int:
        """Sequential search through array elements."""
        for i, val in enumerate(self.array):
            self.record_step(
                operation=f"LINEAR_SEARCH({target}) @ index {i}",
                description=f"Inspecting index {i}: array[{i}] == {val}. Comparing with target {target}.",
                variables={"index": i, "value": val, "target": target},
                prev_state=self.snapshot(),
                updated_state=self.snapshot(),
                highlighted_indices=[i],
                status=TraceStepStatus.COMPARISON,
            )
            if val == target:
                self.record_step(
                    operation=f"FOUND({target})",
                    description=f"Target {target} located at index {i}.",
                    variables={"index": i, "target": target},
                    prev_state=self.snapshot(),
                    updated_state=self.snapshot(),
                    final_result=i,
                    highlighted_indices=[i],
                    status=TraceStepStatus.ELEMENT_FOUND,
                )
                return i

        self.record_step(
            operation=f"NOT_FOUND({target})",
            description=f"Target {target} does not exist in array.",
            variables={"target": target},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            final_result=-1,
            status=TraceStepStatus.ELEMENT_NOT_FOUND,
        )
        return -1

    def binary_search(self, target: int) -> int:
        """Divide-and-conquer binary search on sorted array."""
        low = 0
        high = len(self.array) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_val = self.array[mid]

            self.record_step(
                operation=f"BINARY_SEARCH({target})",
                description=f"Window [low={low}, high={high}]. Midpoint at index {mid} (value={mid_val}).",
                variables={"low": low, "high": high, "mid": mid, "mid_val": mid_val, "target": target},
                prev_state=self.snapshot(),
                updated_state=self.snapshot(),
                highlighted_indices=[mid],
                status=TraceStepStatus.COMPARISON,
            )

            if mid_val == target:
                self.record_step(
                    operation=f"FOUND({target})",
                    description=f"Target {target} found at mid index {mid}.",
                    variables={"index": mid, "target": target},
                    prev_state=self.snapshot(),
                    updated_state=self.snapshot(),
                    final_result=mid,
                    highlighted_indices=[mid],
                    status=TraceStepStatus.ELEMENT_FOUND,
                )
                return mid
            elif mid_val < target:
                low = mid + 1
            else:
                high = mid - 1

        self.record_step(
            operation=f"NOT_FOUND({target})",
            description=f"Search interval exhausted. Target {target} not present in sorted array.",
            variables={"low": low, "high": high, "target": target},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            final_result=-1,
            status=TraceStepStatus.ELEMENT_NOT_FOUND,
        )
        return -1

