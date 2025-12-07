"""
APE JSON Module (Minimal & Ethical Implementation)

JSON parsing and read-only access utilities.

Pure functions only - no mutation, no side effects.
"""

import json as python_json
from typing import Any, Dict, List, Union, Optional


JSONValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def parse(json_string: str) -> JSONValue:
    """
    Parse a JSON string into APE data structures.
    
    Pure read-only JSON parsing with no side effects.
    
    Example:
        data = parse('{"name": "Alice", "age": 30}')
        # Returns: {"name": "Alice", "age": 30}
    
    Args:
        json_string: Valid JSON string
    
    Returns:
        Parsed JSON as dict, list, or primitive value
    
    Raises:
        TypeError: If json_string is not a string
        ValueError: If JSON is malformed
    """
    if not isinstance(json_string, str):
        raise TypeError(f"parse requires string, got {type(json_string).__name__}")
    
    try:
        return python_json.loads(json_string)
    except python_json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}")


def get(obj: Union[Dict[str, Any], List[Any]], path: Union[str, List[str]], default: Any = None) -> Any:
    """
    Get value from nested JSON using path.
    
    Read-only access - does not modify the original object.
    
    Path can be:
    - Dot-separated string: "user.address.city"
    - List of keys: ["user", "address", "city"]
    
    Example:
        data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        city = get(data, "user.address.city")  # "NYC"
        city = get(data, ["user", "address", "city"])  # "NYC"
        missing = get(data, "user.phone", "N/A")  # "N/A"
    
    Args:
        obj: JSON object (dict or list)
        path: Dot-separated string or list of keys
        default: Value to return if path not found
    
    Returns:
        Value at path, or default if not found
    
    Raises:
        TypeError: If obj is not dict/list or path is not string/list
    """
    if not isinstance(obj, (dict, list)):
        raise TypeError(f"get requires dict or list for obj, got {type(obj).__name__}")
    
    # Parse path
    if isinstance(path, str):
        keys = path.split(".")
    elif isinstance(path, list):
        keys = path
    else:
        raise TypeError(f"get requires string or list for path, got {type(path).__name__}")
    
    # Traverse path
    current = obj
    for key in keys:
        if isinstance(current, dict):
            if key not in current:
                return default
            current = current[key]
        elif isinstance(current, list):
            # Try to convert key to int for list indexing
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    return default
                current = current[index]
            except (ValueError, TypeError):
                return default
        else:
            return default
    
    return current


__all__ = ['parse', 'get']
