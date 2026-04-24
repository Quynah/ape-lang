"""
Ape Package

Main package for the Ape compiler.
"""

from pathlib import Path
from typing import Union, Any
import tempfile
from types import SimpleNamespace

from ape.runtime.core import ApeModule
from ape.runtime.context import ExecutionContext, ExecutionError, MaxIterationsExceeded
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.trace import TraceCollector, TraceEvent
from ape.runtime.explain import ExplanationStep, ExplanationEngine
from ape.runtime.replay import ReplayEngine
from ape.runtime.profile import (
    RUNTIME_PROFILES,
    get_profile,
    list_profiles,
    create_context_from_profile,
    create_executor_config_from_profile,
)
# Import all errors from unified hierarchy
from ape.errors import (
    ApeError,
    CapabilityError,
    ReplayError,
    ProfileError,
    RuntimeExecutionError,
    ParseError,
    ValidationError,
    LinkerError,
)
from ape.cli import build_project
from ape.codegen.python_codegen import PythonCodeGenerator
from ape.codegen.python_codegen import mangle_name

__version__ = "1.0.7"


class ApeCompileError(Exception):
    """Raised when Ape source code fails to compile."""
    pass


class ApeValidationError(Exception):
    """Raised when Ape code fails semantic or strictness validation."""
    pass


class ApeExecutionError(Exception):
    """Raised when Ape code execution fails at runtime."""
    pass


def _map_ape_type_to_python(type_name: str) -> Any:
    """Map APE type names to Python runtime types for function annotations."""
    type_map = {
        "String": str,
        "Integer": int,
        "Float": float,
        "Decimal": float,
        "Boolean": bool,
        "Any": Any,
    }
    return type_map.get(type_name, Any)


def _build_task_doc(task: Any) -> str:
    """Create deterministic task docstring for generated callables."""
    lines = [f"Safely loaded callable for APE task '{task.name}'."]
    if getattr(task, "steps", None):
        lines.append("")
        lines.append("Steps:")
        for step in task.steps:
            if hasattr(step, "action") and step.action:
                lines.append(f"    - {step.action}")
    return "\n".join(lines)


def _build_safe_task_callable(public_name: str, task_node: Any) -> Any:
    """Build a deterministic callable that executes a parsed APE task node."""
    input_specs = []
    for input_field in getattr(task_node, "inputs", []):
        annotation = Any
        if getattr(input_field, "type_annotation", None) is not None:
            type_name = getattr(input_field.type_annotation, "type_name", None)
            if type_name:
                annotation = _map_ape_type_to_python(type_name)
        input_specs.append((input_field.name, annotation))

    output_fields = getattr(task_node, "outputs", [])
    if len(output_fields) == 0:
        return_annotation = type(None)
    elif len(output_fields) == 1:
        output_type = getattr(output_fields[0], "type_annotation", None)
        return_annotation = _map_ape_type_to_python(output_type.type_name) if output_type else Any
    else:
        return_annotation = tuple

    required_names = [name for name, _ in input_specs]

    def _task_callable(**kwargs: Any) -> Any:
        provided = set(kwargs.keys())
        required = set(required_names)

        missing = sorted(required - provided)
        if missing:
            raise TypeError(f"Missing required arguments: {missing}")

        extra = sorted(provided - required)
        if extra:
            raise TypeError(f"Unknown arguments: {extra}")

        context = ExecutionContext()
        for name in required_names:
            context.set(name, kwargs[name])

        executor = RuntimeExecutor()
        return executor.execute_task(task_node, context)

    annotations = {name: annotation for name, annotation in input_specs}
    annotations["return"] = return_annotation
    _task_callable.__annotations__ = annotations
    _task_callable.__name__ = public_name
    _task_callable.__qualname__ = public_name
    _task_callable.__doc__ = _build_task_doc(task_node)

    return _task_callable


def _build_safe_compiled_module(parsed_ast: Any, module_name: str) -> Any:
    """Construct a module-like object from parsed AST without dynamic code execution."""
    if not hasattr(parsed_ast, "tasks"):
        raise TypeError("Parsed AST is malformed: missing 'tasks'")

    tasks = getattr(parsed_ast, "tasks")
    if not isinstance(tasks, list):
        raise TypeError("Parsed AST is malformed: 'tasks' must be a list")

    safe_module = SimpleNamespace()
    safe_module._ape_ast = parsed_ast
    safe_module._task_cache = {}

    module_decl_name = parsed_ast.name if getattr(parsed_ast, "name", "") else None

    for task in tasks:
        if not hasattr(task, "name") or not isinstance(task.name, str) or not task.name:
            raise TypeError("Parsed AST task is malformed: missing non-empty string 'name'")
        mangled_name = mangle_name(module_decl_name, task.name)
        safe_module._task_cache[mangled_name] = task
        setattr(safe_module, mangled_name, _build_safe_task_callable(mangled_name, task))

    return safe_module


