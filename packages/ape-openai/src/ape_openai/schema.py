"""
Schema conversion: Ape tasks → OpenAI function schemas.

Converts Ape task signatures to OpenAI-compatible JSON Schema format
for function calling.
"""

from typing import Dict, Any


# Type mapping from Ape to OpenAI JSON Schema
APE_TO_OPENAI_TYPE_MAP = {
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
    "Any": "string",  # Fallback
}


def map_ape_type_to_openai(ape_type: str) -> str:
    """
    Map an Ape type to OpenAI JSON Schema type.
    
    Args:
        ape_type: Ape type string (e.g., "String", "Integer")
        
    Returns:
        OpenAI JSON Schema type (e.g., "string", "integer")
    """
    return APE_TO_OPENAI_TYPE_MAP.get(ape_type, "string")


def ape_task_to_openai_schema(task: Any) -> Dict[str, Any]:
    """
    Convert an Ape task to OpenAI function schema.

    Takes an ApeTask object and converts it to the format required by
    OpenAI's function calling API.

    Args:
        task: ApeTask instance with name, inputs, output, and description

    Returns:
        OpenAI function schema dictionary

    Example:
        >>> task = ApeTask(name="add", inputs={"a": "int", "b": "int"})
        >>> schema = ape_task_to_openai_schema(task)
        >>> print(schema)
        {
            "name": "add",
            "description": "Deterministic Ape task: add",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        }
    """
    # Build properties dict
    properties = {}
    required = []

    for param_name, param_type in task.inputs.items():
        openai_type = map_ape_type_to_openai(param_type)
        properties[param_name] = {"type": openai_type}
        required.append(param_name)

    # OpenAI function schema format
    schema = {
        "name": task.name,
        "description": task.description or f"Deterministic Ape task: {task.name}",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    return schema


def openai_schema_to_ape_stub(schema: Dict[str, Any]) -> str:
    """
    Convert OpenAI function schema back to Ape task stub.
    
    Useful for generating Ape code from existing OpenAI functions.
    
    Args:
        schema: OpenAI function schema dictionary
        
    Returns:
        Ape task definition as string
    """
    name = schema.get("name", "unnamed_task")
    parameters = schema.get("parameters", {})
    properties = parameters.get("properties", {})
    
    # Reverse type mapping
    openai_to_ape = {
        "string": "String",
        "integer": "Integer",
        "number": "Float",
        "boolean": "Boolean",
        "array": "List",
        "object": "Dict"
    }
    
    lines = [f"task {name}"]
    
    # Inputs
    if properties:
        lines.append("  inputs:")
        for param_name, param_schema in properties.items():
            openai_type = param_schema.get("type", "string")
            ape_type = openai_to_ape.get(openai_type, "String")
            lines.append(f"    {param_name}: {ape_type}")
    
    # Outputs (stub)
    lines.append("  outputs:")
    lines.append("    result: Any")
    
    # Constraints (stub)
    lines.append("  constraints:")
    lines.append("    - TODO: Add constraints")
    
    # Steps (stub)
    lines.append("  steps:")
    lines.append("    - TODO: Implement logic")
    
    return "\n".join(lines)


__all__ = [
    "ape_task_to_openai_schema",
    "map_ape_type_to_openai",
    "openai_schema_to_ape_stub",
    "APE_TO_OPENAI_TYPE_MAP",
]
