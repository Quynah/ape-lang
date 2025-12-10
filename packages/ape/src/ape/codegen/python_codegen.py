"""
Ape to Python Code Generator

Transforms Ape IR into executable Python code.
Follows the mapping rules defined in the Ape specification.
"""

from dataclasses import dataclass
from typing import List, Optional
from ape.compiler.ir_nodes import (
    ProjectNode, ModuleNode, EntityNode, TaskNode, FlowNode,
    PolicyNode, EnumNode, FieldNode, DeviationNode
)


def mangle_name(module_name: Optional[str], symbol_name: str) -> str:
    """
    Deterministic name mangling for module-qualified symbols.
    
    This is the single source of truth for name mangling in Ape v0.2.0:
    - If module_name is None or empty: return symbol_name as-is (backward compatible)
    - Otherwise: return module_name + "__" + symbol_name
    
    Args:
        module_name: The module name (e.g., "math", "strings")
        symbol_name: The symbol name (e.g., "add", "upper")
    
    Returns:
        Mangled name (e.g., "math__add", "strings__upper") or original name if no module
    
    Examples:
        >>> mangle_name("math", "add")
        'math__add'
        >>> mangle_name(None, "calculate")
        'calculate'
        >>> mangle_name("", "process")
        'process'
    """
    if module_name:
        return f"{module_name}__{symbol_name}"
    return symbol_name


@dataclass
class GeneratedFile:
    """Represents a generated source code file"""
    path: str
    language: str
    content: str


