"""
Tests for utility functions.
"""

import pytest
import json

from ape_anthropic.utils import (
    format_claude_error,
    format_claude_result,
    validate_claude_response
)


def test_format_claude_error():
    """Test formatting errors for Claude."""
    error = ValueError("Invalid input")
    
    result = format_claude_error(error)
    parsed = json.loads(result)
    
    assert parsed["error"] == "ValueError: Invalid input"


def test_format_claude_result_primitive():
    """Test formatting primitive results."""
    result = format_claude_result(42)
    parsed = json.loads(result)
    
    assert parsed["result"] == 42


def test_format_claude_result_string():
    """Test formatting string results."""
    result = format_claude_result("hello world")
    parsed = json.loads(result)
    
    assert parsed["result"] == "hello world"


def test_format_claude_result_list():
    """Test formatting list results."""
    result = format_claude_result([1, 2, 3, 4, 5])
    parsed = json.loads(result)
    
    assert parsed["result"] == [1, 2, 3, 4, 5]


def test_format_claude_result_dict():
    """Test formatting dict results."""
    result = format_claude_result({"status": "success", "count": 10})
    parsed = json.loads(result)
    
    assert parsed["result"]["status"] == "success"
    assert parsed["result"]["count"] == 10


def test_format_claude_result_non_serializable():
    """Test formatting non-JSON-serializable results."""
    class CustomObject:
        def __str__(self):
            return "CustomObject instance"
    
    obj = CustomObject()
    result = format_claude_result(obj)
    parsed = json.loads(result)
    
    assert parsed["result"] == "CustomObject instance"


def test_validate_claude_response_valid():
    """Test validation of valid Claude response."""
    response = {
        "content": [
            {
                "type": "tool_use",
                "name": "add",
                "input": {"a": 1, "b": 2}
            }
        ],
        "stop_reason": "tool_use"
    }
    
    assert validate_claude_response(response) is True


def test_validate_claude_response_missing_content():
    """Test validation with missing content."""
    response = {}
    
    assert validate_claude_response(response) is False


def test_validate_claude_response_empty_content():
    """Test validation with empty content."""
    response = {"content": []}
    
    assert validate_claude_response(response) is False


def test_validate_claude_response_text_only():
    """Test validation with text-only response."""
    response = {
        "content": [
            {
                "type": "text",
                "text": "Regular text response"
            }
        ]
    }
    
    # Text responses are valid
    assert validate_claude_response(response) is True


def test_format_claude_error_with_traceback():
    """Test formatting errors with detailed information."""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        result = format_claude_error(e)
        parsed = json.loads(result)
        
        assert "ValueError: Test error" in parsed["error"]


def test_format_claude_result_nested():
    """Test formatting nested data structures."""
    nested_data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    
    result = format_claude_result(nested_data)
    parsed = json.loads(result)
    
    assert len(parsed["result"]["users"]) == 2
    assert parsed["result"]["users"][0]["name"] == "Alice"
    assert parsed["result"]["total"] == 2


def test_format_claude_result_boolean():
    """Test formatting boolean results."""
    result_true = format_claude_result(True)
    result_false = format_claude_result(False)
    
    assert json.loads(result_true)["result"] is True
    assert json.loads(result_false)["result"] is False


def test_format_claude_result_null():
    """Test formatting None/null results."""
    result = format_claude_result(None)
    parsed = json.loads(result)
    
    assert parsed["result"] is None
