"""
Tests for LangChain utils functions.
"""

from ape_langchain.utils import (
    format_langchain_result,
    validate_tool_input
)


def test_format_langchain_result_primitive():
    """Test formatting primitive result."""
    result = format_langchain_result(42)
    assert result == {"result": 42}


def test_format_langchain_result_string():
    """Test formatting string result."""
    result = format_langchain_result("hello")
    assert result == {"result": "hello"}


def test_format_langchain_result_list():
    """Test formatting list result."""
    result = format_langchain_result([1, 2, 3])
    assert result == {"result": [1, 2, 3]}


def test_format_langchain_result_dict():
    """Test formatting dict result."""
    result = format_langchain_result({"status": "ok"})
    assert result == {"result": {"status": "ok"}}


def test_format_langchain_result_nested():
    """Test formatting nested structures."""
    data = {"items": [1, 2, 3], "meta": {"count": 3}}
    result = format_langchain_result(data)
    assert result == {"result": data}


def test_format_langchain_result_boolean():
    """Test formatting boolean result."""
    result = format_langchain_result(True)
    assert result == {"result": True}


def test_format_langchain_result_null():
    """Test formatting None result."""
    result = format_langchain_result(None)
    assert result == {"result": None}


def test_validate_tool_input_valid():
    """Test validation with all required fields."""
    data = {"a": 10, "b": 20}
    fields = ["a", "b"]
    assert validate_tool_input(data, fields) is True


def test_validate_tool_input_missing_field():
    """Test validation with missing required field."""
    data = {"a": 10}
    fields = ["a", "b"]
    assert validate_tool_input(data, fields) is False


def test_validate_tool_input_empty():
    """Test validation with empty data."""
    data = {}
    fields = ["a"]
    assert validate_tool_input(data, fields) is False
