"""
Deterministic Array ADT Implementation.
Supports insertion, deletion, linear traversal, index lookup, and in-place element shifting.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class DeterministicArray(BaseDataStructure):
    """
    Fixed-Capacity Array ADT with element shifting visualization.
    """

    DEFAULT_CAPACITY = 6

    def __init__(self, capacity: int = DEFAULT_CAPACITY, initial_values: Optional[List[Any]] = None):
        super().__init__(category=DSACategory.ARRAY, capacity=capacity)
        self.capacity = max(1, capacity)
        self.elements: List[Optional[Any]] = [None] * self.capacity
        self.size: int = 0

        if initial_values:
            for val in initial_values[:self.capacity]:
                self.elements[self.size] = val
                self.size += 1

        self._initial_state = self.snapshot()
        self.record_step(
            operation="INITIALIZE",
            description=f"Initialized array of capacity {self.capacity} containing {self.size} elements.",
            variables={"capacity": self.capacity, "size": self.size},
            prev_state=None,
            updated_state=self.snapshot(),
            top_position=None,
            final_result=None,
            highlighted_indices=list(range(self.size)),
            status=TraceStepStatus.SUCCESS,
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "elements": [x for x in self.elements],
            "active_elements": [self.elements[i] for i in range(self.size)],
            "size": self.size,
            "capacity": self.capacity,
            "is_full": self.size == self.capacity,
            "is_empty": self.size == 0,
        }

    def reset(self) -> None:
        self.elements = [None] * self.capacity
        self.size = 0
        self.steps = []
        self._initial_state = self.snapshot()

    def insert_at(self, index: int, value: Any) -> bool:
        """Inserts value at given index, shifting existing elements to the right."""
        prev = self.snapshot()

        if self.size >= self.capacity:
            self.record_step(
                operation=f"INSERT({index}, {value})",
                description=f"Array Overflow! Cannot insert at index {index} because array is full (size={self.size}, capacity={self.capacity}).",
                variables={"index": index, "value": value, "size": self.size, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.OVERFLOW,
            )
            return False

        if index < 0 or index > self.size:
            self.record_step(
                operation=f"INSERT({index}, {value})",
                description=f"IndexOutOfBoundsException! Index {index} is outside valid insertion range [0, {self.size}].",
                variables={"index": index, "value": value, "size": self.size},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.ERROR,
            )
            return False

        # Shift elements rightward
        for i in range(self.size, index, -1):
            self.elements[i] = self.elements[i - 1]

        self.elements[index] = value
        self.size += 1
        curr = self.snapshot()

        self.record_step(
            operation=f"INSERT({index}, {value})",
            description=f"Shifted elements right from index {index} and inserted '{value}' at index {index}.",
            variables={"index": index, "value": value, "new_size": self.size},
            prev_state=prev,
            updated_state=curr,
            highlighted_indices=[index],
            status=TraceStepStatus.SUCCESS,
        )
        return True

    def delete_at(self, index: int) -> Optional[Any]:
        """Deletes element at given index and shifts remaining elements leftward."""
        prev = self.snapshot()

        if self.size == 0:
            self.record_step(
                operation=f"DELETE({index})",
                description="Array Underflow! Cannot delete from an empty array.",
                variables={"index": index, "size": self.size},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.UNDERFLOW,
            )
            return None

        if index < 0 or index >= self.size:
            self.record_step(
                operation=f"DELETE({index})",
                description=f"IndexOutOfBoundsException! Index {index} is outside range [0, {self.size - 1}].",
                variables={"index": index, "size": self.size},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.ERROR,
            )
            return None

        removed_val = self.elements[index]
        for i in range(index, self.size - 1):
            self.elements[i] = self.elements[i + 1]
        self.elements[self.size - 1] = None
        self.size -= 1
        curr = self.snapshot()

        self.record_step(
            operation=f"DELETE({index})",
            description=f"Removed '{removed_val}' at index {index} and shifted leftward to fill gap.",
            variables={"deleted_index": index, "removed_value": removed_val, "new_size": self.size},
            prev_state=prev,
            updated_state=curr,
            final_result=removed_val,
            highlighted_indices=[index] if index < self.size else [],
            status=TraceStepStatus.SUCCESS,
        )
        return removed_val

