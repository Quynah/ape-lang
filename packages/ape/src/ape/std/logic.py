"""
APE Standard Library - Logic Module

Pure boolean logic and assertion functions.

STRICT BOOLEAN OPERATORS:
All logical operators (and_op, or_op, not_op) require explicit booleans.
No truthy/falsy coercion - non-boolean inputs raise LogicTypeError.
"""

from typing import Any, Optional, List
from ape.std.errors import LogicTypeError


def and_op(a: bool, b: bool) -> bool:
    """
    Strict boolean AND operation.
    
    Args:
        a: First boolean value
        b: Second boolean value
        
    Returns:
        True if both a and b are True, False otherwise
        
    Raises:
        LogicTypeError: If a or b is not a boolean
        
    Examples:
        and_op(True, True) → True
        and_op(True, False) → False
        and_op(1, 1) → LogicTypeError (not booleans)
        
    Note:
        This is NOT short-circuiting - both arguments are always evaluated.
        For short-circuit behavior, use APE's native `if` statements.
    """
    if not isinstance(a, bool):
        raise LogicTypeError("and_op", "a", type(a).__name__)
    if not isinstance(b, bool):
        raise LogicTypeError("and_op", "b", type(b).__name__)
    
    return a and b


def or_op(a: bool, b: bool) -> bool:
    """
    Strict boolean OR operation.
    
    Args:
        a: First boolean value
        b: Second boolean value
        
    Returns:
        True if either a or b is True, False otherwise
        
    Raises:
        LogicTypeError: If a or b is not a boolean
        
    Examples:
        or_op(True, False) → True
        or_op(False, False) → False
        or_op(1, 0) → LogicTypeError (not booleans)
        
    Note:
        This is NOT short-circuiting - both arguments are always evaluated.
        For short-circuit behavior, use APE's native `if` statements.
    """
    if not isinstance(a, bool):
        raise LogicTypeError("or_op", "a", type(a).__name__)
    if not isinstance(b, bool):
        raise LogicTypeError("or_op", "b", type(b).__name__)
    
    return a or b


def not_op(a: bool) -> bool:
    """
    Strict boolean NOT operation.
    
    Args:
        a: Boolean value to negate
        
    Returns:
        True if a is False, False if a is True
        
    Raises:
        LogicTypeError: If a is not a boolean
        
    Examples:
        not_op(True) → False
        not_op(False) → True
        not_op(0) → LogicTypeError (not boolean)
    """
    if not isinstance(a, bool):
        raise LogicTypeError("not_op", "a", type(a).__name__)
    
    return not a


def assert_condition(condition: bool, message: Optional[str] = None) -> None:
    """
    Validate a condition and raise an error if false.
    
    Args:
        condition: Boolean condition to check
        message: Optional error message if condition is false
        
    Raises:
        RuntimeError: If condition is false
        TypeError: If condition is not a boolean
    """
    if not isinstance(condition, bool):
        raise TypeError(f"assert_condition requires boolean condition, got {type(condition).__name__}")
    
    if not condition:
        error_msg = message if message is not None else "Assertion failed"
        raise RuntimeError(error_msg)


def all_true(values: List[Any]) -> bool:
    """
    Check if all values are truthy.
    
    Args:
        values: List of values to check
        
    Returns:
        True if all values are truthy, False otherwise
        
    Raises:
        TypeError: If values is not a list
    """
    if not isinstance(values, list):
        raise TypeError(f"all_true requires list, got {type(values).__name__}")
    
    return all(values)


def any_true(values: List[Any]) -> bool:
    """
    Check if any value is truthy.
    
    Args:
        values: List of values to check
        
    Returns:
        True if any value is truthy, False otherwise
        
    Raises:
        TypeError: If values is not a list
    """
    if not isinstance(values, list):
        raise TypeError(f"any_true requires list, got {type(values).__name__}")
    
    return any(values)


def none_true(values: List[Any]) -> bool:
    """
    Check if no values are truthy.
    
    Args:
        values: List of values to check
        
    Returns:
        True if no values are truthy, False otherwise
        
    Raises:
        TypeError: If values is not a list
    """
    if not isinstance(values, list):
        raise TypeError(f"none_true requires list, got {type(values).__name__}")
    
    return not any(values)


def equals(a: Any, b: Any) -> bool:
    """
    Check equality between two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        True if values are equal, False otherwise
    """
    return a == b


def not_equals(a: Any, b: Any) -> bool:
    """
    Check inequality between two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        True if values are not equal, False otherwise
    """
    return a != b


__all__ = [
    'and_op',
    'or_op',
    'not_op',
    'assert_condition',
    'all_true',
    'any_true',
    'none_true',
    'equals',
    'not_equals',
]
