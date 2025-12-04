"""
Schema conversion: Ape tasks → Claude tool schemas.

Converts Ape task signatures to Claude-compatible JSON Schema format
for tool use.
"""

from typing import Dict, Any


# Type mapping from Ape to Claude JSON Schema
APE_TO_CLAUDE_TYPE_MAP = {
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


def map_ape_type_to_claude(ape_type: str) -> str:
    """
    Map an Ape type to Claude JSON Schema type.
    
    Args:
        ape_type: Ape type string (e.g., "String", "Integer")
        
    Returns:
        Claude JSON Schema type (e.g., "string", "integer")
    """
    return APE_TO_CLAUDE_TYPE_MAP.get(ape_type, "string")


def ape_task_to_claude_schema(task: Any) -> Dict[str, Any]:
    """
    Convert an Ape task to Claude tool schema.

    Takes an ApeTask object and converts it to the format required by
    Claude's tool use API.

    Args:
        task: ApeTask instance with name, inputs, output, and description

    Returns:
        Claude tool schema dictionary

    Example:
        >>> task = ApeTask(name="add", inputs={"a": "int", "b": "int"})
        >>> schema = ape_task_to_claude_schema(task)
        >>> print(schema)
        {
            "name": "add",
            "description": "Deterministic Ape task: add",
            "input_schema": {
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
        claude_type = map_ape_type_to_claude(param_type)
        properties[param_name] = {"type": claude_type}
        required.append(param_name)

    # Claude tool schema format
    schema = {
        "name": task.name,
        "description": task.description or f"Deterministic Ape task: {task.name}",
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    return schema


def claude_schema_to_ape_stub(schema: Dict[str, Any]) -> str:
    """
    Convert Claude tool schema back to Ape task stub.
    
    Useful for generating Ape code from existing Claude tools.
    
    Args:
        schema: Claude tool schema dictionary
        
    Returns:
        Ape task definition as string
    """
    name = schema.get("name", "unnamed_task")
    input_schema = schema.get("input_schema", {})
    properties = input_schema.get("properties", {})
    
    # Reverse type mapping
    claude_to_ape = {
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
            claude_type = param_schema.get("type", "string")
            ape_type = claude_to_ape.get(claude_type, "String")
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
    "ape_task_to_claude_schema",
    "map_ape_type_to_claude",
    "claude_schema_to_ape_stub",
    "APE_TO_CLAUDE_TYPE_MAP",
]
