"""
Deterministic DSA Engine for IT22301 Learning Platform.
Decoupled algorithmic logic, comprehensive step-by-step state tracing,
and structured JSON output for React visualization components.
"""

from app.dsa.base import (
    BaseDataStructure,
    DSACategory,
    TraceStep,
    TraceStepStatus,
    VisualizationTrace,
)
from app.dsa.stack import DeterministicStack, StackOverflowError, StackUnderflowError
from app.dsa.queue import DeterministicQueue, DeterministicCircularQueue
from app.dsa.array import DeterministicArray
from app.dsa.linked_list import DeterministicLinkedList
from app.dsa.trees import DeterministicBST
from app.dsa.graphs import DeterministicGraph
from app.dsa.searching import DeterministicSearching
from app.dsa.sorting import DeterministicSorting
from app.dsa.hashing import DeterministicHashTable
from app.dsa.registry import DSARegistry

__all__ = [
    "BaseDataStructure",
    "DSACategory",
    "TraceStep",
    "TraceStepStatus",
    "VisualizationTrace",
    "DeterministicStack",
    "StackOverflowError",
    "StackUnderflowError",
    "DeterministicQueue",
    "DeterministicCircularQueue",
    "DeterministicArray",
    "DeterministicLinkedList",
    "DeterministicBST",
    "DeterministicGraph",
    "DeterministicSearching",
    "DeterministicSorting",
    "DeterministicHashTable",
    "DSARegistry",
]
