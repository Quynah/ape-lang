"""
APE Error & Diagnostics Model

Unified error hierarchy for APE v1.0.0. Provides semantic context without
exposing Python internals to end users.

Design Principles:
- Errors are inspectable and user-friendly
- No Python stacktraces exposed to users
- Link to execution trace when available
- Provide semantic context (node type, location)
- Stable across v1.x releases
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ErrorContext:
    """
    Semantic context for an error.
    
    Provides user-facing information about where and why an error occurred,
    without exposing Python implementation details.
    
    Attributes:
        node_type: Type of AST node where error occurred (e.g., "IF", "WHILE")
        trace_id: Trace ID of the execution (for observability)
        trace_index: Index in execution trace (if available)
        line_number: Source line number (if available)
        column_number: Source column number (if available)
        details: Additional error-specific information
    """
    node_type: Optional[str] = None
    trace_id: Optional[str] = None
    trace_index: Optional[int] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {}
        if self.node_type:
            result['node_type'] = self.node_type
        if self.trace_id:
            result['trace_id'] = self.trace_id
        if self.trace_index is not None:
            result['trace_index'] = self.trace_index
        if self.line_number is not None:
            result['line_number'] = self.line_number
        if self.column_number is not None:
            result['column_number'] = self.column_number
        if self.details:
            result['details'] = self.details
        return result


class ApeError(Exception):
    """
    Base class for all APE errors.
    
    Provides semantic error information without Python implementation details.
    All APE errors should inherit from this class for v1.0 stability.
    
    Attributes:
        message: Human-readable error message
        context: Semantic context (node type, trace index, etc.)
    """
    
    def __init__(
        self, 
        message: str, 
        context: Optional[ErrorContext] = None
    ):
        """
        Initialize APE error.
        
        Args:
            message: Human-readable error message
            context: Optional semantic context
        """
        self.message = message
        self.context = context or ErrorContext()
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format error message with context"""
        parts = [self.message]
        
        if self.context.trace_id:
            parts.append(f"Trace ID: {self.context.trace_id}")
        
        if self.context.node_type:
            parts.append(f"Node: {self.context.node_type}")
        
        if self.context.trace_index is not None:
            parts.append(f"Trace step: {self.context.trace_index}")
        
        if self.context.line_number is not None:
            parts.append(f"Line: {self.context.line_number}")
        
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary for inspection/serialization.
        
        Returns:
            Dictionary with error type, message, and context
        """
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'context': self.context.to_dict()
        }


class ParseError(ApeError):
    """
    Error during parsing of APE source code.
    
    Raised when source code cannot be parsed into valid AST.
    Typically includes line/column information.
    """
    
    def __init__(
        self, 
        message: str, 
        line: Optional[int] = None,
        column: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize parse error.
        
        Args:
            message: Description of parse failure
            line: Line number where error occurred
            column: Column number where error occurred
            details: Additional parsing context
        """
        context = ErrorContext(
            line_number=line,
            column_number=column,
            details=details or {}
        )
        super().__init__(message, context)


class RuntimeExecutionError(ApeError):
    """
    Error during runtime execution of APE program.
    
    Raised when execution fails (e.g., iteration limit exceeded, invalid operation).
    Includes node type and trace context.
    """
    
    def __init__(
        self, 
        message: str,
        node_type: Optional[str] = None,
        trace_id: Optional[str] = None,
        trace_index: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[ErrorContext] = None
    ):
        """
        Initialize runtime execution error.
        
        Args:
            message: Description of execution failure
            node_type: Type of AST node where error occurred
            trace_id: Trace ID for observability
            trace_index: Index in execution trace
            details: Additional execution context
            context: Pre-constructed ErrorContext (overrides other params)
        """
        if context is not None:
            # Use provided context directly
            error_context = context
        else:
            # Build context from parameters
            error_context = ErrorContext(
                node_type=node_type,
                trace_id=trace_id,
                trace_index=trace_index,
                details=details or {}
            )
        super().__init__(message, error_context)


