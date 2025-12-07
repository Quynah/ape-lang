"""
Ape Runtime Explanation Engine

Converts execution traces into human-readable explanations.
Fully deterministic, no LLM required - pure interpretation of trace events.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
from ape.runtime.trace import TraceCollector, TraceEvent


@dataclass
class ExplanationStep:
    """
    Single step in execution explanation.
    
    Human-readable interpretation of a TraceEvent or sequence of events.
    
    Attributes:
        step: Step identifier (node execution path)
        action: What action was performed
        reason: Why the action was performed
        inputs: Input values/context for this step
        outputs: Output values/results from this step
    """
    step: str
    action: str
    reason: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for stable serialization"""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"ExplanationStep({self.step}: {self.action})"
    
    # Backwards compatibility properties
    @property
    def node_type(self) -> str:
        """Legacy property for backwards compatibility - extract from step"""
        return self.step.split('_')[0] if '_' in self.step else self.step
    
    @property
    def summary(self) -> str:
        """Legacy property for backwards compatibility - combine action and reason"""
        return f"{self.action} ({self.reason})"
    
    @property
    def index(self) -> int:
        """Legacy property for backwards compatibility - extract from step"""
        parts = self.step.split('_')
        return int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else 0
    
    @property
    def details(self) -> Dict[str, Any]:
        """Legacy property for backwards compatibility - combine inputs/outputs"""
        return {**self.inputs, **self.outputs}


