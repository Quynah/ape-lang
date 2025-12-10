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
    Validate an OpenAI API response structure for function calling.

    Args:
        response: Response dictionary from OpenAI

    Returns:
        True if response contains valid function call structure
    """
    if not isinstance(response, dict):
        return False

    if "choices" not in response:
        return False

    if not response["choices"]:
        return False

    # Check if it contains valid function call
    first_choice = response["choices"][0]
    if "message" not in first_choice:
        return False
    
    message = first_choice["message"]
    
    # Check for tool_calls (new format)
    if "tool_calls" in message:
        tool_calls = message["tool_calls"]
        if not tool_calls:
            return False
        # Validate first tool call structure
        first_tool = tool_calls[0]
        if "function" not in first_tool:
            return False
        func = first_tool["function"]
        if "name" not in func or "arguments" not in func:
            return False
        return True
    
    # Check for function_call (legacy format)
    if "function_call" in message:
        func_call = message["function_call"]
        if "name" not in func_call or "arguments" not in func_call:
            return False
        return True
    
    return False  # No function call found


__all__ = [
    "format_openai_error",
    "format_openai_result",
    "validate_openai_response",
]
