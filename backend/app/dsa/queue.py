"""
Deterministic Queue and Circular Queue ADT Implementations.
Supports FIFO (First-In, First-Out) operations with bounded front/rear pointers and modulo indexing.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class DeterministicQueue(BaseDataStructure):
    """
    Linear Bounded Queue (FIFO).
    Front index tracks the head element; rear index tracks the tail.
    """

    DEFAULT_CAPACITY = 5

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        super().__init__(category=DSACategory.QUEUE, capacity=capacity)
        self.capacity = max(1, capacity)
        self.elements: List[Optional[Any]] = [None] * self.capacity
        self.front: int = 0
        self.rear: int = -1
        self.size: int = 0
        self._initial_state = self.snapshot()

        self.record_step(
            operation="INITIALIZE",
            description=f"Initialized empty linear queue with capacity {self.capacity}.",
            variables={"front": self.front, "rear": self.rear, "size": self.size, "capacity": self.capacity},
            prev_state=None,
            updated_state=self.snapshot(),
            status=TraceStepStatus.SUCCESS,
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "elements": [x for x in self.elements],
            "front": self.front,
            "rear": self.rear,
            "size": self.size,
            "capacity": self.capacity,
            "is_empty": self.size == 0,
            "is_full": self.size == self.capacity,
        }

    def reset(self) -> None:
        self.elements = [None] * self.capacity
        self.front = 0
        self.rear = -1
        self.size = 0
        self.steps = []
        self._initial_state = self.snapshot()

    def enqueue(self, value: Any) -> bool:
        prev = self.snapshot()
        if self.size >= self.capacity:
            self.record_step(
                operation=f"ENQUEUE({value})",
                description=f"Queue Overflow! Cannot enqueue '{value}' into full queue (size={self.size}).",
                variables={"value": value, "size": self.size, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.OVERFLOW,
            )
            return False

        self.rear += 1
        self.elements[self.rear] = value
        self.size += 1
        curr = self.snapshot()

        self.record_step(
            operation=f"ENQUEUE({value})",
            description=f"Enqueued '{value}' at rear position {self.rear}. Queue size is now {self.size}.",
            variables={"value": value, "rear": self.rear, "front": self.front, "size": self.size},
            prev_state=prev,
            updated_state=curr,
            highlighted_indices=[self.rear],
            status=TraceStepStatus.SUCCESS,
        )
        return True

    def dequeue(self) -> Optional[Any]:
        prev = self.snapshot()
        if self.size == 0:
            self.record_step(
                operation="DEQUEUE()",
                description="Queue Underflow! Cannot dequeue from an empty queue.",
                variables={"size": self.size, "front": self.front},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.UNDERFLOW,
            )
            return None

        val = self.elements[self.front]
        self.elements[self.front] = None
        removed_front = self.front
        self.front += 1
        self.size -= 1
        curr = self.snapshot()

        self.record_step(
            operation="DEQUEUE()",
            description=f"Dequeued front element '{val}' from position {removed_front}.",
            variables={"removed_value": val, "front": self.front, "rear": self.rear, "size": self.size},
            prev_state=prev,
            updated_state=curr,
            final_result=val,
            highlighted_indices=[removed_front],
            status=TraceStepStatus.SUCCESS,
        )
        return val


class DeterministicCircularQueue(BaseDataStructure):
    """
    Circular Queue ADT utilizing modulo arithmetic `(index + 1) % capacity`.
    Avoids linear queue memory wastage upon repeated dequeues.
    """

    DEFAULT_CAPACITY = 5

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        super().__init__(category=DSACategory.CIRCULAR_QUEUE, capacity=capacity)
        self.capacity = max(1, capacity)
        self.elements: List[Optional[Any]] = [None] * self.capacity
        self.front: int = -1
        self.rear: int = -1
        self._initial_state = self.snapshot()

        self.record_step(
            operation="INITIALIZE",
            description=f"Initialized empty circular queue of capacity {self.capacity}.",
            variables={"front": self.front, "rear": self.rear, "capacity": self.capacity},
            prev_state=None,
            updated_state=self.snapshot(),
            status=TraceStepStatus.SUCCESS,
        )

    def snapshot(self) -> Dict[str, Any]:
        is_empty = self.front == -1
        is_full = (self.rear + 1) % self.capacity == self.front
        return {
            "elements": [x for x in self.elements],
            "front": self.front,
            "rear": self.rear,
            "capacity": self.capacity,
            "is_empty": is_empty,
            "is_full": is_full,
        }

    def reset(self) -> None:
        self.elements = [None] * self.capacity
        self.front = -1
        self.rear = -1
        self.steps = []
        self._initial_state = self.snapshot()

    def enqueue(self, value: Any) -> bool:
        prev = self.snapshot()
        # Full condition: (rear + 1) % capacity == front
        if (self.rear + 1) % self.capacity == self.front:
            self.record_step(
                operation=f"ENQUEUE({value})",
                description=f"Circular Queue Overflow! (rear + 1) % capacity == front (({self.rear}+1)%{self.capacity} == {self.front}).",
                variables={"value": value, "front": self.front, "rear": self.rear},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.OVERFLOW,
            )
            return False

        if self.front == -1:
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.capacity

        self.elements[self.rear] = value
        curr = self.snapshot()

        self.record_step(
            operation=f"ENQUEUE({value})",
            description=f"Circularly advanced rear to ({self.rear}) and stored '{value}'.",
            variables={"value": value, "rear": self.rear, "front": self.front},
            prev_state=prev,
            updated_state=curr,
            highlighted_indices=[self.rear],
            status=TraceStepStatus.SUCCESS,
        )
        return True

    def dequeue(self) -> Optional[Any]:
        prev = self.snapshot()
        if self.front == -1:
            self.record_step(
                operation="DEQUEUE()",
                description="Circular Queue Underflow! Cannot dequeue from empty circular queue (front == -1).",
                variables={"front": self.front, "rear": self.rear},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.UNDERFLOW,
            )
            return None

        val = self.elements[self.front]
        self.elements[self.front] = None
        removed_front = self.front

        if self.front == self.rear:
            # Last element removed: reset to empty state
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity

        curr = self.snapshot()
        self.record_step(
            operation="DEQUEUE()",
            description=f"Removed '{val}' at index {removed_front}. Front advanced to {self.front}.",
            variables={"removed_value": val, "front": self.front, "rear": self.rear},
            prev_state=prev,
            updated_state=curr,
            final_result=val,
            highlighted_indices=[removed_front],
            status=TraceStepStatus.SUCCESS,
        )
        return val

