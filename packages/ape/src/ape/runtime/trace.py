"""
Ape Runtime Execution Tracing

Provides observability into runtime execution without affecting deterministic behavior.
Traces can be used for debugging, auditing, and understanding program flow.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
from copy import deepcopy


@dataclass
class TraceEvent:
    """
    Single event in execution trace.
    
    Records entry/exit points during AST node execution with context snapshot.
    Snapshots are shallow copies to avoid reference leaks.
    
    Attributes:
        node_type: Type of AST node being executed
        phase: Whether this is entry or exit from node
        context_snapshot: Shallow copy of variables (primitives only)
        result: Result value (for exit events)
        metadata: Additional event-specific data
    """
    node_type: str
    phase: Literal["enter", "exit"]
    context_snapshot: Dict[str, Any]
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"TraceEvent({self.phase} {self.node_type}, vars={list(self.context_snapshot.keys())})"


class TraceCollector:
    """
    Collects execution trace events during runtime.
    
    Non-intrusive observation that does not affect deterministic execution.
    All snapshots are shallow copies of primitive values only.
    
    Design principles:
    - No reference leaks (shallow copy primitives)
    - No side effects on execution
    - Minimal performance impact
    - Can be enabled/disabled without code changes
    """
    
    def __init__(self):
        """Initialize empty trace collector"""
        self._events: List[TraceEvent] = []
    
    def record(self, event: TraceEvent) -> None:
        """
        Record an execution event.
        
        Args:
            event: TraceEvent to record
        """
        self._events.append(event)
    
    def events(self) -> List[TraceEvent]:
        """
        Get all recorded events.
        
        Returns:
            List of all TraceEvent objects
        """
        return self._events.copy()
    
    def clear(self) -> None:
        """Clear all recorded events"""
        self._events.clear()
    
    def __len__(self) -> int:
        """Number of recorded events"""
        return len(self._events)
    
    def __bool__(self) -> bool:
        """TraceCollector is always truthy (even with 0 events)"""
        return True
    
    def __repr__(self) -> str:
        """String representation"""
        return f"TraceCollector({len(self._events)} events)"


def create_snapshot(context: Any) -> Dict[str, Any]:
    """
    Create a safe snapshot of execution context variables.
    
    Only includes primitive types and simple collections to avoid
    reference leaks and ensure deterministic behavior.
    
    Args:
        context: ExecutionContext to snapshot
        
    Returns:
        Dictionary with shallow copy of safe values
    """
    if not hasattr(context, 'variables'):
        return {}
    
    snapshot = {}
    for key, value in context.variables.items():
        # Only snapshot safe primitive types
        if isinstance(value, (int, float, str, bool, type(None))):
            snapshot[key] = value
        elif isinstance(value, (list, tuple)):
            # Shallow copy for simple lists/tuples
            try:
                snapshot[key] = type(value)(v for v in value if isinstance(v, (int, float, str, bool, type(None))))
            except:
                snapshot[key] = f"<{type(value).__name__}>"
        elif isinstance(value, dict):
            # Shallow copy for simple dicts
            try:
                snapshot[key] = {k: v for k, v in value.items() if isinstance(v, (int, float, str, bool, type(None)))}
            except:
                snapshot[key] = f"<{type(value).__name__}>"
        else:
            # Complex types get type name only
            snapshot[key] = f"<{type(value).__name__}>"
    
    return snapshot


__all__ = [
    'TraceEvent',
    'TraceCollector',
    'create_snapshot',
]
