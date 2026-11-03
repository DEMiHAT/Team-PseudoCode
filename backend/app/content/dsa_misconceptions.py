"""
Catalog of IT22301 DSA Misconception Rules.
Contains pattern and runtime definitions for common student cognitive bugs in Java DSA.
"""

from typing import List
from app.intelligence.misconception_engine import MisconceptionRule


def get_default_dsa_rules() -> List[MisconceptionRule]:
    """Returns rule catalog for diagnosing typical Java DSA mistakes."""
    return [
        MisconceptionRule(
            rule_code="DSA-ERR-OFF-BY-ONE",
            name="Array Off-by-One Boundary Slip",
            severity="Critical",
            explanation="The loop condition accesses an index outside valid bounds [0, length - 1], causing an IndexOutOfBoundsException.",
            suggested_remedy="Check the loop termination condition. Replace `i <= arr.length` with `i < arr.length` or verify that `i - 1` is non-negative.",
            matcher_pattern=r"(<=\s*\w+\.length|\bIndexOutOfBoundsException\b)",
            runtime_keyword="ArrayIndexOutOfBoundsException",
        ),
        MisconceptionRule(
            rule_code="DSA-ERR-NULL-DEREF",
            name="Unchecked Node Reference Dereference",
            severity="Critical",
            explanation="Attempting to access `.next`, `.val`, `.left`, or `.right` on a reference that is null.",
            suggested_remedy="Always guard pointer traversals with a null check (e.g. `while (current != null)` instead of `while (current.next != null)` unless looking ahead).",
            matcher_pattern=r"(\.next\.next|\.next\.val)",
            runtime_keyword="NullPointerException",
        ),
        MisconceptionRule(
            rule_code="DSA-ERR-MISSING-BASE-CASE",
            name="Missing or Incomplete Recursion Base Case",
            severity="Critical",
            explanation="The recursive method does not reliably terminate, leading to deep call stack exhaustion.",
            suggested_remedy="Identify the simplest input state (e.g., `root == null` or `low > high`) and return immediately before making recursive calls.",
            matcher_pattern=r"(StackOverflowError)",
            runtime_keyword="StackOverflowError",
        ),
        MisconceptionRule(
            rule_code="DSA-ERR-STACK-EMPTY-POP",
            name="Stack or Queue Underflow",
            severity="Warning",
            explanation="Attempting to pop or peek from a stack or dequeue from an empty queue without checking `isEmpty()`.",
            suggested_remedy="Always verify `!stack.isEmpty()` before invoking `pop()` or `peek()` to prevent EmptyStackException.",
            matcher_pattern=r"(EmptyStackException|\.pop\(\);)",
            runtime_keyword="EmptyStackException",
        ),
        MisconceptionRule(
            rule_code="DSA-ERR-CYCLE-VISITED-SET",
            name="Missing Visited Tracking in Graph Traversal",
            severity="Critical",
            explanation="Graph traversal (BFS/DFS) lacks a visited set/array, leading to an infinite cycle on cyclic graphs.",
            suggested_remedy="Maintain a `boolean[] visited` array or `Set<Integer> visited` and check `!visited.contains(neighbor)` before adding to the queue/stack.",
            matcher_pattern=r"(Time Limit Exceeded)",
            runtime_keyword="Time Limit Exceeded",
        ),
    ]

