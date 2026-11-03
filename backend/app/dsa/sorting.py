"""
Deterministic Sorting Algorithms.
Bubble Sort, Selection Sort, and Insertion Sort with explicit comparison, swap,
and partition boundary tracing.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class DeterministicSorting(BaseDataStructure):
    """
    In-place sorting algorithm engine recording comparisons and swaps.
    """

    def __init__(self, array: List[int]):
        super().__init__(category=DSACategory.SORTING)
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

    def bubble_sort(self) -> List[int]:
        """Classic Bubble Sort algorithm with swap tracking."""
        n = len(self.array)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                prev = self.snapshot()
                self.record_step(
                    operation=f"COMPARE({self.array[j]}, {self.array[j+1]})",
                    description=f"Comparing adjacent elements: array[{j}]={self.array[j]} and array[{j+1}]={self.array[j+1]}.",
                    variables={"j": j, "val1": self.array[j], "val2": self.array[j+1]},
                    prev_state=prev,
                    updated_state=prev,
                    highlighted_indices=[j, j + 1],
                    status=TraceStepStatus.COMPARISON,
                )

                if self.array[j] > self.array[j + 1]:
                    # Swap
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    swapped = True
                    curr = self.snapshot()
                    self.record_step(
                        operation=f"SWAP({self.array[j+1]}, {self.array[j]})",
                        description=f"Swapped out-of-order elements: {self.array[j+1]} > {self.array[j]}.",
                        variables={"j": j, "new_array": list(self.array)},
                        prev_state=prev,
                        updated_state=curr,
                        highlighted_indices=[j, j + 1],
                        status=TraceStepStatus.SWAP,
                    )

            if not swapped:
                break

        self.record_step(
            operation="SORT_COMPLETE",
            description="Array is completely sorted.",
            variables={"sorted_array": list(self.array)},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            final_result=list(self.array),
            status=TraceStepStatus.SUCCESS,
        )
        return self.array
