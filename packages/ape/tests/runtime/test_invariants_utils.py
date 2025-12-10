"""
APE Core Invariants: Result & Error Formatting

These tests encode the formatting guarantees that ALL provider adapters rely on
for serializing results and errors. They test provider-agnostic formatting utilities.

Design Principles:
- No provider SDKs
- Test JSON-serializable output formats
- Ensure error formatting is stable and informative
"""

import pytest
import json
from typing import Any


# ============================================================================
# Helper: Generic result formatter (following Anthropic pattern)
# ============================================================================

def format_result_as_json(value: Any) -> str:
    """
    Generic result formatter that produces JSON-serializable output.
    
    This follows the pattern used by provider adapters:
    - Wrap result in {"result": value}
    - Handle non-serializable objects via str() fallback
    """
    try:
        # Try direct JSON serialization
        result_dict = {"result": value}
        return json.dumps(result_dict)
    except (TypeError, ValueError):
        # Fallback for non-serializable objects
        result_dict = {"result": str(value)}
        return json.dumps(result_dict)


def format_error_as_json(error: Exception) -> str:
    """
    Generic error formatter that produces JSON-serializable output.
    
    This follows the pattern used by provider adapters:
    - Wrap error in {"error": message}
    - Include exception type and message
    """
    error_msg = f"{type(error).__name__}: {str(error)}"
    error_dict = {"error": error_msg}
    return json.dumps(error_dict)


# ============================================================================
# C. RESULT / ERROR FORMATTING INVARIANTS
# ============================================================================

class TestResultFormattingInvariants:
    """
    APE Invariant: Result formatting for provider responses.
    
    All provider adapters need consistent JSON-serializable output.
    """
    
    def test_format_primitive_int(self):
        """
        APE invariant: Integer results are JSON-serializable.
        
        Given: An integer result
        Then: Format as {"result": <int>}
        """
        result = format_result_as_json(42)
        parsed = json.loads(result)
        
        assert "result" in parsed
        assert parsed["result"] == 42
        assert isinstance(parsed["result"], int)
    
    def test_format_primitive_float(self):
        """
        APE invariant: Float results are JSON-serializable.
        """
        result = format_result_as_json(3.14159)
        parsed = json.loads(result)
        
        assert parsed["result"] == 3.14159
        assert isinstance(parsed["result"], float)
    
    def test_format_primitive_string(self):
        """
        APE invariant: String results are JSON-serializable.
        """
        result = format_result_as_json("hello world")
        parsed = json.loads(result)
        
        assert parsed["result"] == "hello world"
        assert isinstance(parsed["result"], str)
    
    def test_format_primitive_bool(self):
        """
        APE invariant: Boolean results are JSON-serializable.
        """
        result_true = format_result_as_json(True)
        result_false = format_result_as_json(False)
        
        assert json.loads(result_true)["result"] is True
        assert json.loads(result_false)["result"] is False
    
    def test_format_null_none(self):
        """
        APE invariant: None/null results are JSON-serializable.
        """
        result = format_result_as_json(None)
        parsed = json.loads(result)
        
        assert "result" in parsed
        assert parsed["result"] is None
    
    def test_format_list_result(self):
        """
        APE invariant: List results are preserved as JSON arrays.
        
        Given: A list result [1, 2, 3, 4, 5]
        Then: Format as {"result": [1, 2, 3, 4, 5]}
        """
        result = format_result_as_json([1, 2, 3, 4, 5])
        parsed = json.loads(result)
        
        assert parsed["result"] == [1, 2, 3, 4, 5]
        assert isinstance(parsed["result"], list)
        assert len(parsed["result"]) == 5
    
    def test_format_dict_result(self):
        """
        APE invariant: Dict results are preserved as JSON objects.
        
        Given: A dict result {"status": "success", "count": 10}
        Then: Format as {"result": {"status": "success", "count": 10}}
        """
        result = format_result_as_json({"status": "success", "count": 10})
        parsed = json.loads(result)
        
        assert "result" in parsed
        assert parsed["result"]["status"] == "success"
        assert parsed["result"]["count"] == 10
    
    def test_format_nested_structure(self):
        """
        APE invariant: Nested data structures are preserved.
        
        Given: Nested dicts and lists
        Then: Structure is fully preserved in JSON
        """
        nested_data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "metadata": {
                "total": 2,
                "page": 1
            }
        }
        
        result = format_result_as_json(nested_data)
        parsed = json.loads(result)
        
        assert len(parsed["result"]["users"]) == 2
        assert parsed["result"]["users"][0]["name"] == "Alice"
        assert parsed["result"]["users"][1]["active"] is False
        assert parsed["result"]["metadata"]["total"] == 2
    
    def test_format_empty_list(self):
        """
        APE invariant: Empty lists are valid results.
        """
        result = format_result_as_json([])
        parsed = json.loads(result)
        
        assert parsed["result"] == []
        assert isinstance(parsed["result"], list)
        assert len(parsed["result"]) == 0
    
    def test_format_empty_dict(self):
        """
        APE invariant: Empty dicts are valid results.
        """
        result = format_result_as_json({})
        parsed = json.loads(result)
        
        assert parsed["result"] == {}
        assert isinstance(parsed["result"], dict)
        assert len(parsed["result"]) == 0
    
    def test_format_non_serializable_object_fallback(self):
        """
        APE invariant: Non-JSON-serializable objects fall back to str().
        
        Given: An object that can't be JSON-serialized
        Then: Format using str(obj) representation
        """
        class CustomObject:
            def __str__(self):
                return "CustomObject instance"
        
        obj = CustomObject()
        result = format_result_as_json(obj)
        parsed = json.loads(result)
        
        assert "result" in parsed
        assert isinstance(parsed["result"], str)
        assert "CustomObject" in parsed["result"]


