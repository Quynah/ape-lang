"""
Tests for executor: OpenAI function calling → Ape runtime.
Mirrors ape-anthropic executor tests for provider parity.
"""

import pytest
from unittest.mock import Mock, patch

from ape_openai.executor import (
    execute_openai_call,
    ApeOpenAIFunction
)


def test_execute_openai_call_success():
    """Test successful execution of OpenAI function calling."""
    # Mock Ape module with proper signature
    mock_signature = Mock()
    mock_signature.inputs = {"a": "int", "b": "int"}

    mock_module = Mock()
    mock_module.call.return_value = 42
    mock_module.get_function_signature.return_value = mock_signature

    input_dict = {"a": 10, "b": 32}
    result = execute_openai_call(mock_module, "add", input_dict)

    assert result == 42
    mock_module.call.assert_called_once_with("add", a=10, b=32)


def test_execute_openai_call_missing_required_key():
    """Test handling of missing required parameter."""
    mock_signature = Mock()
    mock_signature.inputs = {"a": "int", "b": "int"}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature

    input_dict = {"a": 10}  # Missing 'b'

    with pytest.raises(TypeError, match="Missing required arguments"):
        execute_openai_call(mock_module, "add", input_dict)


def test_execute_openai_call_unknown_function():
    """Test handling of unknown function."""
    from ape import ApeValidationError

    mock_module = Mock()
    mock_module.get_function_signature.side_effect = KeyError("Function not found")
    mock_module.list_functions.return_value = ["add", "subtract"]

    input_dict = {"x": 5}

    with pytest.raises(KeyError, match="Function 'unknown' not found"):
        execute_openai_call(mock_module, "unknown", input_dict)


def test_execute_openai_call_execution_error():
    """Test handling of execution error."""
    from ape import ApeExecutionError

    mock_signature = Mock()
    mock_signature.inputs = {"x": "int"}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.side_effect = Exception("Execution failed")

    input_dict = {"x": 5}

    with pytest.raises(ApeExecutionError, match="Execution of 'calculate' failed"):
        execute_openai_call(mock_module, "calculate", input_dict)


def test_execute_openai_call_empty_arguments():
    """Test execution with empty arguments."""
    mock_signature = Mock()
    mock_signature.inputs = {}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.return_value = "timestamp"

    input_dict = {}
    result = execute_openai_call(mock_module, "get_timestamp", input_dict)

    assert result == "timestamp"
    mock_module.call.assert_called_once_with("get_timestamp")


def test_execute_openai_call_extra_arguments():
    """Test handling of extra unknown arguments."""
    mock_signature = Mock()
    mock_signature.inputs = {"a": "int"}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature

    input_dict = {"a": 10, "b": 20, "c": 30}  # Extra: b, c

    with pytest.raises(TypeError, match="Unknown arguments"):
        execute_openai_call(mock_module, "add", input_dict)


def test_ape_openai_function_from_ape_file():
    """Test creating ApeOpenAIFunction from Ape file."""
    # Mock the compile function at module level
    with patch('ape_openai.executor.ape_compile') as mock_compile:
        mock_module = Mock()
        mock_compile.return_value = mock_module

        # Mock function signature
        mock_sig = Mock()
        mock_sig.name = "add"
        mock_sig.inputs = {"a": "int", "b": "int"}
        mock_sig.output = "int"
        mock_sig.description = "Add two numbers"

        mock_module.get_function_signature.return_value = mock_sig

        ape_func = ApeOpenAIFunction.from_ape_file("add.ape", "add")

        assert ape_func.function_name == "add"
        assert ape_func.signature.name == "add"
        mock_compile.assert_called_once_with("add.ape")


def test_ape_openai_function_to_openai_function():
    """Test converting ApeOpenAIFunction to OpenAI function schema."""
    # Create properly structured mock module
    mock_signature = Mock()
    mock_signature.name = "multiply"
    mock_signature.inputs = {"x": "int", "y": "int"}
    mock_signature.output = "int"
    mock_signature.description = "Multiply two numbers"

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature

    ape_func = ApeOpenAIFunction(mock_module, "multiply", "Multiply two numbers")
    function_schema = ape_func.to_openai_function()

    assert function_schema["name"] == "multiply"
    assert function_schema["description"] == "Multiply two numbers"
    assert "parameters" in function_schema


def test_ape_openai_function_execute():
    """Test executing ApeOpenAIFunction."""
    mock_signature = Mock()
    mock_signature.name = "multiply"
    mock_signature.inputs = {"x": "int", "y": "int"}

    mock_module = Mock()
    mock_module.call.return_value = 100
    mock_module.get_function_signature.return_value = mock_signature

    ape_func = ApeOpenAIFunction(mock_module, "multiply")

    input_dict = {"x": 10, "y": 10}
    result = ape_func.execute(input_dict)

    assert result == 100
    mock_module.call.assert_called_once_with("multiply", x=10, y=10)


def test_ape_openai_function_execute_with_validation_error():
    """Test execution with validation error."""
    from ape import ApeExecutionError

    mock_signature = Mock()
    mock_signature.name = "calculate"
    mock_signature.inputs = {"value": "int"}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.side_effect = TypeError("Wrong type")

    ape_func = ApeOpenAIFunction(mock_module, "calculate")

    input_dict = {"value": "not an int"}

    with pytest.raises(ApeExecutionError):
        ape_func.execute(input_dict)


def test_execute_openai_call_with_nested_dict():
    """Test execution with nested dictionary arguments."""
    mock_signature = Mock()
    mock_signature.inputs = {"config": "dict", "items": "list"}

    mock_module = Mock()
    mock_module.get_function_signature.return_value = mock_signature
    mock_module.call.return_value = {"status": "success"}

    input_dict = {
        "config": {
            "threshold": 0.5,
            "enabled": True
        },
        "items": [1, 2, 3]
    }

    result = execute_openai_call(mock_module, "process", input_dict)

    assert result == {"status": "success"}
    mock_module.call.assert_called_once()


def test_ape_openai_function_missing_function():
    """Test error when function doesn't exist in module."""
    with patch('ape_openai.executor.ape_compile') as mock_compile:
        mock_module = Mock()
        mock_module.get_function_signature.side_effect = KeyError("Function not found")
        mock_module.list_functions.return_value = ["func1", "func2"]
        mock_compile.return_value = mock_module

        with pytest.raises(KeyError):
            ApeOpenAIFunction.from_ape_file("test.ape", "nonexistent_func")
