"""
Utility functions for ape-openai.
"""

import json
from typing import Any, Dict


def format_openai_error(error: Exception) -> str:
    """
    Format an error for returning to OpenAI.

    Args:
        error: Exception that occurred

    Returns:
        Formatted error string suitable for OpenAI function response
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Format as "ErrorType: message" for compatibility
    formatted_error = f"{error_type}: {error_msg}" if error_msg else error_type

    return json.dumps({
        "error": formatted_error
    })


def format_openai_result(result: Any) -> str:
    """
    Format a successful result for OpenAI.

    Args:
        result: Function execution result

    Returns:
        JSON string for OpenAI function response
    """
    # Handle different result types
    try:
        output = {"result": result}
        return json.dumps(output)
    except TypeError:
        # Convert to string for non-JSON-serializable types
        output = {"result": str(result)}
        return json.dumps(output)


def validate_openai_response(response: Dict[str, Any]) -> bool:
    """
    Validate an OpenAI API response structure.

    Args:
        response: Response dictionary from OpenAI

    Returns:
        True if response is valid
    """
    if not isinstance(response, dict):
        return False

    if "choices" not in response:
        return False

    if not response["choices"]:
        return False

    # Check if it contains function call
    first_choice = response["choices"][0]
    if "message" in first_choice:
        message = first_choice["message"]
        if "function_call" in message or "tool_calls" in message:
            return True

    return True  # Valid response even if not function call


__all__ = [
    "format_openai_error",
    "format_openai_result",
    "validate_openai_response",
]
