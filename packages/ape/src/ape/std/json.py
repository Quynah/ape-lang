"""
APE JSON Module (v1.0.0 Scaffold)

JSON parsing, serialization, and manipulation utilities.

Author: David Van Aelst
Status: Scaffold - implementation pending
"""

from typing import Any, Dict, List, Union, Optional


JSONValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def parse(json_string: str) -> JSONValue:
    """
    Parse a JSON string into APE data structures.
    
    Example:
        data = json.parse('{"name": "Alice", "age": 30}')
        print(data["name"])  # "Alice"
    
    Args:
        json_string: Valid JSON string
    
    Returns:
        Parsed JSON as Map, List, or primitive value
    
    Raises:
        ValueError: If JSON is malformed
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    import json as python_json
    try:
        return python_json.loads(json_string)
    except python_json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def stringify(data: JSONValue, indent: Optional[int] = None) -> str:
    """
    Convert APE data structures to JSON string.
    
    Example:
        data = {"name": "Alice", "age": 30}
        json_str = json.stringify(data, indent=2)
    
    Args:
        data: Data to serialize (Map, List, or primitive)
        indent: Number of spaces for indentation (None for compact)
    
    Returns:
        JSON string representation
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    import json as python_json
    return python_json.dumps(data, indent=indent)


def get(data: Any, path: str, default: Any = None) -> Any:
    """
    Get value from nested JSON/payload using dot notation path.
    
    Never fails silently - always returns a value (data, or default).
    
    Example:
        data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        city = json.get(data, "user.address.city")  # "NYC"
        missing = json.get(data, "user.phone", "N/A")  # "N/A"
        list_access = json.get([{"id": "x"}], "0.id")  # "x"
    
    Args:
        data: JSON object (Map/Dict), List, or any data structure
        path: Dot-separated path (e.g., "user.address.city" or "items.0.name")
        default: Value to return if path not found
    
    Returns:
        Value at path, or default if not found
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not path:
        return data
    
    parts = path.split('.')
    current = data
    
    for part in parts:
        if current is None:
            return default
        
        # Handle dict access
        if isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        # Handle list/array index access
        elif isinstance(current, list):
            try:
                index = int(part)
                if index < 0 or index >= len(current):
                    return default
                current = current[index]
            except (ValueError, IndexError):
                return default
        # Handle object attribute access (for records)
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            return default
    
    return current


def set(data: dict, path: str, value: Any) -> dict:
    """
    Set value in nested JSON using dot notation path.
    Returns new dict (immutable operation).
    
    Example:
        data = {"user": {"name": "Alice"}}
        updated = json.set(data, "user.email", "alice@example.com")
        # {"user": {"name": "Alice", "email": "alice@example.com"}}
    
    Args:
        data: JSON object (Map)
        path: Dot-separated path
        value: Value to set
    
    Returns:
        Updated data structure (creates nested objects as needed)
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    import copy
    result = copy.deepcopy(data) if isinstance(data, dict) else {}
    
    if not path:
        return value if isinstance(value, dict) else result
    
    parts = path.split('.')
    current = result
    
    for i, part in enumerate(parts[:-1]):
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value
    return result


def has_path(data: Any, path: str) -> bool:
    """
    Check if a path exists in JSON data.
    
    Example:
        data = {"user": {"name": "Alice"}}
        json.has_path(data, "user.name")  # True
        json.has_path(data, "user.email")  # False
    
    Args:
        data: JSON object (Map/Dict or List)
        path: Dot-separated path
    
    Returns:
        True if path exists, False otherwise
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not path:
        return True
    
    parts = path.split('.')
    current = data
    
    for part in parts:
        if current is None:
            return False
        
        # Handle dict access
        if isinstance(current, dict):
            if part not in current:
                return False
            current = current[part]
        # Handle list/array index access
        elif isinstance(current, list):
            try:
                index = int(part)
                if index < 0 or index >= len(current):
                    return False
                current = current[index]
            except (ValueError, IndexError):
                return False
        # Handle object attribute access
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            return False
    
    return True


def flatten(data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """
    Flatten nested JSON structure to dotted keys.
    
    Example:
        data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        json.flatten(data)
        # {"user.name": "Alice", "user.address.city": "NYC"}
    
    Args:
        data: Nested JSON object
        prefix: Key prefix (used internally for recursion)
    
    Returns:
        Flattened dict with dotted keys
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    result = {}
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dicts
            result.update(flatten(value, full_key))
        elif isinstance(value, list):
            # Flatten list elements with index
            for i, item in enumerate(value):
                item_key = f"{full_key}.{i}"
                if isinstance(item, dict):
                    result.update(flatten(item, item_key))
                else:
                    result[item_key] = item
        else:
            result[full_key] = value
    
    return result


__all__ = ['parse', 'stringify', 'get', 'set', 'has_path', 'flatten']
