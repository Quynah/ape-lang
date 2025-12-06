"""
Extended Error Types for APE v1.0.0

This module extends the base error hierarchy with user-defined errors
and structured type errors.

Author: David Van Aelst
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ErrorContext:
    """Context information for APE errors"""
    message: str
    location: Optional[str] = None
    node_type: Optional[str] = None
    metadata: Optional[dict] = None


class ApeError(Exception):
    """Base class for all APE errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.context = context or ErrorContext(message=message)


class UserError(ApeError):
    """
    User-defined error raised by APE code using 'raise' statement.
    
    Example:
        raise UserError("Invalid input")
    
    Status: v1.0.0 scaffold - implementation pending
    """
    def __init__(self, message: str, error_type: str = "Error", context: Optional[ErrorContext] = None):
        super().__init__(message, context)
        self.error_type = error_type


class TryCatchError(ApeError):
    """
    Error during try/catch/finally execution.
    
    This is raised when try/catch/finally constructs have structural issues
    (e.g., uncaught exceptions, finally block errors).
    
    Status: v1.0.0 scaffold - implementation pending
    """
    pass


class StructuredTypeError(ApeError):
    """
    Error during structured type operations (List, Map, Record, Tuple).
    
    Examples:
        - Index out of bounds: list[10] when list has 5 elements
        - Key not found: map["missing_key"]
        - Type mismatch: List<Integer> assigned String
        - Invalid record field access
    
    Status: v1.0.0 scaffold - implementation pending
    """
    def __init__(self, message: str, type_name: str, operation: str, context: Optional[ErrorContext] = None):
        super().__init__(message, context)
        self.type_name = type_name
        self.operation = operation


class TypeInferenceError(ApeError):
    """
    Error during type inference.
    
    Raised when the type system cannot infer types for expressions
    or when type constraints conflict.
    
    Status: v1.0.0 scaffold - implementation pending
    """
    pass


# Re-export existing errors for backwards compatibility
from ape.runtime.context import (
    ExecutionError,
    MaxIterationsExceeded,
    CapabilityError,
)

__all__ = [
    'ApeError',
    'ErrorContext',
    'UserError',
    'TryCatchError',
    'StructuredTypeError',
    'TypeInferenceError',
    'ExecutionError',
    'MaxIterationsExceeded',
    'CapabilityError',
]
