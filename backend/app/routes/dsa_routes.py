"""
Deterministic DSA Visualization Routes.
Provides API endpoints to execute and trace algorithm operations,
returning structured JSON for interactive React visualization components.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.dsa import (
    DSACategory,
    VisualizationTrace,
    DSARegistry,
)
from app.utilities.response import ApiResponse, success_response


router = APIRouter()


class StackExecutionRequest(BaseModel):
    capacity: Optional[int] = Field(default=5, ge=1, le=50)
    operations: List[Dict[str, Any]] = Field(
        ...,
        description="List of operations, e.g. [{'op': 'push', 'value': 10}, {'op': 'pop'}]",
    )


class SearchExecutionRequest(BaseModel):
    array: List[int]
    target: int
    algorithm: str = Field(default="binary", description="'linear' or 'binary'")


class SortExecutionRequest(BaseModel):
    array: List[int]
    algorithm: str = Field(default="bubble", description="'bubble'")


class HashExecutionRequest(BaseModel):
    capacity: Optional[int] = Field(default=7, ge=1, le=100)
    keys_to_insert: List[int]


@router.get("/categories", response_model=ApiResponse[List[str]], summary="List all supported DSA categories")
def get_supported_categories():
    """Returns all data structures and algorithms supported by the visualization engine."""
    return success_response(
        data=DSARegistry.get_supported_categories(),
        message="Supported DSA categories retrieved",
    )


@router.post("/stack/execute", response_model=ApiResponse[VisualizationTrace], summary="Execute Stack operations and trace")
def execute_stack_trace(payload: StackExecutionRequest):
    """
    Executes a sequence of Stack ADT operations (push, pop, peek, is_empty, is_full)
    and returns a structured timeline trace with overflow and underflow awareness.
    """
    stack = DSARegistry.create_stack(capacity=payload.capacity or 5)
    trace = stack.execute_sequence(payload.operations)
    return success_response(
        data=trace,
        message=f"Executed {len(payload.operations)} stack operation(s) across {trace.total_steps} trace steps",
    )


@router.get("/stack/demo", response_model=ApiResponse[VisualizationTrace], summary="Get comprehensive Stack ADT demo trace")
def get_stack_demo_trace():
    """
    Returns a pre-recorded complete lifecycle trace demonstrating:
    push, pop, peek, is_empty, is_full, overflow detection, and underflow detection.
    """
    stack = DSARegistry.create_stack(capacity=3)
    stack.is_empty()
    stack.push(10)
    stack.push(20)
    stack.peek()
    stack.push(30)
    stack.is_full()
    stack.push(40)  # Overflow
    stack.pop()
    stack.pop()
    stack.pop()
    stack.pop()     # Underflow
    trace = stack.get_trace(metadata={"title": "IT22301 Stack ADT Comprehensive Demo"})
    return success_response(data=trace, message="Stack demo trace generated")


@router.post("/searching/execute", response_model=ApiResponse[VisualizationTrace], summary="Execute Search algorithm trace")
def execute_searching_trace(payload: SearchExecutionRequest):
    """Executes Linear or Binary search and captures comparison windows and indices."""
    engine = DSARegistry.create_searching(array=payload.array)
    if payload.algorithm.lower() == "linear":
        engine.linear_search(payload.target)
    else:
        # Sort for binary search
        engine.array.sort()
        engine.binary_search(payload.target)
    trace = engine.get_trace()
    return success_response(data=trace, message=f"Executed {payload.algorithm} search")


@router.post("/sorting/execute", response_model=ApiResponse[VisualizationTrace], summary="Execute Sorting algorithm trace")
def execute_sorting_trace(payload: SortExecutionRequest):
    """Executes Bubble sort and captures adjacent comparisons and swaps."""
    engine = DSARegistry.create_sorting(array=payload.array)
    engine.bubble_sort()
    trace = engine.get_trace()
    return success_response(data=trace, message="Executed sorting algorithm")


@router.post("/hashing/execute", response_model=ApiResponse[VisualizationTrace], summary="Execute Hashing trace")
def execute_hashing_trace(payload: HashExecutionRequest):
    """Executes Hash Table insertion with linear probing collision resolution."""
    engine = DSARegistry.create_hash_table(capacity=payload.capacity or 7)
    for k in payload.keys_to_insert:
        engine.insert(key=k, value=f"item_{k}")
    trace = engine.get_trace()
    return success_response(data=trace, message=f"Executed hashing with {len(payload.keys_to_insert)} key insertions")

