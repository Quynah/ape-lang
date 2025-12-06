"""
APE Standard Library - Logic Module

Pure boolean logic and assertion functions.
"""

from typing import Any, Optional, List


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
    'assert_condition',
    'all_true',
    'any_true',
    'none_true',
    'equals',
    'not_equals',
]
