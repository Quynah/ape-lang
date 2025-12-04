"""
Tests for utility functions.
"""

import pytest
import json

from ape_openai.utils import (
    format_openai_error,
    format_openai_result,
    validate_openai_response
)


def test_format_openai_error():
    """Test formatting errors for OpenAI."""
    error = ValueError("Invalid input")
    
    result = format_openai_error(error)
    parsed = json.loads(result)
    
    assert parsed["error"] == "ValueError: Invalid input"


def test_format_openai_result_primitive():
    """Test formatting primitive results."""
    result = format_openai_result(42)
    parsed = json.loads(result)
    
    assert parsed["result"] == 42


def test_format_openai_result_string():
    """Test formatting string results."""
    result = format_openai_result("hello world")
    parsed = json.loads(result)
    
    assert parsed["result"] == "hello world"


def test_format_openai_result_list():
    """Test formatting list results."""
    result = format_openai_result([1, 2, 3, 4, 5])
    parsed = json.loads(result)
    
    assert parsed["result"] == [1, 2, 3, 4, 5]


def test_format_openai_result_dict():
    """Test formatting dict results."""
    result = format_openai_result({"status": "success", "count": 10})
    parsed = json.loads(result)
    
    assert parsed["result"]["status"] == "success"
    assert parsed["result"]["count"] == 10


def test_format_openai_result_non_serializable():
    """Test formatting non-JSON-serializable results."""
    class CustomObject:
        def __str__(self):
            return "CustomObject instance"
    
    obj = CustomObject()
    result = format_openai_result(obj)
    parsed = json.loads(result)
    
    assert parsed["result"] == "CustomObject instance"


def test_validate_openai_response_valid():
    """Test validation of valid OpenAI response."""
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "add",
                                "arguments": '{"a": 1, "b": 2}'
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    assert validate_openai_response(response) is True


def test_validate_openai_response_missing_choices():
    """Test validation with missing choices."""
    response = {}
    
    assert validate_openai_response(response) is False


def test_validate_openai_response_empty_choices():
    """Test validation with empty choices."""
    response = {"choices": []}
    
    assert validate_openai_response(response) is False


def test_validate_openai_response_missing_message():
    """Test validation with missing message."""
    response = {"choices": [{}]}
    
    assert validate_openai_response(response) is False


def test_validate_openai_response_no_tool_calls():
    """Test validation with no tool calls (text response)."""
    response = {
        "choices": [
            {
                "message": {
                    "content": "Regular text response"
                }
            }
        ]
    }
    
    # Text responses are valid
    assert validate_openai_response(response) is True


def test_format_openai_error_with_traceback():
    """Test formatting errors with detailed information."""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        result = format_openai_error(e)
        parsed = json.loads(result)
        
        assert "ValueError: Test error" in parsed["error"]


def test_format_openai_result_nested():
    """Test formatting nested data structures."""
    nested_data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    
    result = format_openai_result(nested_data)
    parsed = json.loads(result)
    
    assert len(parsed["result"]["users"]) == 2
    assert parsed["result"]["users"][0]["name"] == "Alice"
    assert parsed["result"]["total"] == 2


def test_format_openai_result_boolean():
    """Test formatting boolean results."""
    result_true = format_openai_result(True)
    result_false = format_openai_result(False)
    
    assert json.loads(result_true)["result"] is True
    assert json.loads(result_false)["result"] is False


def test_format_openai_result_null():
    """Test formatting None/null results."""
    result = format_openai_result(None)
    parsed = json.loads(result)
    
    assert parsed["result"] is None


def test_validate_openai_response_malformed():
    """Test validation with malformed response structure."""
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": "not a list"  # Should be list
                }
            }
        ]
    }
    
    # Should still be considered valid as long as basic structure exists
    assert validate_openai_response(response) is True
