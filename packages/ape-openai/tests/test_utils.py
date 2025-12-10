"""
Tests for utility functions.
Mirrors ape-anthropic utils tests for provider parity.
"""

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


def test_validate_openai_response_no_choices():
    """Test validation with missing choices."""
    response = {}
    assert validate_openai_response(response) is False


def test_validate_openai_response_empty_choices():
    """Test validation with empty choices."""
    response = {"choices": []}
    assert validate_openai_response(response) is False


def test_validate_openai_response_no_message():
    """Test validation with missing message."""
    response = {"choices": [{}]}
    assert validate_openai_response(response) is False


def test_validate_openai_response_no_tool_calls():
    """Test validation with missing tool_calls."""
    response = {
        "choices": [
            {
                "message": {}
            }
        ]
    }
    assert validate_openai_response(response) is False


def test_validate_openai_response_empty_tool_calls():
    """Test validation with empty tool_calls."""
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": []
                }
            }
        ]
    }
    assert validate_openai_response(response) is False


def test_validate_openai_response_invalid_function():
    """Test validation with invalid function structure."""
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {}
                        }
                    ]
                }
            }
        ]
    }
    assert validate_openai_response(response) is False


def test_validate_openai_response_missing_arguments():
    """Test validation with missing function arguments."""
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "add"
                            }
                        }
                    ]
                }
            }
        ]
    }
    assert validate_openai_response(response) is False
