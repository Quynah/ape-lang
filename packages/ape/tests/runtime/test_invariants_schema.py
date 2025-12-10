"""
APE Core Invariants: Schema & Type Mapping

These tests encode the type system and schema guarantees that ALL provider adapters
must rely on. They test the provider-agnostic type mapping layer.

Design Principles:
- No provider SDKs (no JSON Schema specifics for Claude/OpenAI)
- Test APE's internal type system representation
- Ensure type mappings are stable and complete
"""

import pytest
from typing import Dict, Optional

from ape.runtime.core import FunctionSignature


# ============================================================================
# B. SCHEMA / TYPE MAPPING INVARIANTS
# ============================================================================

class TestFunctionSignatureInvariants:
    """
    APE Invariant: FunctionSignature structure and behavior.
    
    This is the core metadata structure that all provider adapters use
    to understand what a function expects and returns.
    """
    
    def test_function_signature_structure(self):
        """
        APE invariant: FunctionSignature has required fields.
        
        All provider adapters depend on this structure:
        - name: str
        - inputs: Dict[str, str] (param_name -> type_name)
        - output: Optional[str]
        - description: Optional[str]
        """
        sig = FunctionSignature(
            name="test_func",
            inputs={"x": "int", "y": "str"},
            output="bool",
            description="Test function"
        )
        
        assert sig.name == "test_func"
        assert sig.inputs == {"x": "int", "y": "str"}
        assert sig.output == "bool"
        assert sig.description == "Test function"
    
    def test_function_signature_no_parameters(self):
        """
        APE invariant: FunctionSignature supports zero-parameter functions.
        
        Given: A function with no parameters
        Then: inputs is an empty dict, required list should be empty
        """
        sig = FunctionSignature(
            name="get_time",
            inputs={},
            output="str"
        )
        
        assert sig.name == "get_time"
        assert sig.inputs == {}
        assert len(sig.inputs) == 0
        assert sig.output == "str"
    
    def test_function_signature_no_output(self):
        """
        APE invariant: FunctionSignature supports void/no-return functions.
        
        Given: A function with no return value
        Then: output is None
        """
        sig = FunctionSignature(
            name="log_message",
            inputs={"msg": "str"},
            output=None
        )
        
        assert sig.name == "log_message"
        assert sig.output is None
    
    def test_function_signature_no_description(self):
        """
        APE invariant: FunctionSignature description is optional.
        
        Provider adapters should handle missing descriptions gracefully
        (e.g., generate default description).
        """
        sig = FunctionSignature(
            name="calculate",
            inputs={"x": "int"},
            description=None
        )
        
        assert sig.name == "calculate"
        assert sig.description is None


class TestTypeSystemInvariants:
    """
    APE Invariant: Type system stability.
    
    These tests ensure that APE's type names are stable and recognized.
    Provider adapters map these to their respective type systems
    (e.g., JSON Schema for Claude, TypeScript for OpenAI function calling).
    """
    
    def test_primitive_types_are_strings(self):
        """
        APE invariant: Types are represented as strings.
        
        All type names in FunctionSignature.inputs and .output are strings.
        This allows provider adapters to map them consistently.
        """
        sig = FunctionSignature(
            name="test",
            inputs={
                "s": "str",
                "i": "int",
                "f": "float",
                "b": "bool"
            }
        )
        
        # All values must be strings
        for param_name, type_name in sig.inputs.items():
            assert isinstance(type_name, str), f"Type for {param_name} must be string, got {type(type_name)}"
    
    def test_common_ape_types_recognized(self):
        """
        APE invariant: Common APE types are represented consistently.
        
        These are the core types that providers must map:
        - str / String
        - int / Integer
        - float / Float
        - bool / Boolean
        - list / List
        - dict / Dict
        
        Note: Exact capitalization may vary, but consistency within a module is key.
        """
        # This test documents the expected type names
        # Provider adapters must handle these at minimum
        
        expected_types = [
            "str", "int", "float", "bool",  # Python style
            "String", "Integer", "Float", "Boolean",  # Ape style
            "list", "List", "dict", "Dict"  # Container types
        ]
        
        # Each of these should be valid type names
        for type_name in expected_types:
            sig = FunctionSignature(
                name="test",
                inputs={"param": type_name}
            )
            assert sig.inputs["param"] == type_name
    
    def test_complex_type_annotations_preserved(self):
        """
        APE invariant: Complex type annotations are preserved as strings.
        
        Even if the original annotation is complex (e.g., List[Dict[str, int]]),
        it should be converted to a string representation that providers can parse.
        """
        sig = FunctionSignature(
            name="process",
            inputs={
                "items": "list",  # Generic list
                "config": "dict"  # Generic dict
            }
        )
        
        # Verify these are stored as strings
        assert isinstance(sig.inputs["items"], str)
        assert isinstance(sig.inputs["config"], str)


class TestSignatureValidation:
    """
    APE Invariant: Signature validation and consistency.
    
    These tests ensure that signatures are internally consistent and
    provider adapters can rely on their structure.
    """
    
    def test_signature_with_all_fields(self):
        """
        APE invariant: Complete signature includes all metadata.
        
        A fully-specified signature should have:
        - Non-empty name
        - Inputs dict (may be empty)
        - Output type (may be None)
        - Description (may be None)
        """
        sig = FunctionSignature(
            name="complete_func",
            inputs={"a": "int", "b": "str", "c": "bool"},
            output="dict",
            description="A complete function signature"
        )
        
        assert sig.name
        assert isinstance(sig.inputs, dict)
        assert len(sig.inputs) == 3
        assert sig.output == "dict"
        assert sig.description
    
    def test_signature_inputs_must_be_dict(self):
        """
        APE invariant: inputs field must be a dict.
        
        Provider adapters depend on inputs being a dict[str, str].
        """
        sig = FunctionSignature(
            name="test",
            inputs={"x": "int"}
        )
        
        assert isinstance(sig.inputs, dict)
        
        # All keys must be strings (parameter names)
        for key in sig.inputs.keys():
            assert isinstance(key, str)
        
        # All values must be strings (type names)
        for value in sig.inputs.values():
            assert isinstance(value, str)
    
    def test_multiple_parameters_order_preserved(self):
        """
        APE invariant: Parameter order in inputs dict should be consistent.
        
        Note: In Python 3.7+, dicts preserve insertion order.
        Provider adapters may rely on this for positional argument mapping.
        """
        sig = FunctionSignature(
            name="multi_param",
            inputs={"first": "str", "second": "int", "third": "bool"}
        )
        
        # Order should be preserved (Python 3.7+ guarantee)
        param_names = list(sig.inputs.keys())
        assert param_names == ["first", "second", "third"]
