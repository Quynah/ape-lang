"""
Execution layer: Claude tool use → Ape runtime.

Handles execution of Claude tool calls with APE validation.
"""

from typing import Any, Optional, Dict
from pathlib import Path

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


def execute_claude_call(
    module: Any,
    function_name: str,
    input_dict: Dict[str, Any]
) -> Any:
    """
    Execute a Claude tool use with Ape validation.

    Takes the input dictionary from Claude's tool use response,
    validates it against the Ape task signature, and executes it
    deterministically.

    Args:
        module: Compiled ApeModule
        function_name: Name of the function to call
        input_dict: Dictionary of arguments from Claude

    Returns:
        Function execution result (JSON-serializable)

    Raises:
        TypeError: If arguments don't match task signature
        ApeExecutionError: If execution fails
    """
    if not APE_AVAILABLE:
        raise ImportError("ape-anthropic requires ape-lang to be installed")

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


class ApeAnthropicFunction:
    """
    High-level wrapper for Ape function → Claude tool integration.

    Provides a simple interface for:
    - Loading Ape functions from files
    - Converting to Claude tool schemas
    - Executing Claude tool use with validation

    Example:
        >>> func = ApeAnthropicFunction.from_ape_file("calculator.ape", "add")
        >>> 
        >>> # Get Claude tool definition
        >>> tool = func.to_claude_tool()
        >>> 
        >>> # Execute tool use
        >>> result = func.execute({"a": 5, "b": 3})
    """

    def __init__(
        self,
        module: Any,
        function_name: str,
        description: Optional[str] = None
    ):
        """
        Initialize ApeAnthropicFunction.

        Args:
            module: Compiled ApeModule
            function_name: Name of the function to wrap
            description: Optional custom description
        """
        if not APE_AVAILABLE:
            raise ImportError("ape-anthropic requires ape-lang to be installed")

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
    ) -> "ApeAnthropicFunction":
        """
        Create ApeAnthropicFunction from an Ape source file.

        Args:
            ape_file: Path to .ape source file
            function_name: Name of the function to wrap
            description: Optional custom description

        Returns:
            ApeAnthropicFunction instance
        """
        module = ape_compile(ape_file)
        ape_validate(module)
        return cls(module, function_name, description)

    def to_claude_tool(self) -> dict:
        """
        Generate Claude tool definition.

        Returns:
            Claude tool schema dictionary
        """
        from ape_anthropic.schema import ape_task_to_claude_schema
        from ape_anthropic import ApeTask

        # Create ApeTask from signature
        task = ApeTask(
            name=self.signature.name,
            inputs=self.signature.inputs,
            output=self.signature.output,
            description=self.description or self.signature.description
        )

        return ape_task_to_claude_schema(task)

    def execute(self, input_dict: Dict[str, Any]) -> Any:
        """
        Execute Claude tool use.

        Args:
            input_dict: Dictionary of arguments from Claude

        Returns:
            Function execution result
        """
        return execute_claude_call(
            self.module,
            self.function_name,
            input_dict
        )

    def __repr__(self) -> str:
        return f"ApeAnthropicFunction(function='{self.function_name}')"


__all__ = [
    "execute_claude_call",
    "ApeAnthropicFunction",
]
