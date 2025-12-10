"""
Ape Runtime Explanation Engine

Converts execution traces into human-readable explanations.
Fully deterministic, no LLM required - pure interpretation of trace events.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from ape.runtime.trace import TraceCollector, TraceEvent


@dataclass
class ExplanationStep:
    """
    Single step in execution explanation.
    
    Human-readable interpretation of a TraceEvent or sequence of events.
    
    Attributes:
        index: Step number in sequence (0-indexed)
        node_type: Type of AST node (IF, WHILE, FOR, etc.)
        summary: One-line human-readable summary
        details: Additional structured information about the step
    """
    index: int
    node_type: str
    summary: str
    details: Dict[str, Any]
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"ExplanationStep({self.index}: {self.node_type} - {self.summary})"


class ExplanationEngine:
    """
    Generates human-readable explanations from execution traces.
    
    Design principles:
    - Fully deterministic (no LLM, no randomness)
    - Pure interpretation of trace events
    - Context-aware explanations based on node type
    - Handles enter/exit symmetry
    - Supports all APE control flow structures
    
    The engine converts low-level TraceEvents into high-level narrative
    descriptions suitable for debugging, auditing, and learning.
    """
    
    def __init__(self):
        """Initialize explanation engine"""
        pass
    
    def from_trace(self, trace: TraceCollector) -> List[ExplanationStep]:
        """
        Generate explanations from execution trace.
        
        Converts TraceEvents into human-readable ExplanationSteps.
        Pairs enter/exit events and generates context-aware summaries.
        
        Args:
            trace: TraceCollector with recorded events
            
        Returns:
            List of ExplanationStep objects in execution order
        """
        events = trace.events()
        explanations = []
        
        # Track paired enter/exit events
        i = 0
        step_index = 0
        
        while i < len(events):
            event = events[i]
            
            # Look ahead for matching exit event
            exit_event = None
            if event.phase == "enter" and i + 1 < len(events):
                next_event = events[i + 1]
                if next_event.phase == "exit" and next_event.node_type == event.node_type:
                    exit_event = next_event
            
            # Generate explanation for this event (pair)
            explanation = self._explain_event(event, exit_event, step_index)
            explanations.append(explanation)
            
            # Advance past both enter and exit if paired
            if exit_event:
                i += 2
            else:
                i += 1
            
            step_index += 1
        
        return explanations
    
    def _explain_event(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """
        Generate explanation for a single event or event pair.
        
        Args:
            enter_event: The enter event (or standalone event)
            exit_event: The matching exit event (if any)
            index: Step index in sequence
            
        Returns:
            ExplanationStep with context-aware summary
        """
        node_type = enter_event.node_type
        
        # Dispatch to node-specific explainer
        if node_type == "IF":
            return self._explain_if(enter_event, exit_event, index)
        elif node_type == "WHILE":
            return self._explain_while(enter_event, exit_event, index)
        elif node_type == "FOR":
            return self._explain_for(enter_event, exit_event, index)
        elif node_type == "STEP":
            return self._explain_step(enter_event, exit_event, index)
        elif node_type == "EXPRESSION":
            return self._explain_expression(enter_event, exit_event, index)
        elif node_type in ("MODULE", "TASKDEF", "FLOWDEF"):
            return self._explain_definition(enter_event, exit_event, index)
        else:
            return self._explain_generic(enter_event, exit_event, index)
    
    def _explain_if(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain IF node execution"""
        metadata = enter_event.metadata
        condition_result = metadata.get("condition_result", False)
        branch_taken = metadata.get("branch_taken", "then")
        
        if condition_result:
            summary = f"Condition evaluated to true → entered {branch_taken} branch"
        else:
            summary = f"Condition evaluated to false → entered {branch_taken} branch"
        
        details = {
            "condition_result": condition_result,
            "branch_taken": branch_taken,
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, "IF", summary, details)
    
    def _explain_while(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain WHILE node execution"""
        metadata = enter_event.metadata
        iterations = metadata.get("iterations", 0)
        final_condition = metadata.get("final_condition_result", False)
        
        if iterations == 0:
            summary = "Loop condition was false → body not executed"
        elif final_condition:
            summary = f"Loop continued because condition remained true (iteration {iterations})"
        else:
            summary = f"Loop terminated after {iterations} iterations (condition became false)"
        
        details = {
            "iterations": iterations,
            "final_condition": final_condition,
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, "WHILE", summary, details)
    
    def _explain_for(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain FOR node execution"""
        metadata = enter_event.metadata
        collection_size = metadata.get("collection_size", 0)
        loop_var = metadata.get("loop_var", "item")
        iterations = metadata.get("iterations", 0)
        
        if collection_size == 0:
            summary = "Iterating over empty collection → body not executed"
        elif iterations == 1:
            summary = f"Iterating over collection of {collection_size} items (iteration {iterations})"
        else:
            summary = f"Iterating over collection of {collection_size} items (iteration {iterations})"
        
        details = {
            "collection_size": collection_size,
            "loop_variable": loop_var,
            "iterations": iterations,
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, "FOR", summary, details)
    
    def _explain_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain STEP node execution"""
        metadata = enter_event.metadata
        step_name = metadata.get("name", "unnamed")
        
        # Check if this is a dry-run
        is_dry_run = metadata.get("dry_run", False)
        
        if is_dry_run:
            summary = f"Step '{step_name}' analyzed (dry-run, no execution)"
        else:
            summary = f"Executed step '{step_name}'"
        
        details = {
            "step_name": step_name,
            "dry_run": is_dry_run,
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, "STEP", summary, details)
    
    def _explain_expression(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain EXPRESSION node execution"""
        metadata = enter_event.metadata
        var_name = metadata.get("variable", "result")
        value = exit_event.result if exit_event else None
        is_dry_run = metadata.get("dry_run", False)
        
        if is_dry_run:
            summary = f"Variable '{var_name}' would be set to {value} (dry-run)"
        else:
            summary = f"Variable '{var_name}' set to {value}"
        
        details = {
            "variable": var_name,
            "value": value,
            "dry_run": is_dry_run,
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, "EXPRESSION", summary, details)
    
    def _explain_definition(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain MODULE/TASKDEF/FLOWDEF node execution"""
        node_type = enter_event.node_type
        metadata = enter_event.metadata
        name = metadata.get("name", "unnamed")
        
        if node_type == "MODULE":
            summary = f"Entering module '{name}'"
        elif node_type == "TASKDEF":
            summary = f"Defining task '{name}'"
        else:  # FLOWDEF
            summary = f"Defining flow '{name}'"
        
        details = {
            "name": name,
            "type": node_type.lower(),
            "variables_before": enter_event.context_snapshot,
            "variables_after": exit_event.context_snapshot if exit_event else {}
        }
        
        return ExplanationStep(index, node_type, summary, details)
    
    def _explain_generic(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        index: int
    ) -> ExplanationStep:
        """Explain unknown/generic node execution"""
        node_type = enter_event.node_type
        phase = enter_event.phase
        
        summary = f"{phase.capitalize()} {node_type} node"
        
        details = {
            "phase": phase,
            "variables": enter_event.context_snapshot,
            "result": exit_event.result if exit_event else None,
            "metadata": enter_event.metadata
        }
        
        return ExplanationStep(index, node_type, summary, details)


__all__ = [
    'ExplanationStep',
    'ExplanationEngine',
]
