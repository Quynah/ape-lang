"""
Execution layer: OpenAI function calls → Ape runtime.

Handles execution of OpenAI function calls with APE validation.
"""

from typing import Any, Optional, Dict
from pathlib import Path
import json

# Import APE if available
try:
    from ape import compile as ape_compile, validate as ape_validate
    from ape import ApeModule, ApeExecutionError
    APE_AVAILABLE = True
except ImportError:
    APE_AVAILABLE = False
    ape_compile = None  # type: ignore
    ape_validate = None  # type: ignore
    ApeModule = None  # type: ignore
    ApeExecutionError = Exception  # type: ignore


def execute_openai_call(
    module: Any,
    function_name: str,
    arguments: str | Dict[str, Any]
) -> Any:
    """
    Execute an OpenAI function call with Ape validation.

    Takes the arguments from OpenAI's function call response,
    validates them against the Ape task signature, and executes
    deterministically.

    Args:
        module: Compiled ApeModule
        function_name: Name of the function to call
        arguments: JSON string or dict of arguments from OpenAI

    Returns:
        Function execution result (JSON-serializable)

    Raises:
        TypeError: If arguments don't match task signature
        ApeExecutionError: If execution fails
    """
    if not APE_AVAILABLE:
        raise ImportError("ape-openai requires ape-lang to be installed")

    # Parse arguments if string
    if isinstance(arguments, str):
        try:
            input_dict = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}") from e
    else:
        input_dict = arguments

    # Validate arguments match task signature
    try:
        signature = module.get_function_signature(function_name)
    except KeyError as e:
        available = ", ".join(module.list_functions())
        raise KeyError(
            f"Function '{function_name}' not found in module. "
            f"Available: {available}"
        ) from e

    # Check required parameters
    provided = set(input_dict.keys())
    required = set(signature.inputs.keys())
    
    missing = required - provided
    if missing:
        raise TypeError(f"Missing required arguments: {missing}")
    
    extra = provided - required
    if extra:
        raise TypeError(f"Unknown arguments: {extra}")

    # Execute via APE runtime
    try:
        result = module.call(function_name, **input_dict)
        return result
    except Exception as e:
        raise ApeExecutionError(
            f"Execution of '{function_name}' failed: {e}"
        ) from e


class ApeOpenAIFunction:
    """
    High-level wrapper for Ape function → OpenAI function integration.

    Provides a simple interface for:
    - Loading Ape functions from files
    - Converting to OpenAI function schemas
    - Executing OpenAI function calls with validation

    Example:
        >>> func = ApeOpenAIFunction.from_ape_file("calculator.ape", "add")
        >>> 
        >>> # Get OpenAI function definition
        >>> tool = func.to_openai_function()
        >>> 
        >>> # Execute function call
        >>> result = func.execute('{"a": 5, "b": 3}')
    """

    def __init__(
        self,
        module: Any,
        function_name: str,
        description: Optional[str] = None
    ):
        """
        Initialize ApeOpenAIFunction.

        Args:
            module: Compiled ApeModule
            function_name: Name of the function to wrap
            description: Optional custom description
        """
        if not APE_AVAILABLE:
            raise ImportError("ape-openai requires ape-lang to be installed")

        self.module = module
        self.function_name = function_name
        self.description = description

        # Validate function exists
        try:
            self.signature = module.get_function_signature(function_name)
        except KeyError as e:
            available = ", ".join(module.list_functions())
            raise KeyError(
                f"Function '{function_name}' not found. Available: {available}"
            ) from e

    @classmethod
    def from_ape_file(
        cls,
        ape_file: str | Path,
        function_name: str,
        description: Optional[str] = None
    ) -> "ApeOpenAIFunction":
        """
        Create ApeOpenAIFunction from an Ape source file.

        Args:
            ape_file: Path to .ape source file
            function_name: Name of the function to wrap
            description: Optional custom description

        Returns:
            ApeOpenAIFunction instance
        """
        module = ape_compile(ape_file)
        ape_validate(module)
        return cls(module, function_name, description)

    def to_openai_function(self) -> dict:
        """
        Generate OpenAI function definition.

        Returns:
            OpenAI function schema dictionary
        """
        from ape_openai.schema import ape_task_to_openai_schema
        from ape_openai import ApeTask

        # Create ApeTask from signature
        task = ApeTask(
            name=self.signature.name,
            inputs=self.signature.inputs,
            output=self.signature.output,
            description=self.description or self.signature.description
        )

        return ape_task_to_openai_schema(task)

    def execute(self, arguments: str | Dict[str, Any]) -> Any:
        """
        Execute OpenAI function call.

        Args:
            arguments: JSON string or dict of arguments from OpenAI

        Returns:
            Function execution result
        """
        return execute_openai_call(
            self.module,
            self.function_name,
            arguments
        )

    def __repr__(self) -> str:
        return f"ApeOpenAIFunction(function='{self.function_name}')"


__all__ = [
    "execute_openai_call",
    "ApeOpenAIFunction",
]
