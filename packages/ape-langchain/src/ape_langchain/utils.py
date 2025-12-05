"""
Utility functions for ape-langchain.
"""

from typing import Any, Dict


def format_langchain_result(result: Any) -> Dict[str, Any]:
    """
    Format a result for LangChain consumption.

    Args:
        result: Function execution result

    Returns:
        Dictionary with result
    """
    return {"result": result}


def validate_tool_input(input_data: Dict[str, Any], required_fields: list[str]) -> bool:
    """
    Validate tool input has required fields.

    Args:
        input_data: Input dictionary
        required_fields: List of required field names

    Returns:
        True if valid
    """
    provided = set(input_data.keys())
    required = set(required_fields)
    
    return required.issubset(provided)


__all__ = [
    "format_langchain_result",
    "validate_tool_input",
]