class PythonCodeGenerator:
    """
    Generates Python code from Ape IR.
    
    Mapping rules:
    - Entity → Python @dataclass
    - Enum → Python class with constants
    - Task → Python function with type hints
    - Flow → Orchestration function + metadata dict
    - Policy → Python dict
    """
    
    # Ape type to Python type mapping
    TYPE_MAPPING = {
        'String': 'str',
        'Integer': 'int',
        'Float': 'float',
        'Decimal': 'float',  # simplified for v0.1
        'Boolean': 'bool',
        'DateTime': 'datetime.datetime',
        'Date': 'datetime.date',
        'Any': 'Any',
    }
    
    def __init__(self, project_ir: ProjectNode) -> None:
        """
        Initialize the Python code generator.
        
        Args:
            project_ir: The Ape project IR to generate code from
        """
        self.project = project_ir
        self.generated_types: set = set()  # Track generated type names
        self.current_module_name: Optional[str] = None  # Track current module for name mangling
    
    def generate(self) -> List[GeneratedFile]:
        """
        Generate Python files for all modules in the project.
        
        Returns:
            List of generated files with path, language, and content
        """
        files = []
        
        for module in self.project.modules:
            generated_file = self._generate_module(module)
            files.append(generated_file)
        
        return files
    
    def _generate_module(self, module: ModuleNode) -> GeneratedFile:
        """
        Generate a Python file for a single Ape module.
        
        Args:
            module: The module IR to generate
        
        Returns:
            Generated Python file
        """
        # Set current module name for name mangling
        # Only use module name if it looks like an actual module name (not a filename)
        # This ensures backward compatibility: files without module declarations
        # get unmangled names
        module_name = module.name if module.name else None
        
        # If the "module name" is actually a filename (contains .ape), don't use it for mangling
        # This handles the case where IR builder uses filename as fallback
        if module_name and ('.ape' in module_name or '/' in module_name or '\\' in module_name):
            # Looks like a filepath, not a module name - don't mangle
            self.current_module_name = None
        else:
            self.current_module_name = module_name
        
        # Build the file content
        parts = []
        
        # File header with imports
        parts.append(self._generate_header())
        parts.append("")
        
        # Add task node registry if module has tasks
        if module.tasks:
            parts.append("# Task AST nodes for runtime execution")
            parts.append("_task_ast_nodes = {}")
            parts.append("")
        
        # Generate enums first (needed by entities)
        for enum in module.enums:
            parts.append(self._emit_enum(enum))
            parts.append("")
            self.generated_types.add(enum.name)
        
        # Generate entities
        for entity in module.entities:
            parts.append(self._emit_entity(entity))
            parts.append("")
            self.generated_types.add(entity.name)
        
        # Generate tasks
        for task in module.tasks:
            parts.append(self._emit_task(task))
            parts.append("")
        
        # Generate flows
        for flow in module.flows:
            parts.append(self._emit_flow(flow))
            parts.append("")
        
        # Generate policies
        for policy in module.policies:
            parts.append(self._emit_policy(policy))
            parts.append("")
        
        content = "\n".join(parts)
        
        # Determine file path
        module_name = module.name or "generated"
        if module_name.endswith('.ape'):
            module_name = module_name[:-4]
        
        path = f"generated/{module_name}_gen.py"
        
        return GeneratedFile(
            path=path,
            language="python",
            content=content
        )
    
    def _generate_header(self) -> str:
        """Generate the standard header for Python files"""
        return """from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any
import datetime

from ape.runtime.core import RunContext"""
    
    def _emit_entity(self, entity: EntityNode) -> str:
        """
        Generate Python @dataclass for an Ape entity.
        
        Args:
            entity: The entity IR node
        
        Returns:
            Python class definition as string
        """
        lines = []
        
        # Class decorator and definition
        lines.append("@dataclass")
        lines.append(f"class {entity.name}:")
        
        # Docstring if constraints exist
        if entity.constraints:
            lines.append('    """')
            lines.append(f"    Entity: {entity.name}")
            lines.append("    ")
            lines.append("    Constraints:")
            for constraint in entity.constraints:
                lines.append(f"        - {constraint.expression}")
            lines.append('    """')
        else:
            lines.append(f'    """Auto-generated from Ape entity \'{entity.name}\'."""')
        
        # Fields
        if not entity.fields:
            lines.append("    pass")
        else:
            for field in entity.fields:
                field_def = self._emit_field(field)
                lines.append(f"    {field_def}")
        
        return "\n".join(lines)
    
    def _emit_field(self, field: FieldNode) -> str:
        """
        Generate a field definition for a dataclass.
        
        Args:
            field: The field IR node
        
        Returns:
            Python field definition
        """
        # Map type
        python_type = self._map_type(field.type)
        
        # Handle optional
        if field.optional:
            python_type = f"{python_type} | None"
        
        # Build field definition
        if field.default is not None:
            # Has default value
            if isinstance(field.default, str):
                default_val = f'"{field.default}"'
            else:
                default_val = str(field.default)
            return f"{field.name}: {python_type} = {default_val}"
        elif field.optional:
            # Optional but no explicit default
            return f"{field.name}: {python_type} = None"
        else:
            # Required field
            return f"{field.name}: {python_type}"
    
    def _emit_enum(self, enum: EnumNode) -> str:
        """
        Generate Python class with constants for an Ape enum.
        
        Args:
            enum: The enum IR node
        
        Returns:
            Python class definition
        """
        lines = []
        
        lines.append(f"class {enum.name}:")
        lines.append(f'    """Auto-generated from Ape enum \'{enum.name}\'."""')
        
        if not enum.values:
            lines.append("    pass")
        else:
            for value in enum.values:
                # Create constant: VALUE = "value"
                const_name = value.upper()
                lines.append(f'    {const_name} = "{value}"')
        
        return "\n".join(lines)
    
    def _emit_task(self, task: TaskNode) -> str:
        """
        Generate Python function for an Ape task.
        
        Args:
            task: The task IR node
        
        Returns:
            Python function definition
        """
        lines = []
        
        # Function signature with name mangling
        func_name = mangle_name(self.current_module_name, task.name)
        
        # Build parameter list
        params = []
        for input_field in task.inputs:
            param_type = self._map_type(input_field.type)
            params.append(f"{input_field.name}: {param_type}")
        
        # Build return type
        if task.outputs:
            if len(task.outputs) == 1:
                return_type = self._map_type(task.outputs[0].type)
            else:
                # Multiple outputs → tuple
                output_types = [self._map_type(o.type) for o in task.outputs]
                return_type = f"tuple[{', '.join(output_types)}]"
        else:
            return_type = "None"
        
        # Function definition line
        param_str = ", ".join(params) if params else ""
        lines.append(f"def {func_name}({param_str}) -> {return_type}:")
        
        # Docstring
        lines.append(f'    """Auto-generated from Ape task \'{task.name}\'.')
        lines.append("")
        
        if task.constraints:
            lines.append("    Constraints:")
            for constraint in task.constraints:
                if isinstance(constraint, DeviationNode):
                    lines.append(f"        - Deviation (scope={constraint.scope}, mode={constraint.mode.value})")
                else:
                    lines.append(f"        - {constraint.expression}")
            lines.append("")
        
        if task.steps:
            lines.append("    Steps:")
            for step in task.steps:
                lines.append(f"        - {step.action}")
        
        lines.append('    """')
        
        # Body - use AST runtime execution
        lines.append("    # Execute task via AST runtime")
        lines.append("    from ape.runtime.executor import RuntimeExecutor")
        lines.append("    from ape.runtime.context import ExecutionContext")
        lines.append("    ")
        lines.append("    # Get task node from module cache")
        lines.append(f"    if '{func_name}' not in _task_cache:")
        lines.append(f"        raise NotImplementedError(f'Task {func_name} not found in cache')")
        lines.append(f"    task_node = _task_cache['{func_name}']")
        lines.append("    ")
        lines.append("    # Create execution context with inputs")
        lines.append("    context = ExecutionContext()")
        for input_field in task.inputs:
            lines.append(f"    context.set('{input_field.name}', {input_field.name})")
        lines.append("    ")
        lines.append("    # Execute task")
        lines.append("    executor = RuntimeExecutor()")
        lines.append("    result = executor.execute_task(task_node, context)")
        lines.append("    return result")
        
        return "\n".join(lines)
    
    def _emit_flow(self, flow: FlowNode) -> str:
        """
        Generate Python orchestration function + metadata for an Ape flow.
        
        Args:
            flow: The flow IR node
        
        Returns:
            Python function + metadata dict
        """
        lines = []
        
        # Metadata dict
        flow_var_name = f"FLOW_{flow.name}"
        lines.append(f"{flow_var_name} = {{")
        lines.append(f'    "name": "{flow.name}",')
        lines.append('    "trigger": {},  # TODO: add trigger metadata')
        lines.append("}")
        lines.append("")
        
        # Function definition with name mangling
        func_name = mangle_name(self.current_module_name, flow.name)
        lines.append(f"def {func_name}(context: RunContext) -> None:")
        lines.append(f'    """Auto-generated from Ape flow \'{flow.name}\'.')
        lines.append("")
        
        if flow.constraints:
            lines.append("    Constraints:")
            for constraint in flow.constraints:
                lines.append(f"        - {constraint.expression}")
            lines.append("")
        
        if flow.steps:
            lines.append("    Steps:")
            for step in flow.steps:
                lines.append(f"        - {step.action}")
        
        lines.append('    """')
        
        # Body (placeholder with step comments)
        if flow.steps:
            lines.append("    # Flow steps:")
            for i, step in enumerate(flow.steps, 1):
                lines.append(f"    # {i}. {step.action}")
        
        lines.append("    raise NotImplementedError")
        
        return "\n".join(lines)
    
    def _emit_policy(self, policy: PolicyNode) -> str:
        """
        Generate Python dict for an Ape policy.
        
        Args:
            policy: The policy IR node
        
        Returns:
            Python dict definition
        """
        lines = []
        
        policy_var_name = f"POLICY_{policy.name}"
        lines.append(f"{policy_var_name} = {{")
        lines.append(f'    "name": "{policy.name}",')
        lines.append(f'    "scope": "{policy.scope}",')
        lines.append('    "rules": [')
        
        for rule in policy.rules:
            lines.append(f'        "{rule}",')
        
        lines.append("    ],")
        lines.append('    "enforcement": {},  # TODO: add enforcement metadata')
        lines.append("}")
        
        return "\n".join(lines)
    
    def _map_type(self, ape_type: str) -> str:
        """
        Map an Ape type to a Python type.
        
        Args:
            ape_type: The Ape type name
        
        Returns:
            Python type annotation as string
        """
        # Handle List[X]
        if ape_type.startswith('List[') and ape_type.endswith(']'):
            inner_type = ape_type[5:-1]
            mapped_inner = self._map_type(inner_type)
            return f"list[{mapped_inner}]"
        
        # Check builtin mapping
        if ape_type in self.TYPE_MAPPING:
            return self.TYPE_MAPPING[ape_type]
        
        # Assume it's a user-defined type (entity or enum)
        # Use string quotes to allow forward references
        return f'"{ape_type}"'
    
    def resolve_qualified_name(self, qualified_name: str) -> str:
        """
        Resolve a qualified identifier to its mangled form.
        
        Args:
            qualified_name: Qualified identifier like "math.add" or simple name like "calculate"
        
        Returns:
            Mangled name if qualified (e.g., "math__add"), or original name if simple
        
        Examples:
            >>> codegen.resolve_qualified_name("math.add")
            'math__add'
            >>> codegen.resolve_qualified_name("calculate")
            'calculate'
        """
        if '.' in qualified_name:
            parts = qualified_name.split('.')
            if len(parts) == 2:
                module_name, symbol_name = parts
                return mangle_name(module_name, symbol_name)
            elif len(parts) > 2:
                # Handle deeply nested like "strings.utils.upper" -> "strings.utils__upper"
                module_path = '.'.join(parts[:-1])
                symbol_name = parts[-1]
                return mangle_name(module_path, symbol_name)
        
        # Simple identifier, return as-is
        return qualified_name
