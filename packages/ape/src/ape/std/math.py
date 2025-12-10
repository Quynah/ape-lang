"""
APE Standard Library - Math Module

Pure mathematical functions.
"""

from typing import List, Union


def abs_value(x: Union[int, float]) -> Union[int, float]:
    """
    Return absolute value of a number.
    
    Args:
        x: Number to process
        
    Returns:
        Absolute value of x
        
    Raises:
        TypeError: If x is not a number
    """
    if not isinstance(x, (int, float)):
        raise TypeError(f"abs_value requires number, got {type(x).__name__}")
    
    return abs(x)


def min_value(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Return minimum of two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Minimum of a and b
        
    Raises:
        TypeError: If a or b is not a number
    """
    if not isinstance(a, (int, float)):
        raise TypeError(f"min_value requires number for a, got {type(a).__name__}")
    
    if not isinstance(b, (int, float)):
        raise TypeError(f"min_value requires number for b, got {type(b).__name__}")
    
    return min(a, b)


def max_value(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Return maximum of two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Maximum of a and b
        
    Raises:
        TypeError: If a or b is not a number
    """
    if not isinstance(a, (int, float)):
        raise TypeError(f"max_value requires number for a, got {type(a).__name__}")
    
    if not isinstance(b, (int, float)):
        raise TypeError(f"max_value requires number for b, got {type(b).__name__}")
    
    return max(a, b)


def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value to a range.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Value clamped between min_val and max_val
        
    Raises:
        TypeError: If any argument is not a number
        ValueError: If min_val > max_val
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"clamp requires number for value, got {type(value).__name__}")
    
    if not isinstance(min_val, (int, float)):
        raise TypeError(f"clamp requires number for min_val, got {type(min_val).__name__}")
    
    if not isinstance(max_val, (int, float)):
        raise TypeError(f"clamp requires number for max_val, got {type(max_val).__name__}")
    
    if min_val > max_val:
        raise ValueError(f"clamp requires min_val <= max_val, got {min_val} > {max_val}")
    
    return max(min_val, min(value, max_val))


def sum_values(values: List[Union[int, float]]) -> Union[int, float]:
    """
    Return sum of a collection of numbers.
    
    Args:
        values: List of numbers to sum
        
    Returns:
        Sum of all values
        
    Raises:
        TypeError: If values is not a list or contains non-numbers
    """
    if not isinstance(values, list):
        raise TypeError(f"sum_values requires list, got {type(values).__name__}")
    
    for i, val in enumerate(values):
        if not isinstance(val, (int, float)):
            raise TypeError(f"sum_values requires all values to be numbers, got {type(val).__name__} at index {i}")
    
    return sum(values)


__all__ = [
    'abs_value',
    'min_value',
    'max_value',
    'clamp',
    'sum_values',
]
