"""
APE Standard Library - Math Module

Pure mathematical functions.

All math operations in APE are:
- Deterministic (same inputs → same output)
- Type-strict (int and float are distinct types)
- Explicit (errors on division by zero, type mismatch)
- Integer-first (prefer int over float when possible)
"""

from typing import List, Union
from ape.std.errors import MathTypeError, DivisionByZeroError


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Deterministic addition.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        a + b (int if both int, float otherwise)
        
    Raises:
        MathTypeError: If a or b is not a number
        
    Examples:
        add(1, 2) → 3
        add(1.5, 2.5) → 4.0
        add(1, 2.5) → 3.5
    """
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise MathTypeError("add", "a", type(a).__name__)
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise MathTypeError("add", "b", type(b).__name__)
    
    return a + b


def sub(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Deterministic subtraction.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
        
    Returns:
        a - b (int if both int, float otherwise)
        
    Raises:
        MathTypeError: If a or b is not a number
        
    Examples:
        sub(5, 3) → 2
        sub(5.5, 2.5) → 3.0
        sub(5, 2.5) → 2.5
    """
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise MathTypeError("sub", "a", type(a).__name__)
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise MathTypeError("sub", "b", type(b).__name__)
    
    return a - b


def mul(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Deterministic multiplication.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        a * b (int if both int, float otherwise)
        
    Raises:
        MathTypeError: If a or b is not a number
        
    Examples:
        mul(3, 4) → 12
        mul(2.5, 4.0) → 10.0
        mul(2, 3.5) → 7.0
    """
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise MathTypeError("mul", "a", type(a).__name__)
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise MathTypeError("mul", "b", type(b).__name__)
    
    return a * b


def div(a: Union[int, float], b: Union[int, float]) -> float:
    """
    Deterministic division (always returns float).
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        a / b as float
        
    Raises:
        MathTypeError: If a or b is not a number
        DivisionByZeroError: If b is zero
        
    Examples:
        div(10, 2) → 5.0
        div(10, 3) → 3.3333333333333335
        div(10, 0) → DivisionByZeroError
        
    Note:
        Always returns float for consistent behavior.
        For integer division, use div_int().
    """
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise MathTypeError("div", "a", type(a).__name__)
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise MathTypeError("div", "b", type(b).__name__)
    
    if b == 0:
        raise DivisionByZeroError(a)
    
    return a / b


def div_int(a: int, b: int) -> int:
    """
    Integer division (floor division).
    
    Args:
        a: Numerator (must be int)
        b: Denominator (must be int)
        
    Returns:
        a // b as int
        
    Raises:
        MathTypeError: If a or b is not an integer
        DivisionByZeroError: If b is zero
        
    Examples:
        div_int(10, 3) → 3
        div_int(10, 2) → 5
        div_int(-10, 3) → -4
    """
    if not isinstance(a, int) or isinstance(a, bool):
        raise MathTypeError("div_int", "a", type(a).__name__)
    if not isinstance(b, int) or isinstance(b, bool):
        raise MathTypeError("div_int", "b", type(b).__name__)
    
    if b == 0:
        raise DivisionByZeroError(a)
    
    return a // b


def mod(a: int, b: int) -> int:
    """
    Modulo operation (remainder).
    
    Args:
        a: Dividend (must be int)
        b: Divisor (must be int)
        
    Returns:
        a % b as int
        
    Raises:
        MathTypeError: If a or b is not an integer
        DivisionByZeroError: If b is zero
        
    Examples:
        mod(10, 3) → 1
        mod(10, 5) → 0
        mod(-10, 3) → 2
    """
    if not isinstance(a, int) or isinstance(a, bool):
        raise MathTypeError("mod", "a", type(a).__name__)
    if not isinstance(b, int) or isinstance(b, bool):
        raise MathTypeError("mod", "b", type(b).__name__)
    
    if b == 0:
        raise DivisionByZeroError(a)
    
    return a % b


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
    'add',
    'sub',
    'mul',
    'div',
    'div_int',
    'mod',
    'abs_value',
    'min_value',
    'max_value',
    'clamp',
    'sum_values',
]
