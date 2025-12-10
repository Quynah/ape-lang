"""
APE Core Invariants: Executor

These tests encode the fundamental execution guarantees that ALL provider adapters
(Anthropic, OpenAI, LangChain, etc.) must rely on. They are provider-agnostic and
test only the core APE execution layer.

Design Principles:
- No provider SDKs imported (no anthropic, openai, langchain)
- No network access or API calls
- Fast, deterministic, suitable for CI
- Test dict-based invocation model that all adapters use
"""

import pytest
from typing import Dict, Any, List

from ape.runtime.core import ApeModule, FunctionSignature
from ape.runtime.context import ExecutionContext, ExecutionError


# ============================================================================
# HELPER: Pure Python functions wrapped as APE callables
# ============================================================================

def _create_simple_add_module() -> ApeModule:
    """Create a minimal ApeModule with a simple add function."""
    # Simulate a generated module with a simple function
    class GeneratedModule:
        @staticmethod
        def add(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b
    
    module = ApeModule("test_module", GeneratedModule())
    return module


def _create_nested_data_module() -> ApeModule:
    """Create an ApeModule that processes nested dict/list structures."""
    class GeneratedModule:
        @staticmethod
        def process_order(order: dict) -> int:
            """Process an order and return total item count"""
            items = order.get('items', [])
            return len(items)
        
        @staticmethod
        def calculate_total(order: dict) -> float:
            """Calculate total from nested structure"""
            items = order.get('items', [])
            total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
            return float(total)
    
    return ApeModule("nested_module", GeneratedModule())


def _create_zero_param_module() -> ApeModule:
    """Create an ApeModule with a zero-parameter function."""
    class GeneratedModule:
        @staticmethod
        def get_timestamp() -> str:
            """Get current timestamp"""
            return "2024-12-10T00:00:00Z"
    
    return ApeModule("zero_param_module", GeneratedModule())


def _create_error_prone_module() -> ApeModule:
    """Create an ApeModule with a function that raises an error."""
    class GeneratedModule:
        @staticmethod
        def divide(a: int, b: int) -> float:
            """Divide two numbers"""
            return a / b
    
    return ApeModule("error_module", GeneratedModule())


# ============================================================================
# A. EXECUTION INVARIANTS: Dict-based invocation
# ============================================================================

class TestExecutorDictBasedInvocation:
    """
    APE Invariant: All providers must support dict-based parameter passing.
    
    This is the foundational execution model that enables Claude tool use,
    OpenAI function calling, and LangChain tool integration.
    """
    
    def test_simple_function_execution(self):
        """
        APE invariant: Simple function with primitive params returns primitive result.
        
        Given: A function add(a: int, b: int) -> int
        When: Invoked via dict {"a": 2, "b": 3}
        Then: Result is 5 (unchanged primitive)
        """
        module = _create_simple_add_module()
        
        # Execute via dict-based invocation
        result = module.call("add", **{"a": 2, "b": 3})
        
        assert result == 5
        assert isinstance(result, int)
    
    def test_nested_dict_inputs(self):
        """
        APE invariant: Nested dict/list structures are passed through correctly.
        
        Given: A function processing nested data structures
        When: Invoked with nested dicts and lists
        Then: Function receives correctly structured data
        """
        module = _create_nested_data_module()
        
        # Complex nested input
        order = {
            "customer_id": "CUST-123",
            "items": [
                {"product_id": "P-001", "quantity": 2, "price": 10.0},
                {"product_id": "P-002", "quantity": 1, "price": 25.0}
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Amsterdam",
                "country": "NL"
            }
        }
        
        # Execute and verify structure is preserved
        item_count = module.call("process_order", order=order)
        assert item_count == 2
        
        total = module.call("calculate_total", order=order)
        assert total == 45.0  # (2 * 10.0) + (1 * 25.0)
    
    def test_missing_required_parameter_raises_error(self):
        """
        APE invariant: Missing required parameter must fail deterministically.
        
        Given: A function with required parameters
        When: Called with missing required key
        Then: TypeError is raised with clear message
        """
        module = _create_simple_add_module()
        
        # Missing 'b' parameter
        with pytest.raises(TypeError) as exc_info:
            module.call("add", **{"a": 10})
        
        # Error message should mention the missing parameter
        assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
    
    def test_extra_unknown_parameters(self):
        """
        APE invariant: Extra/unknown parameters are rejected.
        
        Given: A function with defined parameters
        When: Called with extra unknown keys
        Then: TypeError is raised
        """
        module = _create_simple_add_module()
        
        # Extra parameter 'c' not in signature
        with pytest.raises(TypeError) as exc_info:
            module.call("add", **{"a": 10, "b": 20, "c": 30})
        
        # Error should mention unexpected argument
        assert "unexpected" in str(exc_info.value).lower() or "got an unexpected" in str(exc_info.value).lower()
    
    def test_zero_parameter_function_with_empty_dict(self):
        """
        APE invariant: Zero-parameter functions accept empty dict.
        
        Given: A function with no parameters
        When: Called with empty dict {}
        Then: Execution succeeds
        """
        module = _create_zero_param_module()
        
        result = module.call("get_timestamp", **{})
        
        assert result == "2024-12-10T00:00:00Z"
        assert isinstance(result, str)
    
    def test_zero_parameter_function_rejects_extra_params(self):
        """
        APE invariant: Zero-parameter functions reject any parameters.
        
        Given: A function with no parameters
        When: Called with any keys
        Then: TypeError is raised
        """
        module = _create_zero_param_module()
        
        with pytest.raises(TypeError):
            module.call("get_timestamp", **{"invalid": "param"})
    
    def test_function_exception_propagates(self):
        """
        APE invariant: Exceptions from functions propagate with original info.
        
        Given: A function that raises an exception
        When: Called with inputs that trigger the exception
        Then: The exception propagates (may be wrapped, but cause is preserved)
        """
        module = _create_error_prone_module()
        
        # This will trigger ZeroDivisionError
        with pytest.raises(ZeroDivisionError) as exc_info:
            module.call("divide", **{"a": 10, "b": 0})
        
        # Verify the error message indicates division by zero
        assert "division" in str(exc_info.value).lower() or "zero" in str(exc_info.value).lower()


class TestExecutorFunctionDiscovery:
    """
    APE Invariant: Function discovery and introspection.
    
    All providers need to discover available functions and their signatures.
    """
    
    def test_list_functions(self):
        """
        APE invariant: ApeModule.list_functions() returns all callable functions.
        """
        module = _create_simple_add_module()
        
        functions = module.list_functions()
        
        assert "add" in functions
        assert isinstance(functions, list)
    
    def test_get_function_signature(self):
        """
        APE invariant: get_function_signature returns complete metadata.
        
        Given: An ApeModule with functions
        When: Requesting signature for a function
        Then: Returns FunctionSignature with name, inputs, output, description
        """
        module = _create_simple_add_module()
        
        sig = module.get_function_signature("add")
        
        assert isinstance(sig, FunctionSignature)
        assert sig.name == "add"
        assert "a" in sig.inputs
        assert "b" in sig.inputs
        assert sig.inputs["a"] == "int"
        assert sig.inputs["b"] == "int"
        assert sig.output == "int"
        assert sig.description is not None  # Has docstring
    
    def test_get_nonexistent_function_raises_keyerror(self):
        """
        APE invariant: Requesting non-existent function signature raises KeyError.
        """
        module = _create_simple_add_module()
        
        with pytest.raises(KeyError):
            module.get_function_signature("nonexistent_function")
    
    def test_call_nonexistent_function_raises_attributeerror(self):
        """
        APE invariant: Calling non-existent function raises AttributeError.
        
        The error message should list available functions.
        """
        module = _create_simple_add_module()
        
        with pytest.raises(AttributeError) as exc_info:
            module.call("nonexistent", **{})
        
        # Error should mention available functions
        error_msg = str(exc_info.value)
        assert "not found" in error_msg or "Available" in error_msg
