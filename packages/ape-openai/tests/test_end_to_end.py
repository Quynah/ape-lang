"""
End-to-end integration tests for ape-openai.

Tests the complete flow: schema conversion → execution with validation.
Mirrors ape-anthropic test behaviour to ensure provider parity.
"""

import pytest
from unittest.mock import Mock

from ape_openai.schema import ape_task_to_openai_schema
from ape_openai.executor import execute_openai_call


def test_end_to_end_simple_function():
    """Test complete flow with a simple add function."""
    # Create a stub ApeModule
    mock_signature = Mock()
    mock_signature.name = "add"
    mock_signature.inputs = {"a": "int", "b": "int"}
    mock_signature.output = "int"
    mock_signature.description = "Add two integers"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.return_value = 15

    # Convert to OpenAI function schema
    function_schema = ape_task_to_openai_schema(mock_signature)

    # Verify schema structure (OpenAI format)
    assert function_schema["name"] == "add"
    assert function_schema["description"] == "Add two integers"
    assert "parameters" in function_schema
    assert function_schema["parameters"]["type"] == "object"
    assert "a" in function_schema["parameters"]["properties"]
    assert "b" in function_schema["parameters"]["properties"]

    # Execute with OpenAI-style input
    input_dict = {"a": 7, "b": 8}
    result = execute_openai_call(mock_module, "add", input_dict)

    # Verify execution
    assert result == 15
    mock_module.call.assert_called_once_with("add", a=7, b=8)


def test_end_to_end_complex_function():
    """Test complete flow with complex nested data."""
    # Create a stub ApeModule with complex signature
    mock_signature = Mock()
    mock_signature.name = "process_order"
    mock_signature.inputs = {
        "customer_id": "str",
        "items": "list",
        "shipping_address": "dict"
    }
    mock_signature.output = "dict"
    mock_signature.description = "Process customer order"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.return_value = {
        "order_id": "ORD-12345",
        "status": "confirmed",
        "total": 99.99
    }

    # Convert to OpenAI function schema
    function_schema = ape_task_to_openai_schema(mock_signature)

    # Verify schema has all properties
    assert function_schema["name"] == "process_order"
    properties = function_schema["parameters"]["properties"]
    assert "customer_id" in properties
    assert "items" in properties
    assert "shipping_address" in properties

    # Execute with OpenAI-style nested input
    input_dict = {
        "customer_id": "CUST-789",
        "items": [
            {"product_id": "P-001", "quantity": 2},
            {"product_id": "P-002", "quantity": 1}
        ],
        "shipping_address": {
            "street": "123 Main St",
            "city": "Amsterdam",
            "country": "NL"
        }
    }

    result = execute_openai_call(mock_module, "process_order", input_dict)

    # Verify execution
    assert result["order_id"] == "ORD-12345"
    assert result["status"] == "confirmed"
    mock_module.call.assert_called_once()


def test_end_to_end_validation_error():
    """Test that validation errors are caught end-to-end."""
    from ape import ApeExecutionError

    mock_signature = Mock()
    mock_signature.name = "divide"
    mock_signature.inputs = {"a": "int", "b": "int"}
    mock_signature.output = "float"
    mock_signature.description = "Divide two numbers"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.side_effect = ZeroDivisionError("Cannot divide by zero")

    # Convert to schema
    function_schema = ape_task_to_openai_schema(mock_signature)
    assert function_schema["name"] == "divide"

    # Execute with invalid input (will trigger error)
    input_dict = {"a": 10, "b": 0}

    with pytest.raises(ApeExecutionError):
        execute_openai_call(mock_module, "divide", input_dict)


def test_end_to_end_missing_parameter():
    """Test schema validation catches missing parameters."""
    mock_signature = Mock()
    mock_signature.name = "multiply"
    mock_signature.inputs = {"x": "int", "y": "int"}
    mock_signature.output = "int"
    mock_signature.description = "Multiply two integers"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature

    # Convert to schema
    function_schema = ape_task_to_openai_schema(mock_signature)

    # Verify required fields
    assert set(function_schema["parameters"]["required"]) == {"x", "y"}

    # Try to execute with missing parameter
    input_dict = {"x": 5}  # Missing 'y'

    with pytest.raises(TypeError, match="Missing required arguments"):
        execute_openai_call(mock_module, "multiply", input_dict)


def test_end_to_end_no_parameters():
    """Test function with no input parameters."""
    mock_signature = Mock()
    mock_signature.name = "get_timestamp"
    mock_signature.inputs = {}
    mock_signature.output = "str"
    mock_signature.description = "Get current timestamp"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.return_value = "2024-12-04T10:30:00Z"

    # Convert to schema
    function_schema = ape_task_to_openai_schema(mock_signature)

    # Verify schema structure for no-param function
    assert function_schema["name"] == "get_timestamp"
    assert function_schema["parameters"]["properties"] == {}
    assert function_schema["parameters"]["required"] == []

    # Execute with empty input
    result = execute_openai_call(mock_module, "get_timestamp", {})

    assert result == "2024-12-04T10:30:00Z"
    mock_module.call.assert_called_once_with("get_timestamp")