@dataclass
class ExplanationOutput:
    """
    Complete explanation output with stable schema.
    
    Schema guarantees:
    - All keys always present
    - Empty arrays instead of None
    - Deterministic ordering
    - Machine-readable format
    
    Attributes:
        trace_id: Trace identifier for observability
        status: Execution status
        decisions: List of decision steps
        errors: List of errors encountered
    """
    trace_id: str
    status: Literal["executed", "dry_run", "rejected", "failed"]
    decisions: List[ExplanationStep] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with stable schema"""
        return {
            "trace_id": self.trace_id,
            "status": self.status,
            "decisions": [step.to_dict() for step in self.decisions],
            "errors": self.errors
        }


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
    
    def explain(self, trace: TraceCollector, status: str = "executed") -> ExplanationOutput:
        """
        Generate stable explanation output from execution trace.
        
        Returns a structured ExplanationOutput with guaranteed schema.
        
        Args:
            trace: TraceCollector with recorded events
            status: Execution status ("executed", "dry_run", "rejected", "failed")
            
        Returns:
            ExplanationOutput with stable schema
        """
        events = trace.events()
        decisions = []
        errors = []
        
        # Track paired enter/exit events
        i = 0
        step_counter = 0
        
        while i < len(events):
            event = events[i]
            
            # Look ahead for matching exit event
            exit_event = None
            if event.phase == "enter" and i + 1 < len(events):
                next_event = events[i + 1]
                if next_event.phase == "exit" and next_event.node_type == event.node_type:
                    exit_event = next_event
            
            # Check for errors in metadata
            if event.metadata.get("error"):
                errors.append({
                    "step": f"{event.node_type}_{step_counter}",
                    "error": str(event.metadata.get("error")),
                    "context": event.context_snapshot
                })
            
            # Generate explanation for this event (pair)
            explanation = self._explain_event_to_step(event, exit_event, step_counter)
            if explanation:
                decisions.append(explanation)
            
            # Advance past both enter and exit if paired
            if exit_event:
                i += 2
            else:
                i += 1
            
            step_counter += 1
        
        return ExplanationOutput(
            trace_id=trace.trace_id,
            status=status,
            decisions=decisions,
            errors=errors
        )
    
    def from_trace(self, trace: TraceCollector) -> List[ExplanationStep]:
        """
        Legacy method for backwards compatibility.
        
        Use explain() for new code to get stable schema.
        
        Args:
            trace: TraceCollector with recorded events
            
        Returns:
            List of ExplanationStep objects
        """
        output = self.explain(trace)
        return output.decisions
    
    def _explain_event_to_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        step_index: int
    ) -> Optional[ExplanationStep]:
        """
        Generate explanation step for an event or event pair.
        
        Args:
            enter_event: The enter event (or standalone event)
            exit_event: The matching exit event (if any)
            step_index: Step index in sequence
            
        Returns:
            ExplanationStep or None if no explanation needed
        """
        node_type = enter_event.node_type
        
        # Dispatch to node-specific explainer
        if node_type == "IfNode":
            return self._explain_if_step(enter_event, exit_event, step_index)
        elif node_type == "WhileNode":
            return self._explain_while_step(enter_event, exit_event, step_index)
        elif node_type == "ForNode":
            return self._explain_for_step(enter_event, exit_event, step_index)
        elif node_type == "ExpressionNode":
            return self._explain_expression_step(enter_event, exit_event, step_index)
        else:
            # Generic explanation
            return ExplanationStep(
                step=f"{node_type}_{step_index}",
                action=f"Execute {node_type}",
                reason="Control flow node",
                inputs=enter_event.context_snapshot,
                outputs=exit_event.context_snapshot if exit_event else {}
            )
    
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
    
    def _explain_if_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        step_index: int
    ) -> ExplanationStep:
        """Explain IF node execution as step"""
        metadata = enter_event.metadata
        condition_result = metadata.get("condition_result", False)
        branch_taken = metadata.get("branch_taken", "then")
        
        return ExplanationStep(
            step=f"IF_{step_index}",
            action=f"Evaluate condition and enter {branch_taken} branch",
            reason=f"Condition evaluated to {condition_result}",
            inputs=enter_event.context_snapshot,
            outputs=exit_event.context_snapshot if exit_event else {}
        )
    
    def _explain_while_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        step_index: int
    ) -> ExplanationStep:
        """Explain WHILE node execution as step"""
        metadata = enter_event.metadata
        iterations = metadata.get("iterations", 0)
        
        return ExplanationStep(
            step=f"WHILE_{step_index}",
            action=f"Execute loop ({iterations} iterations)",
            reason="Loop condition was true",
            inputs=enter_event.context_snapshot,
            outputs=exit_event.context_snapshot if exit_event else {}
        )
    
    def _explain_for_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        step_index: int
    ) -> ExplanationStep:
        """Explain FOR node execution as step"""
        metadata = enter_event.metadata
        iterations = metadata.get("iterations", 0)
        
        return ExplanationStep(
            step=f"FOR_{step_index}",
            action=f"Iterate over collection ({iterations} items)",
            reason="Iterating collection",
            inputs=enter_event.context_snapshot,
            outputs=exit_event.context_snapshot if exit_event else {}
        )
    
    def _explain_expression_step(
        self, 
        enter_event: TraceEvent, 
        exit_event: Optional[TraceEvent],
        step_index: int
    ) -> ExplanationStep:
        """Explain EXPRESSION node execution as step"""
        result = exit_event.result if exit_event else None
        
        return ExplanationStep(
            step=f"EXPR_{step_index}",
            action="Evaluate expression",
            reason="Expression evaluation",
            inputs=enter_event.context_snapshot,
            outputs={"result": result}
        )
    
    def from_trace(self, trace: 'TraceCollector') -> List[ExplanationStep]:
        """
        Legacy method for backwards compatibility.
        
        Converts trace to list of explanation steps using old format.
        New code should use explain() which returns ExplanationOutput.
        
        Args:
            trace: TraceCollector with recorded events
            
        Returns:
            List of ExplanationStep objects (new format, compatible with old tests)
        """
        explanation = self.explain(trace, status="executed")
        return explanation.decisions


__all__ = [
    'ExplanationStep',
    'ExplanationOutput',
    'ExplanationEngine',
]
