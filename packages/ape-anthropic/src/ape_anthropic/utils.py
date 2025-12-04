"""
Utility functions for ape-anthropic.
"""

import json
from typing import Any, Dict


def format_claude_error(error: Exception) -> str:
    """
    Format an error for returning to Claude.

    Args:
        error: Exception that occurred

    Returns:
        Formatted error string suitable for Claude tool response
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Format as "ErrorType: message" for compatibility
    formatted_error = f"{error_type}: {error_msg}" if error_msg else error_type

    return json.dumps({
        "error": formatted_error
    })


def format_claude_result(result: Any) -> str:
    """
    Format a successful result for Claude.

    Args:
        result: Function execution result

    Returns:
        JSON string for Claude tool response
    """
    # Handle different result types
    try:
        output = {"result": result}
        return json.dumps(output)
    except TypeError:
        # Convert to string for non-JSON-serializable types
        output = {"result": str(result)}
        return json.dumps(output)


def validate_claude_response(response: Dict[str, Any]) -> bool:
    """
    Validate a Claude API response structure.

    Args:
        response: Response dictionary from Claude

    Returns:
        True if response is valid
    """
    if not isinstance(response, dict):
        return False

    if "content" not in response:
        return False

    if not response["content"]:
        return False

    # Check if it contains tool use
    if "stop_reason" in response and response["stop_reason"] == "tool_use":
        return True

    return True  # Valid response even if not tool use


__all__ = [
    "format_claude_error",
    "format_claude_result",
    "validate_claude_response",
]
