"""
APE Constraint Validation Runtime

Constraint checking for decision correctness and determinism.

Author: David Van Aelst
Status: Decision Engine v2024 - Complete
"""

from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import time


class ConstraintType(Enum):
    """Types of constraints"""
    PRECONDITION = "pre"      # Must be true before execution
    POSTCONDITION = "post"    # Must be true after execution
    INVARIANT = "inv"         # Must always be true
    DETERMINISM = "det"       # Must produce same output for same input
    PERFORMANCE = "perf"      # Must meet performance bounds


@dataclass
class Constraint:
    """Individual constraint"""
    name: str
    type: ConstraintType
    condition: str  # APE expression
    error_message: str = ""
    severity: str = "error"  # "error", "warning", "info"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintViolation:
    """Record of constraint violation"""
    constraint_name: str
    type: ConstraintType
    severity: str
    message: str
    context: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ValidationResult:
    """Result of constraint validation"""
    passed: bool
    violations: List[ConstraintViolation]
    warnings: List[ConstraintViolation]
    execution_time_ms: float
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return any(v.severity == "error" for v in self.violations)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings occurred"""
        return any(v.severity == "warning" for v in self.violations + self.warnings)


class ConstraintChecker:
    """
    Constraint validation engine.
    
    Validates preconditions, postconditions, invariants, determinism,
    and performance constraints for decision logic.
    
    Example:
        checker = ConstraintChecker()
        
        # Add precondition
        checker.add_constraint(
            "positive_amount",
            ConstraintType.PRECONDITION,
            "amount > 0",
            error_message="Amount must be positive"
        )
        
        # Add postcondition
        checker.add_constraint(
            "discount_valid",
            ConstraintType.POSTCONDITION,
            "discount >= 0 and discount <= 1",
            error_message="Discount must be between 0 and 1"
        )
        
        # Validate
        context = {"amount": 100}
        result = checker.validate_preconditions(context)
        
        # After execution
        outputs = {"discount": 0.15}
        result = checker.validate_postconditions(outputs)
    """
    
    def __init__(self):
        self.constraints: Dict[ConstraintType, List[Constraint]] = {
            ConstraintType.PRECONDITION: [],
            ConstraintType.POSTCONDITION: [],
            ConstraintType.INVARIANT: [],
            ConstraintType.DETERMINISM: [],
            ConstraintType.PERFORMANCE: []
        }
        self.enabled = True
        self.strict_mode = True  # Raise on errors vs collect violations
        
        # Determinism tracking
        self._execution_cache: Dict[str, Any] = {}
    
    def add_constraint(self, name: str, type: ConstraintType, condition: str,
                      error_message: str = "", severity: str = "error") -> None:
        """
        Add a constraint.
        
        Args:
            name: Unique constraint identifier
            type: Constraint type
            condition: APE expression to check
            error_message: Error message on violation
            severity: "error", "warning", or "info"
        """
        constraint = Constraint(
            name=name,
            type=type,
            condition=condition,
            error_message=error_message or f"Constraint '{name}' violated",
            severity=severity
        )
        self.constraints[type].append(constraint)
    
    def remove_constraint(self, name: str) -> bool:
        """Remove a constraint by name"""
        for type_constraints in self.constraints.values():
            original_len = len(type_constraints)
            type_constraints[:] = [c for c in type_constraints if c.name != name]
            if len(type_constraints) < original_len:
                return True
        return False
    
    def validate_preconditions(self, context: Dict[str, Any],
                               executor: Optional[Any] = None) -> ValidationResult:
        """
        Validate preconditions before execution.
        
        Args:
            context: Input variables
            executor: RuntimeExecutor instance
        
        Returns:
            ValidationResult with any violations
        """
        return self._validate_constraints(
            ConstraintType.PRECONDITION,
            context,
            executor
        )
    
    def validate_postconditions(self, context: Dict[str, Any],
                                executor: Optional[Any] = None) -> ValidationResult:
        """
        Validate postconditions after execution.
        
        Args:
            context: Output variables
            executor: RuntimeExecutor instance
        
        Returns:
            ValidationResult with any violations
        """
        return self._validate_constraints(
            ConstraintType.POSTCONDITION,
            context,
            executor
        )
    
    def validate_invariants(self, context: Dict[str, Any],
                           executor: Optional[Any] = None) -> ValidationResult:
        """
        Validate invariants (can be checked at any time).
        
        Args:
            context: Current state
            executor: RuntimeExecutor instance
        
        Returns:
            ValidationResult with any violations
        """
        return self._validate_constraints(
            ConstraintType.INVARIANT,
            context,
            executor
        )
    
    def check_determinism(self, inputs: Dict[str, Any], outputs: Any,
                         function_name: str = "default") -> ValidationResult:
        """
        Check determinism: same inputs should produce same outputs.
        
        Args:
            inputs: Input parameters
            outputs: Execution result
            function_name: Name of function/rule being checked
        
        Returns:
            ValidationResult indicating determinism violations
        """
        start_time = time.time()
        violations = []
        
        # Create cache key from inputs
        cache_key = f"{function_name}:{self._hash_inputs(inputs)}"
        
        if cache_key in self._execution_cache:
            # Check if outputs match
            cached_outputs = self._execution_cache[cache_key]
            if outputs != cached_outputs:
                violation = ConstraintViolation(
                    constraint_name="determinism_check",
                    type=ConstraintType.DETERMINISM,
                    severity="error",
                    message=f"Non-deterministic behavior detected in '{function_name}': "
                            f"same inputs produced different outputs",
                    context={
                        "inputs": inputs,
                        "current_output": outputs,
                        "cached_output": cached_outputs
                    }
                )
                violations.append(violation)
        else:
            # Cache this execution
            self._execution_cache[cache_key] = outputs
        
        execution_time = (time.time() - start_time) * 1000
        
        return ValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=[],
            execution_time_ms=execution_time
        )
    
    def check_performance(self, execution_time_ms: float,
                         max_time_ms: float = 1000,
                         function_name: str = "default") -> ValidationResult:
        """
        Check performance constraints.
        
        Args:
            execution_time_ms: Actual execution time in milliseconds
            max_time_ms: Maximum allowed time
            function_name: Name of function being checked
        
        Returns:
            ValidationResult indicating performance violations
        """
        violations = []
        warnings = []
        
        if execution_time_ms > max_time_ms:
            violation = ConstraintViolation(
                constraint_name="performance_check",
                type=ConstraintType.PERFORMANCE,
                severity="error",
                message=f"Performance constraint violated in '{function_name}': "
                        f"execution took {execution_time_ms:.2f}ms (max: {max_time_ms}ms)",
                context={
                    "execution_time_ms": execution_time_ms,
                    "max_time_ms": max_time_ms
                }
            )
            violations.append(violation)
        elif execution_time_ms > max_time_ms * 0.8:
            # Warning if > 80% of limit
            warning = ConstraintViolation(
                constraint_name="performance_warning",
                type=ConstraintType.PERFORMANCE,
                severity="warning",
                message=f"Performance warning in '{function_name}': "
                        f"execution time approaching limit ({execution_time_ms:.2f}ms / {max_time_ms}ms)",
                context={
                    "execution_time_ms": execution_time_ms,
                    "max_time_ms": max_time_ms
                }
            )
            warnings.append(warning)
        
        return ValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            execution_time_ms=0.0  # This check is instant
        )
    
    def _validate_constraints(self, constraint_type: ConstraintType,
                             context: Dict[str, Any],
                             executor: Optional[Any]) -> ValidationResult:
        """Internal: validate constraints of a specific type"""
        if not self.enabled:
            return ValidationResult(
                passed=True,
                violations=[],
                warnings=[],
                execution_time_ms=0.0
            )
        
        start_time = time.time()
        violations = []
        warnings = []
        
        for constraint in self.constraints[constraint_type]:
            if not constraint.enabled:
                continue
            
            # Evaluate constraint condition
            satisfied = self._evaluate_constraint(
                constraint.condition,
                context,
                executor
            )
            
            if not satisfied:
                violation = ConstraintViolation(
                    constraint_name=constraint.name,
                    type=constraint.type,
                    severity=constraint.severity,
                    message=constraint.error_message,
                    context=dict(context)
                )
                
                if constraint.severity == "error":
                    violations.append(violation)
                elif constraint.severity == "warning":
                    warnings.append(violation)
        
        execution_time = (time.time() - start_time) * 1000
        
        return ValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            execution_time_ms=execution_time
        )
    
    def _evaluate_constraint(self, condition: str, context: Dict[str, Any],
                            executor: Optional[Any]) -> bool:
        """Evaluate a constraint condition"""
        if executor is None:
            # Fallback: Python eval
            try:
                namespace = dict(context)
                result = eval(condition, {"__builtins__": {}}, namespace)
                return bool(result)
            except Exception:
                return False
        else:
            # Use APE executor
            try:
                result = executor.eval_expression_with_context(condition, context)
                return bool(result)
            except Exception:
                return False
    
    def _hash_inputs(self, inputs: Dict[str, Any]) -> str:
        """Create a hashable representation of inputs"""
        import json
        try:
            # Sort keys for consistent hashing
            return json.dumps(inputs, sort_keys=True)
        except (TypeError, ValueError):
            # Fallback: use repr
            return repr(sorted(inputs.items()))
    
    def clear_cache(self) -> None:
        """Clear determinism execution cache"""
        self._execution_cache.clear()
    
    def get_constraint(self, name: str) -> Optional[Constraint]:
        """Get a constraint by name"""
        for type_constraints in self.constraints.values():
            for constraint in type_constraints:
                if constraint.name == name:
                    return constraint
        return None
    
    def list_constraints(self, constraint_type: Optional[ConstraintType] = None) -> List[str]:
        """
        Get list of constraint names.
        
        Args:
            constraint_type: Filter by type, or None for all
        
        Returns:
            List of constraint names
        """
        if constraint_type is None:
            # All constraints
            names = []
            for type_constraints in self.constraints.values():
                names.extend(c.name for c in type_constraints)
            return names
        else:
            return [c.name for c in self.constraints[constraint_type]]
    
    def clear_constraints(self, constraint_type: Optional[ConstraintType] = None) -> None:
        """
        Clear constraints.
        
        Args:
            constraint_type: Type to clear, or None to clear all
        """
        if constraint_type is None:
            for type_constraints in self.constraints.values():
                type_constraints.clear()
        else:
            self.constraints[constraint_type].clear()


__all__ = [
    'ConstraintChecker', 'ConstraintType', 'Constraint',
    'ConstraintViolation', 'ValidationResult'
]