class TestErrorFormattingInvariants:
    """
    APE Invariant: Error formatting for provider responses.
    
    All provider adapters need consistent error serialization.
    """
    
    def test_format_exception_basic(self):
        """
        APE invariant: Exceptions are formatted with type and message.
        
        Given: An exception
        Then: Format as {"error": "ExceptionType: message"}
        """
        error = ValueError("Invalid input")
        result = format_error_as_json(error)
        parsed = json.loads(result)
        
        assert "error" in parsed
        assert "ValueError" in parsed["error"]
        assert "Invalid input" in parsed["error"]
    
    def test_format_exception_preserves_type(self):
        """
        APE invariant: Exception type is included in error message.
        
        This allows provider adapters to communicate the error type
        back to the LLM/user.
        """
        errors = [
            TypeError("Wrong type"),
            AttributeError("Missing attribute"),
            KeyError("Key not found"),
            ZeroDivisionError("Division by zero")
        ]
        
        for error in errors:
            result = format_error_as_json(error)
            parsed = json.loads(result)
            
            error_type = type(error).__name__
            assert error_type in parsed["error"]
    
    def test_format_exception_includes_message(self):
        """
        APE invariant: Exception message is included in error output.
        """
        error = RuntimeError("Something went wrong in execution")
        result = format_error_as_json(error)
        parsed = json.loads(result)
        
        assert "Something went wrong" in parsed["error"]
    
    def test_format_exception_json_serializable(self):
        """
        APE invariant: Error output is always valid JSON.
        
        Even with special characters or quotes in the error message,
        the output must be valid JSON.
        """
        # Error message with quotes and special chars
        error = ValueError('Error with "quotes" and special chars: \n\t')
        result = format_error_as_json(error)
        
        # Should parse without exception
        parsed = json.loads(result)
        assert "error" in parsed
    
    def test_format_exception_empty_message(self):
        """
        APE invariant: Exceptions with empty messages are handled.
        """
        error = Exception()  # Empty message
        result = format_error_as_json(error)
        parsed = json.loads(result)
        
        assert "error" in parsed
        assert "Exception" in parsed["error"]


class TestOutputStructureInvariants:
    """
    APE Invariant: Output structure consistency.
    
    These tests ensure that the top-level structure of formatted output
    is consistent and predictable for all provider adapters.
    """
    
    def test_result_has_result_key(self):
        """
        APE invariant: Successful results always have "result" key.
        
        Provider adapters can rely on {"result": ...} structure.
        """
        test_values = [
            42,
            "string",
            True,
            None,
            [1, 2, 3],
            {"key": "value"}
        ]
        
        for value in test_values:
            result = format_result_as_json(value)
            parsed = json.loads(result)
            
            assert "result" in parsed, f"Missing 'result' key for value: {value}"
            assert parsed["result"] == value or parsed["result"] == str(value)
    
    def test_error_has_error_key(self):
        """
        APE invariant: Errors always have "error" key.
        
        Provider adapters can distinguish errors from results by key presence.
        """
        errors = [
            ValueError("test"),
            TypeError("test"),
            RuntimeError("test")
        ]
        
        for error in errors:
            result = format_error_as_json(error)
            parsed = json.loads(result)
            
            assert "error" in parsed
            # Should NOT have "result" key
            assert "result" not in parsed
    
    def test_result_and_error_are_mutually_exclusive(self):
        """
        APE invariant: Output has either "result" OR "error", never both.
        
        This prevents ambiguous responses to provider adapters.
        """
        # Result output
        success = format_result_as_json(42)
        success_parsed = json.loads(success)
        assert "result" in success_parsed
        assert "error" not in success_parsed
        
        # Error output
        error = format_error_as_json(ValueError("test"))
        error_parsed = json.loads(error)
        assert "error" in error_parsed
        assert "result" not in error_parsed