def compile(source_or_path: Union[str, Path]) -> ApeModule:
    """
    Compile Ape source code or file to an executable module.

    This is the main entry point for programmatic compilation of Ape code.
    It handles:
    1. Parsing the Ape source
    2. Building IR
    3. Generating Python code
    4. Loading the generated code as a Python module

    Args:
        source_or_path: Either:
            - Path to a .ape file (str or Path)
            - Raw Ape source code as string (detected if no file exists)

    Returns:
        ApeModule: A compiled module that can be executed

    Raises:
        ApeCompileError: If compilation fails

    Example:
        >>> module = compile("examples/calculator.ape")
        >>> result = module.call("add", a=5, b=3)
        >>> print(result)
        8
    """
    temp_source_path: Path | None = None

    try:
        # Determine if it's a file path or source code
        path_obj = Path(source_or_path) if isinstance(source_or_path, (str, Path)) else None

        if path_obj and path_obj.is_file():
            # it's a file path
            source_path = path_obj
        else:
            # Assume it's source code - write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ape', delete=False, encoding='utf-8') as f:
                f.write(str(source_or_path))
                source_path = Path(f.name)
                temp_source_path = source_path

        # Build project IR (includes linking)
        project = build_project(source_path)

        # Also parse to get AST for runtime execution
        from ape.tokenizer.tokenizer import Tokenizer
        from ape.parser.parser import Parser
        with open(source_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tokenizer = Tokenizer(source_code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Generate Python code
        generator = PythonCodeGenerator(project)
        files = generator.generate()

        if not files:
            raise ApeCompileError("Code generation produced no files")

        # For now, use the first generated file
        # In future, may need to handle multi-module projects
        generated = files[0]

        # Resolve module name from generated artifact path.
        module_name = Path(generated.path).stem

        # Build a structured module without executing generated Python source.
        python_module = _build_safe_compiled_module(ast, module_name)

        # Wrap in ApeModule for stable API
        ape_module = ApeModule(module_name, python_module)

        return ape_module

    except ApeCompileError:
        raise
    except Exception as e:
        raise ApeCompileError(f"Compilation failed: {e}") from e
    finally:
        # Clean up temporary source file if we created one
        if temp_source_path is not None:
            try:
                temp_source_path.unlink()
            except FileNotFoundError:
                pass
def validate(module: ApeModule) -> None:
    """
    Validate an Ape module for semantic correctness and strictness.

    Note: In the current implementation, validation happens during compile().
    This function is provided for API completeness and may be extended
    to support runtime validation in future versions.

    Args:
        module: The ApeModule to validate

    Raises:
        ApeValidationError: If validation fails

    Example:
        >>> module = compile("examples/calculator.ape")
        >>> validate(module)  # Raises if invalid
    """
    # Current implementation: validation happens in compile()
    # This is a no-op for API compatibility
    # Future: may add runtime constraint validation
    pass


def run(source: str, *, context: dict | None = None, language: str = "en") -> Any:
    """
    Execute Ape source code using AST-based runtime.

    This is a convenience function that:
    1. Normalizes language-specific syntax to canonical APE (if needed)
    2. Tokenizes and parses the source into an AST
    3. Creates an ExecutionContext (optionally with initial variables)
    4. Executes the AST using RuntimeExecutor

    This provides a quick way to run Ape code without going through
    the full compilation pipeline. Useful for experiments and testing.

    Args:
        source: Ape source code as a string
        context: Optional dictionary of initial variables
        language: ISO 639-1 language code (default: 'en')
                  Supported: en, nl, fr, de, es, it, pt

    Returns:
        The result of executing the program

    Raises:
        ExecutionError: If runtime execution fails
        ValidationError: If language code is unsupported

    Example:
        >>> result = run('''
        ... task main:
        ...     inputs:
        ...         x: Integer
        ...     outputs:
        ...         result: Integer
        ...     steps:
        ...         if x > 0:
        ...             - set result to x * 2
        ...         else:
        ...             - set result to 0
        ...         - return result
        ... ''', context={'x': 5})
        >>> print(result)
        10

        >>> # Dutch syntax
        >>> result = run('''
        ... task main:
        ...     steps:
        ...         als x > 0:
        ...             - set result to x * 2
        ... ''', context={'x': 5}, language='nl')
    """
    from ape.tokenizer.tokenizer import Tokenizer
    from ape.parser.parser import Parser
    from ape.lang import get_adapter

    # Normalize language-specific syntax to canonical APE
    adapter = get_adapter(language)
    normalized_source = adapter.normalize_source(source)

    # Tokenize
    tokenizer = Tokenizer(normalized_source)
    tokens = tokenizer.tokenize()

    # Parse
    parser = Parser(tokens)
    ast = parser.parse()

    # Create execution context
    exec_context = ExecutionContext()
    if context:
        for key, value in context.items():
            exec_context.set(key, value)

    # Execute
    executor = RuntimeExecutor()
    return executor.execute(ast, exec_context)


__all__ = [
    # ===== PUBLIC API (v1.0 Stable) =====
    # High-level functions
    "compile",
    "validate",
    "run",

    # Core runtime
    "ApeModule",
    "ExecutionContext",
    "RuntimeExecutor",

    # Tracing & observability
    "TraceCollector",
    "TraceEvent",

    # Explanation & replay
    "ExplanationStep",
    "ExplanationEngine",
    "ReplayEngine",

    # Runtime profiles
    "RUNTIME_PROFILES",
    "get_profile",
    "list_profiles",
    "create_context_from_profile",
    "create_executor_config_from_profile",

    # Errors (v1.0 unified hierarchy)
    "ApeError",
    "ApeCompileError",
    "ApeValidationError",
    "ApeExecutionError",
    "ExecutionError",
    "MaxIterationsExceeded",
    "CapabilityError",
    "ReplayError",
    "ProfileError",
    "RuntimeExecutionError",
    "ParseError",
    "ValidationError",
    "LinkerError",
]

