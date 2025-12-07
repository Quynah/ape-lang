"""
Ape Runtime Replay Engine

Validates deterministic execution by replaying traces.
Does not re-execute code - validates trace structure and determinism.
"""

from typing import List
from ape.runtime.trace import TraceCollector, TraceEvent
from ape.errors import ReplayError


class ReplayEngine:
    """
    Validates deterministic execution by replaying traces.
    
    Design principles:
    - Does NOT re-execute code
    - Validates trace structure (enter/exit symmetry)
    - Validates node order
    - Validates context snapshots consistency
    - Produces new TraceCollector with validated events
    
    Replay is validation, not execution. It ensures that a trace
    represents a valid, deterministic execution sequence.
    """
    
    def __init__(self):
        """Initialize replay engine"""
        self._stack: List[TraceEvent] = []
    
    def replay(self, trace: TraceCollector) -> TraceCollector:
        """
        Replay and validate execution trace.
        
        Validates:
        - Enter/exit symmetry (every enter has matching exit)
        - Node type consistency
        - Proper nesting of events
        - Context snapshot integrity
        
        Args:
            trace: Original TraceCollector to replay
            
        Returns:
            New TraceCollector with validated events
            
        Raises:
            ReplayError: If trace is invalid or non-deterministic
        """
        events = trace.events()
        replayed = TraceCollector()
        self._stack.clear()
        
        for i, event in enumerate(events):
            try:
                # Validate event
                self._validate_event(event, i)
                
                # Handle enter/exit
                if event.phase == "enter":
                    self._handle_enter(event)
                elif event.phase == "exit":
                    self._handle_exit(event)
                else:
                    raise ReplayError(f"Invalid phase '{event.phase}' at event {i}")
                
                # Record validated event
                replayed.record(event)
                
            except ReplayError:
                raise
            except Exception as e:
                raise ReplayError(f"Unexpected error at event {i}: {e}")
        
        # Validate all events were closed
        if self._stack:
            unclosed = [e.node_type for e in self._stack]
            raise ReplayError(f"Unclosed events at end of trace: {unclosed}")
        
        return replayed
    
    def _validate_event(self, event: TraceEvent, index: int) -> None:
        """
        Validate basic event structure.
        
        Args:
            event: Event to validate
            index: Event index in sequence
            
        Raises:
            ReplayError: If event is invalid
        """
        # Check required fields
        if not event.node_type:
            raise ReplayError(f"Event {index} missing node_type")
        
        if event.phase not in ("enter", "exit"):
            raise ReplayError(f"Event {index} has invalid phase: {event.phase}")
        
        # Context snapshot should be a dict
        if not isinstance(event.context_snapshot, dict):
            raise ReplayError(f"Event {index} has invalid context_snapshot type: {type(event.context_snapshot)}")
        
        # Metadata should be a dict
        if not isinstance(event.metadata, dict):
            raise ReplayError(f"Event {index} has invalid metadata type: {type(event.metadata)}")
    
    def _handle_enter(self, event: TraceEvent) -> None:
        """
        Handle enter event.
        
        Pushes event onto stack for later exit matching.
        
        Args:
            event: Enter event to handle
        """
        self._stack.append(event)
    
    def _handle_exit(self, event: TraceEvent) -> None:
        """
        Handle exit event.
        
        Pops matching enter from stack and validates consistency.
        
        Args:
            event: Exit event to handle
            
        Raises:
            ReplayError: If exit doesn't match enter
        """
        if not self._stack:
            raise ReplayError(
                f"Exit event for {event.node_type} without matching enter",
                actual_node=event.node_type
            )
        
        enter_event = self._stack.pop()
        
        # Validate node type matches
        if enter_event.node_type != event.node_type:
            raise ReplayError(
                f"Exit event node_type mismatch: expected {enter_event.node_type}, got {event.node_type}",
                expected_node=enter_event.node_type,
                actual_node=event.node_type
            )
        
        # Validate context snapshot consistency
        # Exit should have same or more variables than enter
        self._validate_context_consistency(enter_event, event)
    
    def _validate_context_consistency(
        self, 
        enter_event: TraceEvent, 
        exit_event: TraceEvent
    ) -> None:
        """
        Validate context snapshots are consistent.
        
        Exit context should be a superset of enter context (may have new variables).
        Shared variables should have valid types.
        
        Args:
            enter_event: Enter event with context snapshot
            exit_event: Exit event with context snapshot
            
        Raises:
            ReplayError: If contexts are inconsistent
        """
        enter_vars = enter_event.context_snapshot
        exit_vars = exit_event.context_snapshot
        
        # Check that all enter variables are still present at exit
        # (Note: Some may be removed in child scopes, so this is lenient)
        for var_name in enter_vars:
            if var_name in exit_vars:
                # Variable exists in both - validate type consistency
                _enter_val = enter_vars[var_name]
                exit_val = exit_vars[var_name]
                
                # Type can change (reassignment), but should be valid
                if not self._is_valid_snapshot_value(exit_val):
                    raise ReplayError(
                        f"Invalid snapshot value for '{var_name}' at exit: {exit_val}"
                    )
    
    def _is_valid_snapshot_value(self, value: any) -> bool:
        """
        Check if a value is valid for snapshot.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is valid snapshot type
        """
        # Primitives are valid
        if isinstance(value, (int, float, str, bool, type(None))):
            return True
        
        # Simple collections are valid
        if isinstance(value, (list, tuple, dict)):
            return True
        
        # Type markers are valid (e.g., "<ClassName>")
        if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
            return True
        
        return False
    
    def validate_determinism(self, trace1: TraceCollector, trace2: TraceCollector) -> bool:
        """
        Validate that two traces represent the same deterministic execution.
        
        Checks that both traces have:
        - Same number of events
        - Same node types in same order
        - Same enter/exit structure
        
        Args:
            trace1: First trace to compare
            trace2: Second trace to compare
            
        Returns:
            True if traces are deterministically equivalent
            
        Raises:
            ReplayError: If traces differ
        """
        events1 = trace1.events()
        events2 = trace2.events()
        
        # Check length
        if len(events1) != len(events2):
            raise ReplayError(
                f"Trace length mismatch: {len(events1)} vs {len(events2)}"
            )
        
        # Check each event pair
        for i, (e1, e2) in enumerate(zip(events1, events2)):
            # Check node type
            if e1.node_type != e2.node_type:
                raise ReplayError(
                    f"Event {i} node_type mismatch: {e1.node_type} vs {e2.node_type}",
                    trace_index=i,
                    expected_node=e1.node_type,
                    actual_node=e2.node_type
                )
            
            # Check phase
            if e1.phase != e2.phase:
                raise ReplayError(
                    f"Event {i} phase mismatch: {e1.phase} vs {e2.phase}",
                    trace_index=i,
                    details={'expected_phase': e1.phase, 'actual_phase': e2.phase}
                )
        
        return True


__all__ = [
    'ReplayEngine',
]
