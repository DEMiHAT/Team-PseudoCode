"""
Deterministic Binary Search Tree (BST) ADT.
Supports recursive/iterative insertion, binary search with comparison traces,
and in-order, pre-order, and post-order depth-first traversals.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus


class TreeNode:
    """Internal BST Node."""
    def __init__(self, val: int, node_id: int):
        self.val = val
        self.node_id = node_id
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None


class DeterministicBST(BaseDataStructure):
    """
    Binary Search Tree with trace capture of comparison paths and visits.
    """

    def __init__(self, initial_values: Optional[List[int]] = None):
        super().__init__(category=DSACategory.TREE)
        self.root: Optional[TreeNode] = None
        self._next_id: int = 1
        self.size: int = 0

        if initial_values:
            for val in initial_values:
                self.insert(val)

        self._initial_state = self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        node_map = {}

        def traverse(node: Optional[TreeNode]):
            if not node:
                return
            node_map[str(node.node_id)] = {
                "id": node.node_id,
                "val": node.val,
                "left_id": node.left.node_id if node.left else None,
                "right_id": node.right.node_id if node.right else None,
            }
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)
        return {
            "root_id": self.root.node_id if self.root else None,
            "nodes": node_map,
            "size": self.size,
        }

    def reset(self) -> None:
        self.root = None
        self._next_id = 1
        self.size = 0
        self.steps = []
        self._initial_state = self.snapshot()

    def insert(self, val: int) -> None:
        prev = self.snapshot()
        new_node = TreeNode(val, self._next_id)
        self._next_id += 1

        if not self.root:
            self.root = new_node
            self.size += 1
            curr = self.snapshot()
            self.record_step(
                operation=f"INSERT({val})",
                description=f"Inserted {val} as tree ROOT (Node ID: {new_node.node_id}).",
                variables={"val": val, "node_id": new_node.node_id},
                prev_state=prev,
                updated_state=curr,
                status=TraceStepStatus.SUCCESS,
            )
            return

        curr_ptr = self.root
        while True:
            if val < curr_ptr.val:
                if curr_ptr.left is None:
                    curr_ptr.left = new_node
                    break
                curr_ptr = curr_ptr.left
            else:
                if curr_ptr.right is None:
                    curr_ptr.right = new_node
                    break
                curr_ptr = curr_ptr.right

        self.size += 1
        curr = self.snapshot()
        self.record_step(
            operation=f"INSERT({val})",
            description=f"Inserted node with value {val} at correct BST position.",
            variables={"val": val, "node_id": new_node.node_id},
            prev_state=prev,
            updated_state=curr,
            status=TraceStepStatus.SUCCESS,
        )

    def search(self, target: int) -> bool:
        curr = self.root
        steps_taken = 0
        while curr:
            steps_taken += 1
            self.record_step(
                operation=f"SEARCH({target})",
                description=f"Comparing target {target} with current node {curr.val}.",
                variables={"target": target, "current_val": curr.val, "node_id": curr.node_id},
                prev_state=self.snapshot(),
                updated_state=self.snapshot(),
                status=TraceStepStatus.COMPARISON,
            )
            if curr.val == target:
                self.record_step(
                    operation=f"SEARCH({target}) -> FOUND",
                    description=f"Target {target} located at Node ID {curr.node_id}.",
                    variables={"target": target, "found": True},
                    prev_state=self.snapshot(),
                    updated_state=self.snapshot(),
                    final_result=True,
                    status=TraceStepStatus.ELEMENT_FOUND,
                )
                return True
            elif target < curr.val:
                curr = curr.left
            else:
                curr = curr.right

        self.record_step(
            operation=f"SEARCH({target}) -> NOT_FOUND",
            description=f"Target {target} is not present in the Binary Search Tree.",
            variables={"target": target, "found": False},
            prev_state=self.snapshot(),
            updated_state=self.snapshot(),
            final_result=False,
            status=TraceStepStatus.ELEMENT_NOT_FOUND,
        )
        return False

