"""
Schema conversion: Ape tasks → LangChain tool schemas.

Converts Ape task signatures to LangChain-compatible tool format.
"""

from typing import Dict, Any


# Type mapping from Ape to Python/LangChain types
APE_TO_PYTHON_TYPE_MAP = {
    "str": str,
    "string": str,
    "String": str,
    "int": int,
    "integer": int,
    "Integer": int,
    "float": float,
    "Float": float,
    "Decimal": float,
    "bool": bool,
    "boolean": bool,
    "Boolean": bool,
    "list": list,
    "List": list,
    "dict": dict,
    "Dict": dict,
    "Any": str,  # Fallback
}


# Type mapping for JSON Schema representation
APE_TO_JSON_SCHEMA_TYPE = {
    "str": "string",
    "string": "string",
    "String": "string",
    "int": "integer",
    "integer": "integer",
    "Integer": "integer",
    "float": "number",
    "Float": "number",
    "Decimal": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "Boolean": "boolean",
    "list": "array",
    "List": "array",
    "dict": "object",
    "Dict": "object",
    "Any": "string",
}


def map_ape_type_to_python(ape_type: str) -> type:
    """
    Map an Ape type to Python type.
    
    Args:
        ape_type: Ape type string (e.g., "String", "Integer")
        
    Returns:
        Python type (e.g., str, int)
    """
    return APE_TO_PYTHON_TYPE_MAP.get(ape_type, str)


def map_ape_type_to_json_schema(ape_type: str) -> str:
    """
    Map an Ape type to JSON Schema type.
    
    Args:
        ape_type: Ape type string
        
    Returns:
        JSON Schema type string
    """
    return APE_TO_JSON_SCHEMA_TYPE.get(ape_type, "string")


def ape_task_to_langchain_schema(task: Any) -> Dict[str, Any]:
    """
    Convert an Ape task to LangChain tool schema.

    Takes an ApeTask object and converts it to the format used by
    LangChain's StructuredTool.

    Args:
        task: ApeTask instance with name, inputs, output, and description

    Returns:
        LangChain tool schema dictionary with args_schema

    Example:
        >>> task = ApeTask(name="add", inputs={"a": "int", "b": "int"})
        >>> schema = ape_task_to_langchain_schema(task)
    """
    # Build args schema for Pydantic
    properties = {}
    required = []

    for param_name, param_type in task.inputs.items():
        json_type = map_ape_type_to_json_schema(param_type)
        properties[param_name] = {
            "type": json_type,
            "title": param_name.replace("_", " ").title()
        }
        required.append(param_name)

    # LangChain-compatible schema
    schema = {
        "name": task.name,
        "description": task.description or f"Deterministic Ape task: {task.name}",
        "args_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    return schema


def create_pydantic_model(task: Any) -> type:
    """
    Create a Pydantic model from an Ape task for LangChain.
    
    Args:
        task: ApeTask instance
        
    Returns:
        Pydantic BaseModel class
    """
    try:
        from pydantic import BaseModel, Field, create_model
    except ImportError:
        raise ImportError(
            "LangChain integration requires pydantic. "
            "Install it with: pip install ape-langchain[langchain]"
        )

    # Build field definitions
    fields = {}
    for param_name, param_type in task.inputs.items():
        python_type = map_ape_type_to_python(param_type)
        field_description = f"{param_name} parameter"
        fields[param_name] = (python_type, Field(description=field_description))

    # Create dynamic model
    model_name = f"{task.name.title()}Input"
    return create_model(model_name, **fields)


__all__ = [
    "ape_task_to_langchain_schema",
    "map_ape_type_to_python",
    "map_ape_type_to_json_schema",
    "create_pydantic_model",
    "APE_TO_PYTHON_TYPE_MAP",
    "APE_TO_JSON_SCHEMA_TYPE",
]
