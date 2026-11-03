"""
Deterministic Stack ADT Implementation.
Provides bounded array-backed Stack with explicit overflow/underflow detection,
atomic timeline recording, and state snapshots for React frontend visualization.
"""

from typing import List, Dict, Any, Optional
from app.dsa.base import BaseDataStructure, DSACategory, TraceStepStatus, VisualizationTrace


class StackOverflowError(Exception):
    """Raised when attempting to push onto a saturated Stack ADT."""
    pass


class StackUnderflowError(Exception):
    """Raised when attempting to pop or peek an empty Stack ADT."""
    pass


class DeterministicStack(BaseDataStructure):
    """
    Bounded Array Implementation of the Stack ADT (LIFO: Last-In, First-Out).
    Maintains internal top pointer, bounded capacity, and records discrete visual states.
    """

    DEFAULT_CAPACITY = 5

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        super().__init__(category=DSACategory.STACK, capacity=capacity)
        self.capacity = max(1, capacity)
        self.elements: List[Optional[Any]] = [None] * self.capacity
        self.top: int = -1
        self._initial_state = self.snapshot()

        # Record initial creation step
        self.record_step(
            operation="INITIALIZE",
            description=f"Initialized an empty stack with bounded capacity of {self.capacity}.",
            variables={"capacity": self.capacity, "top": self.top, "size": 0},
            prev_state=None,
            updated_state=self.snapshot(),
            top_position=self.top,
            final_result=None,
            highlighted_indices=[],
            status=TraceStepStatus.SUCCESS,
        )

    def snapshot(self) -> Dict[str, Any]:
        """Creates an isolated snapshot of stack contents and pointer metadata."""
        active_elements = [self.elements[i] for i in range(self.top + 1)] if self.top >= 0 else []
        return {
            "elements": [x for x in self.elements],  # Full array representation including None slots
            "active_elements": active_elements,      # Currently valid stack items
            "top": self.top,
            "size": self.top + 1,
            "capacity": self.capacity,
            "is_empty": self.top == -1,
            "is_full": self.top == self.capacity - 1,
        }

    def reset(self) -> None:
        """Resets the stack to an empty initial state."""
        self.elements = [None] * self.capacity
        self.top = -1
        self.steps = []
        self._initial_state = self.snapshot()
        self.record_step(
            operation="RESET",
            description="Stack reset to initial empty state.",
            variables={"capacity": self.capacity, "top": self.top, "size": 0},
            prev_state=None,
            updated_state=self.snapshot(),
            top_position=self.top,
            final_result=None,
            highlighted_indices=[],
            status=TraceStepStatus.SUCCESS,
        )

    def is_empty(self) -> bool:
        """Checks whether the stack contains zero elements."""
        prev = self.snapshot()
        result = self.top == -1
        self.record_step(
            operation="ISEMPTY()",
            description=f"Checked if stack is empty: top == -1 evaluates to {result}.",
            variables={"top": self.top, "capacity": self.capacity, "result": result},
            prev_state=prev,
            updated_state=self.snapshot(),
            top_position=self.top,
            final_result=result,
            highlighted_indices=[self.top] if self.top >= 0 else [],
            status=TraceStepStatus.SUCCESS,
        )
        return result

    def is_full(self) -> bool:
        """Checks whether the stack has reached maximum capacity."""
        prev = self.snapshot()
        result = self.top == self.capacity - 1
        self.record_step(
            operation="ISFULL()",
            description=f"Checked if stack is full: top == capacity - 1 ({self.capacity - 1}) evaluates to {result}.",
            variables={"top": self.top, "capacity": self.capacity, "result": result},
            prev_state=prev,
            updated_state=self.snapshot(),
            top_position=self.top,
            final_result=result,
            highlighted_indices=[self.top] if self.top >= 0 else [],
            status=TraceStepStatus.SUCCESS,
        )
        return result

    def push(self, value: Any) -> bool:
        """
        Pushes a new value onto the top of the stack.
        Detects overflow if the stack is already saturated.
        """
        prev = self.snapshot()

        # Overflow detection check
        if self.top >= self.capacity - 1:
            self.record_step(
                operation=f"PUSH({value})",
                description=(
                    f"Stack Overflow detected! Cannot push element '{value}'. "
                    f"Top index ({self.top}) has reached maximum array capacity ({self.capacity}). "
                    f"In Java, this requires array resizing or throwing an exception."
                ),
                variables={"attempted_value": value, "top": self.top, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                top_position=self.top,
                final_result="OVERFLOW_ERROR",
                highlighted_indices=[self.top],
                status=TraceStepStatus.OVERFLOW,
            )
            return False

        # Execute deterministic push transition
        self.top += 1
        self.elements[self.top] = value
        curr = self.snapshot()

        self.record_step(
            operation=f"PUSH({value})",
            description=(
                f"Incremented top pointer from {self.top - 1} to {self.top}, "
                f"and inserted value '{value}' into elements[{self.top}]."
            ),
            variables={
                "pushed_value": value,
                "previous_top": self.top - 1,
                "updated_top": self.top,
                "size": self.top + 1,
            },
            prev_state=prev,
            updated_state=curr,
            top_position=self.top,
            final_result=value,
            highlighted_indices=[self.top],
            status=TraceStepStatus.SUCCESS,
        )
        return True

    def pop(self) -> Optional[Any]:
        """
        Pops and returns the element at the top of the stack.
        Detects underflow if the stack is empty.
        """
        prev = self.snapshot()

        # Underflow detection check
        if self.top == -1:
            self.record_step(
                operation="POP()",
                description=(
                    "Stack Underflow detected! Cannot pop from an empty stack (top == -1). "
                    "In Java, calling pop() on java.util.Stack throws EmptyStackException."
                ),
                variables={"top": self.top, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                top_position=self.top,
                final_result="UNDERFLOW_ERROR",
                highlighted_indices=[],
                status=TraceStepStatus.UNDERFLOW,
            )
            return None

        # Execute deterministic pop transition
        popped_value = self.elements[self.top]
        self.elements[self.top] = None
        removed_top = self.top
        self.top -= 1
        curr = self.snapshot()

        self.record_step(
            operation="POP()",
            description=(
                f"Retrieved element '{popped_value}' at index {removed_top}, "
                f"cleared elements[{removed_top}], and decremented top pointer to {self.top}."
            ),
            variables={
                "popped_value": popped_value,
                "previous_top": removed_top,
                "updated_top": self.top,
                "size": self.top + 1,
            },
            prev_state=prev,
            updated_state=curr,
            top_position=self.top,
            final_result=popped_value,
            highlighted_indices=[removed_top],
            status=TraceStepStatus.SUCCESS,
        )
        return popped_value

    def peek(self) -> Optional[Any]:
        """
        Observes the top element without removing it.
        Detects underflow if the stack is empty.
        """
        prev = self.snapshot()

        # Underflow detection check
        if self.top == -1:
            self.record_step(
                operation="PEEK()",
                description=(
                    "Stack Underflow detected! Cannot peek into an empty stack (top == -1). "
                    "In Java, calling peek() on an empty stack throws EmptyStackException."
                ),
                variables={"top": self.top, "capacity": self.capacity},
                prev_state=prev,
                updated_state=prev,
                top_position=self.top,
                final_result="UNDERFLOW_ERROR",
                highlighted_indices=[],
                status=TraceStepStatus.UNDERFLOW,
            )
            return None

        # Execute peek
        top_value = self.elements[self.top]
        self.record_step(
            operation="PEEK()",
            description=f"Observed top element '{top_value}' at index {self.top} without modifying stack state.",
            variables={"top_value": top_value, "top": self.top, "size": self.top + 1},
            prev_state=prev,
            updated_state=self.snapshot(),
            top_position=self.top,
            final_result=top_value,
            highlighted_indices=[self.top],
            status=TraceStepStatus.SUCCESS,
        )
        return top_value

    def execute_sequence(self, operations: List[Dict[str, Any]]) -> VisualizationTrace:
        """
        Executes an ordered batch of operations (e.g. push, pop, peek, is_empty, is_full).
        Returns a complete multi-step VisualizationTrace.
        """
        for item in operations:
            op_name = item.get("op", "").lower()
            val = item.get("value")

            if op_name == "push":
                self.push(val)
            elif op_name == "pop":
                self.pop()
            elif op_name == "peek":
                self.peek()
            elif op_name == "is_empty":
                self.is_empty()
            elif op_name == "is_full":
                self.is_full()
            elif op_name == "reset":
                self.reset()

        return self.get_trace(metadata={"operation_count": len(operations)})

