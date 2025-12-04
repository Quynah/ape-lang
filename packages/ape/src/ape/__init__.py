"""
Ape Package

Main package for the Ape compiler.
"""

from pathlib import Path
from typing import Union
import tempfile
import importlib.util
import sys

from ape.runtime.core import ApeModule
from ape.cli import build_project
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.strictness_engine import StrictnessEngine
from ape.codegen.python_codegen import PythonCodeGenerator

__version__ = "0.2.1"


class ApeCompileError(Exception):
    """Raised when Ape source code fails to compile."""
    pass


class ApeValidationError(Exception):
    """Raised when Ape code fails semantic or strictness validation."""
    pass


class ApeExecutionError(Exception):
    """Raised when Ape code execution fails at runtime."""
    pass


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

        # Generate Python code
        generator = PythonCodeGenerator(project)
        files = generator.generate()

        if not files:
            raise ApeCompileError("Code generation produced no files")

        # For now, use the first generated file
        # In future, may need to handle multi-module projects
        generated = files[0]

        # Load the generated Python code as a module
        module_name = Path(generated.path).stem
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        if spec is None:
            raise ApeCompileError(f"Failed to create module spec for {module_name}")

        python_module = importlib.util.module_from_spec(spec)

        # Execute the generated code in the module's namespace
        exec(generated.content, python_module.__dict__)

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


__all__ = [
    "compile",
    "validate", 
    "ApeModule",
    "ApeCompileError",
    "ApeValidationError",
    "ApeExecutionError",
]
