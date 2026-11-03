"""
Deterministic Hashing Engine.
Fixed-capacity Hash Table with modulo hash function `key % capacity`
and open-addressing Linear Probing collision resolution.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class DeterministicHashTable(BaseDataStructure):
    """
    Fixed-Capacity Hash Table with Linear Probing collision resolution.
    """

    DEFAULT_CAPACITY = 7

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        super().__init__(category=DSACategory.HASHING, capacity=capacity)
        self.capacity = max(1, capacity)
        self.table: List[Optional[Dict[str, Any]]] = [None] * self.capacity
        self.size: int = 0
        self._initial_state = self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "table": [dict(x) if x else None for x in self.table],
            "size": self.size,
            "capacity": self.capacity,
            "load_factor": round(self.size / self.capacity, 2),
        }

    def reset(self) -> None:
        self.table = [None] * self.capacity
        self.size = 0
        self.steps = []
        self._initial_state = self.snapshot()

    def _hash(self, key: int) -> int:
        return key % self.capacity

    def insert(self, key: int, value: Any) -> bool:
        prev = self.snapshot()
        if self.size >= self.capacity:
            self.record_step(
                operation=f"INSERT({key})",
                description=f"Hash Table Full! Cannot insert key {key}.",
                variables={"key": key, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                status=TraceStepStatus.OVERFLOW,
            )
            return False

        h = self._hash(key)
        start_index = h
        step_count = 0

        while self.table[h] is not None and self.table[h]["key"] != key:
            self.record_step(
                operation=f"COLLISION({key}) @ index {h}",
                description=f"Collision at index {h} occupied by key {self.table[h]['key']}. Linear probing to {(h + 1) % self.capacity}.",
                variables={"key": key, "collision_index": h},
                prev_state=self.snapshot(),
                updated_state=self.snapshot(),
                highlighted_indices=[h],
                status=TraceStepStatus.COMPARISON,
            )
            h = (h + 1) % self.capacity
            step_count += 1
            if step_count >= self.capacity:
                return False

        if self.table[h] is None:
            self.size += 1

        self.table[h] = {"key": key, "value": value}
        curr = self.snapshot()

        self.record_step(
            operation=f"INSERT({key}, {value})",
            description=f"Inserted key {key} at slot {h} after {step_count} probes.",
            variables={"key": key, "slot": h, "probes": step_count, "load_factor": curr["load_factor"]},
            prev_state=prev,
            updated_state=curr,
            highlighted_indices=[h],
            status=TraceStepStatus.SUCCESS,
        )
        return True
