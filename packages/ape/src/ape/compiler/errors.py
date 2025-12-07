"""
Ape Compiler Error Definitions

Machine-readable error structures for the Ape compiler.
All errors follow Ape's strict philosophy: clear, deterministic, and actionable.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from .ir_nodes import Location


class ErrorCategory(Enum):
    """Error categories for classification"""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    TYPE = "type"
    POLICY = "policy"
    DEVIATION = "deviation"
    STRICTNESS = "strictness"
    CONTRACT = "contract"


class ErrorCode(Enum):
    """All possible Ape compiler error codes"""
    
    # Semantic errors (E1xxx)
    E_UNDEFINED_SYMBOL = "E1001"
    E_DUPLICATE_DEFINITION = "E1002"
    E_CIRCULAR_DEPENDENCY = "E1003"
    E_INVALID_IMPORT = "E1004"
    
    # Type errors (E2xxx)
    E_TYPE_MISMATCH = "E2001"
    E_UNKNOWN_TYPE = "E2002"
    E_INVALID_FIELD_TYPE = "E2003"
    E_MISSING_REQUIRED_FIELD = "E2004"
    
    # Contract errors (E3xxx)
    E_CONTRACT_VIOLATION = "E3001"
    E_PRECONDITION_FAILED = "E3002"
    E_POSTCONDITION_FAILED = "E3003"
    E_INVARIANT_VIOLATED = "E3004"
    
    # Policy errors (E4xxx)
    E_POLICY_VIOLATION = "E4001"
    E_POLICY_CONFLICT = "E4002"
    E_POLICY_SCOPE_INVALID = "E4003"
    
    # Deviation errors (E5xxx)
    E_DEVIATION_NOT_DECLARED = "E5001"
    E_DEVIATION_UNBOUNDED = "E5002"
    E_DEVIATION_OUT_OF_SCOPE = "E5003"
    E_DEVIATION_POLICY_CONFLICT = "E5004"
    E_DEVIATION_AMBIGUOUS_BOUND = "E5005"
    
    # Strictness errors (E6xxx)
    E_AMBIGUOUS_BEHAVIOR = "E6001"
    E_UNDECLARED_BEHAVIOR = "E6002"
    E_NON_DETERMINISTIC = "E6003"
    E_IMPLICIT_CONVERSION = "E6004"
    E_UNCONTROLLED_SIDE_EFFECT = "E6005"


@dataclass
class ApeError:
    """
    Machine-readable error structure for Ape compiler.
    
    Attributes:
        code: Unique error code (e.g., E1001)
        category: Error category for filtering
        message: Human-readable error description
        location: Source location where error occurred
        context: Additional contextual information
        suggestion: Optional fix suggestion
    """
    code: ErrorCode
    category: ErrorCategory
    message: str
    location: Optional[Location] = None
    context: Dict[str, Any] = None
    suggestion: Optional[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if isinstance(self.code, str):
            self.code = ErrorCode(self.code)
        if isinstance(self.category, str):
            self.category = ErrorCategory(self.category)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to machine-readable dictionary"""
        result = {
            "code": self.code.value,
            "category": self.category.value,
            "message": self.message,
            "context": self.context
        }
        if self.location:
            result["location"] = str(self.location)
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result
    
    def __str__(self) -> str:
        """Human-readable error string"""
        parts = [f"[{self.code.value}] {self.message}"]
        if self.location:
            parts.insert(0, str(self.location))
        if self.suggestion:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)


class ErrorCollector:
    """Utility for collecting multiple errors during validation"""
    
    def __init__(self):
        self.errors: List[ApeError] = []
    
    def add(self, error: ApeError):
        """Add an error to the collection"""
        self.errors.append(error)
    
    def add_error(self, code: ErrorCode, category: ErrorCategory, 
                  message: str, location: Optional[Location] = None,
                  context: Dict[str, Any] = None, suggestion: Optional[str] = None):
        """Convenience method to add error from components"""
        self.errors.append(ApeError(
            code=code,
            category=category,
            message=message,
            location=location,
            context=context or {},
            suggestion=suggestion
        ))
    
    def has_errors(self) -> bool:
        """Check if any errors were collected"""
        return len(self.errors) > 0
    
    def get_errors(self) -> list:
        """Get all collected errors"""
        return self.errors
    
    def clear(self):
        """Clear all errors"""
        self.errors.clear()
