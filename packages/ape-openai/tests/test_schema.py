"""
Tests for schema conversion: Ape → OpenAI.
Mirrors ape-anthropic schema tests for provider parity.
"""

from ape_openai.schema import (
    ape_task_to_openai_schema,
    map_ape_type_to_openai,
    openai_schema_to_ape_stub,
    APE_TO_OPENAI_TYPE_MAP
)
from ape_openai import ApeTask


def test_map_ape_type_to_openai():
    """Test type mapping from Ape to OpenAI."""
    assert map_ape_type_to_openai("String") == "string"
    assert map_ape_type_to_openai("Integer") == "integer"
    assert map_ape_type_to_openai("Float") == "number"
    assert map_ape_type_to_openai("Boolean") == "boolean"
    assert map_ape_type_to_openai("List") == "array"
    assert map_ape_type_to_openai("Dict") == "object"
    assert map_ape_type_to_openai("Unknown") == "string"  # Fallback


def test_ape_task_to_openai_schema_basic():
    """Test basic schema conversion."""
    task = ApeTask(
        name="add",
        inputs={"a": "int", "b": "int"},
        output="int",
        description="Add two numbers"
    )
    
    schema = ape_task_to_openai_schema(task)
    
    assert schema["name"] == "add"
    assert schema["description"] == "Add two numbers"
    
    parameters = schema["parameters"]
    assert parameters["type"] == "object"
    assert "a" in parameters["properties"]
    assert "b" in parameters["properties"]
    assert parameters["properties"]["a"]["type"] == "integer"
    assert parameters["properties"]["b"]["type"] == "integer"
    assert set(parameters["required"]) == {"a", "b"}


def test_ape_task_to_openai_schema_no_description():
    """Test schema conversion without description."""
    task = ApeTask(
        name="multiply",
        inputs={"x": "float", "y": "float"},
        output="float"
    )
    
    schema = ape_task_to_openai_schema(task)
    
    assert schema["description"] == "Deterministic Ape task: multiply"


def test_ape_task_to_openai_schema_various_types():
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
    
    schema = ape_task_to_openai_schema(task)
    props = schema["parameters"]["properties"]
    
    assert props["name"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["rate"]["type"] == "number"
    assert props["enabled"]["type"] == "boolean"
    assert props["items"]["type"] == "array"


def test_openai_schema_to_ape_stub():
    """Test reverse conversion: OpenAI schema → Ape stub."""
    schema = {
        "name": "calculate_tax",
        "parameters": {
            "properties": {
                "amount": {"type": "number"},
                "rate": {"type": "number"}
            }
        }
    }
    
    ape_stub = openai_schema_to_ape_stub(schema)
    
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
    
    schema = ape_task_to_openai_schema(task)
    
    assert schema["parameters"]["properties"] == {}
    assert schema["parameters"]["required"] == []


def test_type_mapping_completeness():
    """Test that all defined types have mappings."""
    for ape_type in APE_TO_OPENAI_TYPE_MAP:
        openai_type = map_ape_type_to_openai(ape_type)
        assert openai_type in ["string", "integer", "number", "boolean", "array", "object"]