class CapabilityError(ApeError):
    """
    Error when required capability is not granted.
    
    Raised when operation requires a capability that hasn't been granted
    via ExecutionContext.allow().
    """
    
    def __init__(
        self, 
        capability: str,
        operation: str,
        node_type: Optional[str] = None,
        trace_index: Optional[int] = None
    ):
        """
        Initialize capability error.
        
        Args:
            capability: Name of required capability
            operation: Operation that was attempted
            node_type: Type of AST node where error occurred
            trace_index: Index in execution trace
        """
        message = f"Operation '{operation}' requires capability '{capability}'"
        context = ErrorContext(
            node_type=node_type,
            trace_index=trace_index,
            details={'capability': capability, 'operation': operation}
        )
        super().__init__(message, context)
        self.capability = capability
        self.operation = operation


class ReplayError(ApeError):
    """
    Error during trace replay validation.
    
    Raised when replay validation fails, indicating non-deterministic behavior
    or corrupted trace.
    """
    
    def __init__(
        self, 
        message: str,
        trace_index: Optional[int] = None,
        expected_node: Optional[str] = None,
        actual_node: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize replay error.
        
        Args:
            message: Description of replay failure
            trace_index: Index where validation failed
            expected_node: Expected node type
            actual_node: Actual node type found
            details: Additional replay context
        """
        replay_details = details or {}
        if expected_node:
            replay_details['expected_node'] = expected_node
        if actual_node:
            replay_details['actual_node'] = actual_node
        
        context = ErrorContext(
            trace_index=trace_index,
            details=replay_details
        )
        super().__init__(message, context)


class ValidationError(ApeError):
    """
    Error during semantic validation.
    
    Raised when semantic validation fails (e.g., type mismatch, undefined symbol).
    """
    
    def __init__(
        self, 
        message: str,
        node_type: Optional[str] = None,
        line: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation error.
        
        Args:
            message: Description of validation failure
            node_type: Type of AST node that failed validation
            line: Line number in source
            details: Additional validation context
        """
        context = ErrorContext(
            node_type=node_type,
            line_number=line,
            details=details or {}
        )
        super().__init__(message, context)


class LinkerError(ApeError):
    """
    Error during module linking.
    
    Raised when module dependencies cannot be resolved or circular imports detected.
    """
    
    def __init__(
        self, 
        message: str,
        module_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize linker error.
        
        Args:
            message: Description of linking failure
            module_name: Name of module being linked
            details: Additional linker context (e.g., import chain)
        """
        linker_details = details or {}
        if module_name:
            linker_details['module_name'] = module_name
        
        context = ErrorContext(details=linker_details)
        super().__init__(message, context)


class ProfileError(ApeError):
    """
    Error in runtime profile configuration.
    
    Raised when profile is invalid or cannot be applied.
    """
    
    def __init__(
        self, 
        message: str,
        profile_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize profile error.
        
        Args:
            message: Description of profile error
            profile_name: Name of profile
            details: Additional profile context
        """
        profile_details = details or {}
        if profile_name:
            profile_details['profile_name'] = profile_name
        
        context = ErrorContext(details=profile_details)
        super().__init__(message, context)


# Legacy compatibility - map old exceptions to new hierarchy
# These allow gradual migration without breaking existing code
class ExecutionError(RuntimeExecutionError):
    """Legacy alias for RuntimeExecutionError (backwards compatibility)"""
    pass


class MaxIterationsExceeded(RuntimeExecutionError):
    """
    Error when iteration limit is exceeded.
    
    Raised when loop exceeds max_iterations safety limit.
    """
    
    def __init__(
        self,
        max_iterations: int,
        node_type: str = "WHILE",
        trace_index: Optional[int] = None
    ):
        """
        Initialize max iterations error.
        
        Args:
            max_iterations: The iteration limit that was exceeded
            node_type: Type of loop node (WHILE or FOR)
            trace_index: Index in execution trace
        """
        message = f"Loop exceeded maximum iterations ({max_iterations})"
        super().__init__(
            message,
            node_type=node_type,
            trace_index=trace_index,
            details={'max_iterations': max_iterations}
        )


__all__ = [
    # Core error hierarchy
    'ApeError',
    'ErrorContext',
    
    # Specific error types
    'ParseError',
    'RuntimeExecutionError',
    'CapabilityError',
    'ReplayError',
    'ValidationError',
    'LinkerError',
    'ProfileError',
    
    # Legacy compatibility
    'ExecutionError',
    'MaxIterationsExceeded',
]
