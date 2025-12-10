"""
Tests for schema conversion: Ape → LangChain tools.
Mirrors ape-anthropic schema tests for provider parity.
"""

import pytest

from ape_langchain.schema import (
    ape_task_to_langchain_schema,
    map_ape_type_to_json_schema,
    map_ape_type_to_python,
    APE_TO_JSON_SCHEMA_TYPE,
    APE_TO_PYTHON_TYPE_MAP
)
from ape_langchain import ApeTask


def test_map_ape_type_to_json_schema():
    """Test type mapping from Ape to JSON Schema."""
    assert map_ape_type_to_json_schema("String") == "string"
    assert map_ape_type_to_json_schema("Integer") == "integer"
    assert map_ape_type_to_json_schema("Float") == "number"
    assert map_ape_type_to_json_schema("Boolean") == "boolean"
    assert map_ape_type_to_json_schema("List") == "array"
    assert map_ape_type_to_json_schema("Dict") == "object"
    assert map_ape_type_to_json_schema("Unknown") == "string"


def test_map_ape_type_to_python():
    """Test type mapping from Ape to Python."""
    assert map_ape_type_to_python("String") == str
    assert map_ape_type_to_python("Integer") == int
    assert map_ape_type_to_python("Float") == float
    assert map_ape_type_to_python("Boolean") == bool
    assert map_ape_type_to_python("List") == list
    assert map_ape_type_to_python("Dict") == dict


def test_ape_task_to_langchain_schema_basic():
    """Test basic schema conversion."""
    task = ApeTask(
        name="add",
        inputs={"a": "int", "b": "int"},
        output="int",
        description="Add two numbers"
    )
    
    schema = ape_task_to_langchain_schema(task)
    
    assert schema["name"] == "add"
    assert schema["description"] == "Add two numbers"
    
    args_schema = schema["args_schema"]
    assert args_schema["type"] == "object"
    assert "a" in args_schema["properties"]
    assert "b" in args_schema["properties"]
    assert args_schema["properties"]["a"]["type"] == "integer"
    assert args_schema["properties"]["b"]["type"] == "integer"
    assert set(args_schema["required"]) == {"a", "b"}


def test_ape_task_to_langchain_schema_no_description():
    """Test schema conversion without description."""
    task = ApeTask(
        name="multiply",
        inputs={"x": "float", "y": "float"},
        output="float"
    )
    
    schema = ape_task_to_langchain_schema(task)
    
    assert schema["description"] == "Deterministic Ape task: multiply"


def test_ape_task_to_langchain_schema_various_types():
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
    
    schema = ape_task_to_langchain_schema(task)
    props = schema["args_schema"]["properties"]
    
    assert props["name"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["rate"]["type"] == "number"
    assert props["enabled"]["type"] == "boolean"
    assert props["items"]["type"] == "array"


def test_ape_task_empty_inputs():
    """Test schema conversion with no inputs."""
    task = ApeTask(
        name="get_timestamp",
        inputs={},
        output="String"
    )
    
    schema = ape_task_to_langchain_schema(task)
    
    assert schema["args_schema"]["properties"] == {}
    assert schema["args_schema"]["required"] == []


def test_type_mapping_completeness():
    """Test that all defined types have mappings."""
    for ape_type in APE_TO_JSON_SCHEMA_TYPE:
        json_type = map_ape_type_to_json_schema(ape_type)
        assert json_type in ["string", "integer", "number", "boolean", "array", "object"]
    
    for ape_type in APE_TO_PYTHON_TYPE_MAP:
        python_type = map_ape_type_to_python(ape_type)
        assert python_type in [str, int, float, bool, list, dict]
