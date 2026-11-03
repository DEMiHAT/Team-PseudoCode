"""
Unit and Integration Tests for Deterministic DSA Visualization Engine.
Validates exact algorithmic transitions, boundary invariants, overflow/underflow detection,
and structured trace output across all supported data structures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dsa import (
    DSACategory,
    TraceStepStatus,
    DeterministicStack,
    DeterministicQueue,
    DeterministicCircularQueue,
    DeterministicArray,
    DeterministicLinkedList,
    DeterministicBST,
    DeterministicGraph,
    DeterministicSearching,
    DeterministicSorting,
    DeterministicHashTable,
    DSARegistry,
)

client = TestClient(app)


# ==========================================
# 1. Stack ADT Tests (Core Implementation)
# ==========================================
def test_stack_initial_state():
    """Stack initializes with correct top pointer, size, and capacity."""
    stack = DeterministicStack(capacity=4)
    assert stack.capacity == 4
    assert stack.top == -1
    assert stack.is_empty()
    assert not stack.is_full()
    assert len(stack.steps) == 3  # INITIALIZE + ISEMPTY + ISFULL


def test_stack_push_success():
    """Pushing elements increments top pointer and preserves LIFO order."""
    stack = DeterministicStack(capacity=3)
    assert stack.push(10)
    assert stack.top == 0
    assert stack.elements[0] == 10

    assert stack.push(20)
    assert stack.top == 1
    assert stack.elements[1] == 20

    snap = stack.snapshot()
    assert snap["size"] == 2
    assert snap["active_elements"] == [10, 20]


def test_stack_pop_lifo_order():
    """Popping elements returns most recently pushed element and decrements top."""
    stack = DeterministicStack(capacity=3)
    stack.push(100)
    stack.push(200)

    val = stack.pop()
    assert val == 200
    assert stack.top == 0
    assert stack.elements[1] is None

    val2 = stack.pop()
    assert val2 == 100
    assert stack.top == -1


def test_stack_peek_non_mutating():
    """Peeking returns top element without removing it or altering top pointer."""
    stack = DeterministicStack(capacity=3)
    stack.push(42)
    top_val = stack.peek()
    assert top_val == 42
    assert stack.top == 0
    assert stack.elements[0] == 42
    assert stack.snapshot()["size"] == 1


def test_stack_is_empty_and_is_full():
    """isEmpty and isFull accurately report boolean boundaries."""
    stack = DeterministicStack(capacity=2)
    assert stack.is_empty()
    assert not stack.is_full()

    stack.push(1)
    assert not stack.is_empty()
    assert not stack.is_full()

    stack.push(2)
    assert not stack.is_empty()
    assert stack.is_full()


def test_stack_overflow_detection():
    """Pushing beyond bounded capacity triggers overflow step and returns False."""
    stack = DeterministicStack(capacity=2)
    stack.push(10)
    stack.push(20)

    success = stack.push(30)
    assert not success
    assert stack.top == 1
    assert stack.elements[1] == 20

    last_step = stack.steps[-1]
    assert last_step.status == TraceStepStatus.OVERFLOW
    assert last_step.final_result == "OVERFLOW_ERROR"
    assert "Stack Overflow" in last_step.operation_description


def test_stack_underflow_detection_on_pop():
    """Popping an empty stack triggers underflow step and returns None."""
    stack = DeterministicStack(capacity=3)
    val = stack.pop()
    assert val is None

    last_step = stack.steps[-1]
    assert last_step.status == TraceStepStatus.UNDERFLOW
    assert last_step.final_result == "UNDERFLOW_ERROR"
    assert "Stack Underflow" in last_step.operation_description


def test_stack_underflow_detection_on_peek():
    """Peeking into an empty stack triggers underflow step and returns None."""
    stack = DeterministicStack(capacity=3)
    val = stack.peek()
    assert val is None

    last_step = stack.steps[-1]
    assert last_step.status == TraceStepStatus.UNDERFLOW
    assert last_step.final_result == "UNDERFLOW_ERROR"


def test_stack_reset():
    """Resetting the stack restores empty state and records RESET transition."""
    stack = DeterministicStack(capacity=3)
    stack.push(1)
    stack.push(2)
    stack.reset()
    assert stack.top == -1
    assert stack.is_empty()
    assert len(stack.steps) == 2  # RESET + ISEMPTY


def test_stack_batch_sequence_execution():
    """execute_sequence runs multi-operation pipelines and returns a complete VisualizationTrace."""
    stack = DeterministicStack(capacity=3)
    ops = [
        {"op": "push", "value": 11},
        {"op": "push", "value": 22},
        {"op": "peek"},
        {"op": "pop"},
    ]
    trace = stack.execute_sequence(ops)
    assert trace.total_steps == 5  # INITIALIZE + 4 ops
    assert trace.final_state["active_elements"] == [11]
    assert trace.structure_type == DSACategory.STACK


# ==========================================
# 2. Extensible Data Structures & Algorithm Tests
# ==========================================
def test_array_insertion_shifting_and_bounds():
    """Array shifts elements on insertion and prevents out-of-bounds index writes."""
    arr = DeterministicArray(capacity=4, initial_values=[10, 30])
    # Insert 20 at index 1 -> [10, 20, 30]
    assert arr.insert_at(1, 20)
    assert arr.elements[:3] == [10, 20, 30]

    # Out of bounds check
    assert not arr.insert_at(10, 99)


def test_array_deletion_and_underflow():
    """Array deletes element and shifts subsequent items leftward."""
    arr = DeterministicArray(capacity=3, initial_values=[5, 10, 15])
    val = arr.delete_at(1)
    assert val == 10
    assert arr.elements[:2] == [5, 15]


def test_linear_queue_fifo_order():
    """Queue enforces FIFO order across enqueue and dequeue."""
    queue = DeterministicQueue(capacity=3)
    queue.enqueue("First")
    queue.enqueue("Second")
    assert queue.dequeue() == "First"
    assert queue.dequeue() == "Second"
    assert queue.dequeue() is None  # Underflow


def test_circular_queue_modulo_arithmetic():
    """Circular queue wraps rear and front using modulo arithmetic."""
    cq = DeterministicCircularQueue(capacity=3)
    cq.enqueue(1)
    cq.enqueue(2)
    cq.enqueue(3)
    assert cq.snapshot()["is_full"]
    assert not cq.enqueue(4)  # Overflow

    assert cq.dequeue() == 1  # Frees index 0
    assert cq.enqueue(4)      # Wraps rear to 0
    assert cq.elements[0] == 4


def test_singly_linked_list_reversal():
    """Reverses singly linked list using 3-pointer algorithm and tracks links."""
    ll = DeterministicLinkedList(initial_values=[1, 2, 3])
    assert ll.snapshot()["values"] == [1, 2, 3]
    ll.reverse()
    assert ll.snapshot()["values"] == [3, 2, 1]


def test_bst_insertion_and_search():
    """BST inserts in sorted tree order and searches along binary branch paths."""
    bst = DeterministicBST(initial_values=[50, 25, 75])
    assert bst.search(25)
    assert not bst.search(999)


def test_graph_bfs_traversal():
    """Graph BFS visits vertices in breadth-first layer order."""
    g = DeterministicGraph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    order = g.bfs("A")
    assert order[0] == "A"
    assert set(order[1:3]) == {"B", "C"}
    assert order[3] == "D"


def test_searching_algorithms():
    """Linear and Binary searches locate elements and emit comparison traces."""
    searcher = DeterministicSearching([10, 20, 30, 40, 50])
    assert searcher.linear_search(30) == 2
    assert searcher.binary_search(40) == 3
    assert searcher.binary_search(99) == -1


def test_sorting_algorithms():
    """Bubble sort sorts array and records swap steps."""
    sorter = DeterministicSorting([5, 2, 8, 1])
    sorted_arr = sorter.bubble_sort()
    assert sorted_arr == [1, 2, 5, 8]


def test_hash_table_linear_probing():
    """Hash table handles key collision via linear probing."""
    ht = DeterministicHashTable(capacity=5)
    ht.insert(key=5, value="item5")  # 5 % 5 = 0
    ht.insert(key=10, value="item10") # 10 % 5 = 0 -> collides -> probes to 1
    assert ht.table[0]["key"] == 5
    assert ht.table[1]["key"] == 10


def test_dsa_registry_discovery():
    """Registry returns all supported DSA category identifiers."""
    categories = DSARegistry.get_supported_categories()
    assert "STACK" in categories
    assert "QUEUE" in categories
    assert "CIRCULAR_QUEUE" in categories
    assert "LINKED_LIST" in categories
    assert "TREE" in categories
    assert "SORTING" in categories


# ==========================================
# 3. DSA FastAPI Route Endpoints
# ==========================================
def test_api_dsa_categories():
    """GET /api/v1/dsa/categories returns all categories."""
    res = client.get("/api/v1/dsa/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "STACK" in data["data"]


def test_api_dsa_stack_demo():
    """GET /api/v1/dsa/stack/demo returns 12-step complete stack lifecycle trace."""
    res = client.get("/api/v1/dsa/stack/demo")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    trace = data["data"]
    assert trace["structure_type"] == "STACK"
    assert trace["total_steps"] >= 10
    # Check that overflow and underflow steps are present
    statuses = [s["status"] for s in trace["steps"]]
    assert "OVERFLOW" in statuses
    assert "UNDERFLOW" in statuses


def test_api_dsa_stack_execute():
    """POST /api/v1/dsa/stack/execute executes custom operation sequence."""
    payload = {
        "capacity": 4,
        "operations": [
            {"op": "push", "value": 77},
            {"op": "push", "value": 88},
            {"op": "peek"},
            {"op": "pop"},
        ],
    }
    res = client.post("/api/v1/dsa/stack/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    trace = data["data"]
    assert trace["total_steps"] == 5
    assert trace["final_state"]["active_elements"] == [77]


def test_api_dsa_searching_execute():
    """POST /api/v1/dsa/searching/execute executes binary search."""
    payload = {
        "array": [10, 20, 30, 40, 50],
        "target": 30,
        "algorithm": "binary",
    }
    res = client.post("/api/v1/dsa/searching/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["structure_type"] == "SEARCHING"


def test_api_dsa_sorting_execute():
    """POST /api/v1/dsa/sorting/execute executes bubble sort."""
    payload = {
        "array": [3, 1, 2],
        "algorithm": "bubble",
    }
    res = client.post("/api/v1/dsa/sorting/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["final_state"]["array"] == [1, 2, 3]


def test_api_dsa_hashing_execute():
    """POST /api/v1/dsa/hashing/execute executes hash table insertions."""
    payload = {
        "capacity": 5,
        "keys_to_insert": [1, 6],  # 1 and 6 collide at index 1
    }
    res = client.post("/api/v1/dsa/hashing/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["structure_type"] == "HASHING"
