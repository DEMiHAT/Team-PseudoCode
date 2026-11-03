"""
DSA Registry and Dispatch Factory.
Allows dynamic instantiation and operation execution across all deterministic data structures.
"""

from typing import Dict, Type, Any, List, Optional
from app.dsa.base import BaseDataStructure, DSACategory, VisualizationTrace
from app.dsa.stack import DeterministicStack
from app.dsa.queue import DeterministicQueue, DeterministicCircularQueue
from app.dsa.array import DeterministicArray
from app.dsa.linked_list import DeterministicLinkedList
from app.dsa.trees import DeterministicBST
from app.dsa.graphs import DeterministicGraph
from app.dsa.searching import DeterministicSearching
from app.dsa.sorting import DeterministicSorting
from app.dsa.hashing import DeterministicHashTable


class DSARegistry:
    """
    Central registry for data structure implementations and algorithm tracers.
    """

    _REGISTRY: Dict[DSACategory, Type[BaseDataStructure]] = {
        DSACategory.STACK: DeterministicStack,
        DSACategory.QUEUE: DeterministicQueue,
        DSACategory.CIRCULAR_QUEUE: DeterministicCircularQueue,
        DSACategory.ARRAY: DeterministicArray,
        DSACategory.LINKED_LIST: DeterministicLinkedList,
        DSACategory.TREE: DeterministicBST,
        DSACategory.GRAPH: DeterministicGraph,
        DSACategory.SEARCHING: DeterministicSearching,
        DSACategory.SORTING: DeterministicSorting,
        DSACategory.HASHING: DeterministicHashTable,
    }

    @classmethod
    def get_supported_categories(cls) -> List[str]:
        """Returns all registered data structure and algorithm identifiers."""
        return [cat.value for cat in cls._REGISTRY.keys()]

    @classmethod
    def create_stack(cls, capacity: int = 5) -> DeterministicStack:
        return DeterministicStack(capacity=capacity)

    @classmethod
    def create_queue(cls, capacity: int = 5) -> DeterministicQueue:
        return DeterministicQueue(capacity=capacity)

    @classmethod
    def create_circular_queue(cls, capacity: int = 5) -> DeterministicCircularQueue:
        return DeterministicCircularQueue(capacity=capacity)

    @classmethod
    def create_array(cls, capacity: int = 6, initial_values: Optional[List[Any]] = None) -> DeterministicArray:
        return DeterministicArray(capacity=capacity, initial_values=initial_values)

    @classmethod
    def create_linked_list(cls, initial_values: Optional[List[Any]] = None) -> DeterministicLinkedList:
        return DeterministicLinkedList(initial_values=initial_values)

    @classmethod
    def create_bst(cls, initial_values: Optional[List[int]] = None) -> DeterministicBST:
        return DeterministicBST(initial_values=initial_values)

    @classmethod
    def create_graph(cls) -> DeterministicGraph:
        return DeterministicGraph()

    @classmethod
    def create_searching(cls, array: List[int]) -> DeterministicSearching:
        return DeterministicSearching(array=array)

    @classmethod
    def create_sorting(cls, array: List[int]) -> DeterministicSorting:
        return DeterministicSorting(array=array)

    @classmethod
    def create_hash_table(cls, capacity: int = 7) -> DeterministicHashTable:
        return DeterministicHashTable(capacity=capacity)

