"""
Base Framework for Deterministic DSA Visualization Engine.
Provides abstract specifications for data structures, timeline trace steps,
and serialization contracts for React visualization components.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DSACategory(str, Enum):
    """Supported computational and structural categories."""
    STACK = "STACK"
    ARRAY = "ARRAY"
    QUEUE = "QUEUE"
    CIRCULAR_QUEUE = "CIRCULAR_QUEUE"
    LINKED_LIST = "LINKED_LIST"
    TREE = "TREE"
    GRAPH = "GRAPH"
    SEARCHING = "SEARCHING"
    SORTING = "SORTING"
    HASHING = "HASHING"


class TraceStepStatus(str, Enum):
    """Status flags for an algorithm trace transition."""
    SUCCESS = "SUCCESS"
    OVERFLOW = "OVERFLOW"
    UNDERFLOW = "UNDERFLOW"
    ELEMENT_FOUND = "ELEMENT_FOUND"
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    SWAP = "SWAP"
    COMPARISON = "COMPARISON"
    ERROR = "ERROR"


class TraceStep(BaseModel):
    """
    Individual atomic state transition along the algorithm timeline.
    Provides complete state preservation to support bidirectional step-through navigation.
    """
    step_index: int = Field(..., ge=0, description="Sequential index in trace timeline")
    current_operation: str = Field(..., description="e.g. PUSH(42), POP(), PEEK(), IS_EMPTY()")
    operation_description: str = Field(..., description="Pedagogical explanation of this step")
    variable_values: Dict[str, Any] = Field(default_factory=dict, description="Snapshot of internal variables")
    previous_state: Optional[Dict[str, Any]] = Field(default=None, description="State immediately prior to this operation")
    updated_state: Dict[str, Any] = Field(..., description="State immediately after this operation")
    current_top_position: Optional[int] = Field(default=None, description="Top index for stack, or primary focus index")
    final_result: Optional[Any] = Field(default=None, description="Return value or outcome of the operation")
    highlighted_indices: List[int] = Field(default_factory=list, description="Target indices for animation/highlighting")
    status: TraceStepStatus = Field(default=TraceStepStatus.SUCCESS)


class VisualizationTrace(BaseModel):
    """
    Complete algorithm execution trace consumable by the React frontend.
    Enables interactive timeline scrubbing, play/pause, and step-by-step state inspection.
    """
    structure_type: DSACategory
    capacity: Optional[int] = None
    total_steps: int
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    steps: List[TraceStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseDataStructure(ABC):
    """
    Abstract base class for all deterministic data structures in the learning engine.
    Mandates timeline recording and state snapshotting.
    """

    def __init__(self, category: DSACategory, capacity: Optional[int] = None):
        self.category = category
        self.capacity = capacity
        self.steps: List[TraceStep] = []
        self._initial_state: Dict[str, Any] = {}

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]:
        """Returns an immutable dictionary snapshot of the current internal state."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Resets the data structure to its initial empty state."""
        pass

    def record_step(
        self,
        operation: str,
        description: str,
        variables: Dict[str, Any],
        prev_state: Optional[Dict[str, Any]],
        updated_state: Dict[str, Any],
        top_position: Optional[int] = None,
        final_result: Optional[Any] = None,
        highlighted_indices: Optional[List[int]] = None,
        status: TraceStepStatus = TraceStepStatus.SUCCESS,
    ) -> TraceStep:
        """Appends an atomic state transition to the execution trace."""
        step = TraceStep(
            step_index=len(self.steps),
            current_operation=operation,
            operation_description=description,
            variable_values=variables,
            previous_state=prev_state,
            updated_state=updated_state,
            current_top_position=top_position,
            final_result=final_result,
            highlighted_indices=highlighted_indices or [],
            status=status,
        )
        self.steps.append(step)
        return step

    def get_trace(self, metadata: Optional[Dict[str, Any]] = None) -> VisualizationTrace:
        """Packages the execution history into a VisualizationTrace model."""
        return VisualizationTrace(
            structure_type=self.category,
            capacity=self.capacity,
            total_steps=len(self.steps),
            initial_state=self._initial_state,
            final_state=self.snapshot(),
            steps=self.steps,
            metadata=metadata or {},
        )

