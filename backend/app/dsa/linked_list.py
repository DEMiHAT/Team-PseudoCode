"""
Deterministic Singly Linked List ADT.
Supports node insertion (head/tail), node deletion, pointer traversal,
and the canonical 3-pointer list reversal algorithm (IT22301 Core).
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class ListNode:
    """Internal representation of a Singly Linked List Node."""
    def __init__(self, val: Any, node_id: int):
        self.val = val
        self.node_id = node_id
        self.next: Optional["ListNode"] = None


class DeterministicLinkedList(BaseDataStructure):
    """
    Singly Linked List with discrete pointer tracking (prev, curr, next).
    """

    def __init__(self, initial_values: Optional[List[Any]] = None):
        super().__init__(category=DSACategory.LINKED_LIST)
        self.head: Optional[ListNode] = None
        self._next_id: int = 1
        self.size: int = 0

        if initial_values:
            for val in initial_values:
                self.append(val)

        self._initial_state = self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        nodes = []
        curr = self.head
        while curr is not None:
            nodes.append({
                "id": curr.node_id,
                "val": curr.val,
                "next_id": curr.next.node_id if curr.next else None,
            })
            curr = curr.next
        return {
            "nodes": nodes,
            "head_id": self.head.node_id if self.head else None,
            "size": self.size,
            "values": [n["val"] for n in nodes],
        }

    def reset(self) -> None:
        self.head = None
        self.size = 0
        self._next_id = 1
        self.steps = []
        self._initial_state = self.snapshot()

    def append(self, val: Any) -> None:
        prev = self.snapshot()
        new_node = ListNode(val, self._next_id)
        self._next_id += 1

        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node

        self.size += 1
        curr_snap = self.snapshot()
        self.record_step(
            operation=f"APPEND({val})",
            description=f"Appended node with value '{val}' (ID: {new_node.node_id}) to tail.",
            variables={"value": val, "node_id": new_node.node_id, "size": self.size},
            prev_state=prev,
            updated_state=curr_snap,
            highlighted_indices=[self.size - 1],
            status=TraceStepStatus.SUCCESS,
        )

    def prepend(self, val: Any) -> None:
        prev = self.snapshot()
        new_node = ListNode(val, self._next_id)
        self._next_id += 1
        new_node.next = self.head
        self.head = new_node
        self.size += 1
        curr_snap = self.snapshot()

        self.record_step(
            operation=f"PREPEND({val})",
            description=f"Prepend node '{val}' at head. Updated head pointer to new node ID {new_node.node_id}.",
            variables={"value": val, "node_id": new_node.node_id, "size": self.size},
            prev_state=prev,
            updated_state=curr_snap,
            highlighted_indices=[0],
            status=TraceStepStatus.SUCCESS,
        )

    def reverse(self) -> None:
        """
        In-place 3-pointer reversal algorithm.
        Emits step-by-step trace showing prev, current, next transitions.
        """
        prev_node: Optional[ListNode] = None
        curr_node: Optional[ListNode] = self.head

        self.record_step(
            operation="REVERSE_START",
            description="Starting 3-pointer reversal: prev = null, current = head.",
            variables={"prev": None, "curr": curr_node.node_id if curr_node else None},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            status=TraceStepStatus.SUCCESS,
        )

        step_counter = 1
        while curr_node is not None:
            before_step = self.snapshot()
            next_node = curr_node.next
            curr_node.next = prev_node

            prev_id = prev_node.node_id if prev_node else None
            curr_id = curr_node.node_id
            next_id = next_node.node_id if next_node else None

            prev_node = curr_node
            curr_node = next_node

            # Update head representation if loop finishes
            if curr_node is None:
                self.head = prev_node

            after_step = self.snapshot()
            self.record_step(
                operation=f"REVERSE_STEP({step_counter})",
                description=(
                    f"Reversed link: node {curr_id}.next now points to {prev_id}. "
                    f"Advanced prev to {curr_id}, curr to {next_id}."
                ),
                variables={"prev_id": prev_id, "curr_id": curr_id, "next_id": next_id},
                prev_state=before_step,
                updated_state=after_step,
                status=TraceStepStatus.SUCCESS,
            )
            step_counter += 1

        self.record_step(
            operation="REVERSE_COMPLETE",
            description="Linked list reversal complete. Head now points to the original tail node.",
            variables={"new_head_id": self.head.node_id if self.head else None},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            status=TraceStepStatus.SUCCESS,
        )

