"""
Tests for schema conversion: Ape → Claude.
"""

import pytest
from unittest.mock import Mock

from ape_anthropic.schema import (
    ape_task_to_claude_schema,
    map_ape_type_to_claude,
    claude_schema_to_ape_stub,
    APE_TO_CLAUDE_TYPE_MAP
)
from ape_anthropic import ApeTask


def test_map_ape_type_to_claude():
    """Test type mapping from Ape to Claude."""
    assert map_ape_type_to_claude("String") == "string"
    assert map_ape_type_to_claude("Integer") == "integer"
    assert map_ape_type_to_claude("Float") == "number"
    assert map_ape_type_to_claude("Boolean") == "boolean"
    assert map_ape_type_to_claude("List") == "array"
    assert map_ape_type_to_claude("Dict") == "object"
    assert map_ape_type_to_claude("Unknown") == "string"  # Fallback


def test_ape_task_to_claude_schema_basic():
    """Test basic schema conversion."""
    task = ApeTask(
        name="add",
        inputs={"a": "int", "b": "int"},
        output="int",
        description="Add two numbers"
    )
    
    schema = ape_task_to_claude_schema(task)
    
    assert schema["name"] == "add"
    assert schema["description"] == "Add two numbers"
    
    input_schema = schema["input_schema"]
    assert input_schema["type"] == "object"
    assert "a" in input_schema["properties"]
    assert "b" in input_schema["properties"]
    assert input_schema["properties"]["a"]["type"] == "integer"
    assert input_schema["properties"]["b"]["type"] == "integer"
    assert set(input_schema["required"]) == {"a", "b"}


def test_ape_task_to_claude_schema_no_description():
    """Test schema conversion without description."""
    task = ApeTask(
        name="multiply",
        inputs={"x": "float", "y": "float"},
        output="float"
    )
    
    schema = ape_task_to_claude_schema(task)
    
    assert schema["description"] == "Deterministic Ape task: multiply"


def test_ape_task_to_claude_schema_various_types():
    """Test schema conversion with various types."""
    task = ApeTask(
        name="complex_task",
        inputs={
            "name": "String",
            "count": "Integer",
            "rate": "Float",
            "enabled": "Boolean",
            "items": "List"
        }
    )
    
    schema = ape_task_to_claude_schema(task)
    props = schema["input_schema"]["properties"]
    
    assert props["name"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["rate"]["type"] == "number"
    assert props["enabled"]["type"] == "boolean"
    assert props["items"]["type"] == "array"


def test_claude_schema_to_ape_stub():
    """Test reverse conversion: Claude schema → Ape stub."""
    schema = {
        "name": "calculate_tax",
        "input_schema": {
            "properties": {
                "amount": {"type": "number"},
                "rate": {"type": "number"}
            }
        }
    }
    
    ape_stub = claude_schema_to_ape_stub(schema)
    
    assert "task calculate_tax" in ape_stub
    assert "amount: Float" in ape_stub
    assert "rate: Float" in ape_stub
    assert "inputs:" in ape_stub
    assert "outputs:" in ape_stub
    assert "constraints:" in ape_stub
    assert "steps:" in ape_stub


def test_ape_task_empty_inputs():
    """Test schema conversion with no inputs."""
    task = ApeTask(
        name="get_timestamp",
        inputs={},
        output="String"
    )
    
    schema = ape_task_to_claude_schema(task)
    
    assert schema["input_schema"]["properties"] == {}
    assert schema["input_schema"]["required"] == []


def test_type_mapping_completeness():
    """Test that all defined types have mappings."""
    for ape_type in APE_TO_CLAUDE_TYPE_MAP:
        claude_type = map_ape_type_to_claude(ape_type)
        assert claude_type in ["string", "integer", "number", "boolean", "array", "object"]
