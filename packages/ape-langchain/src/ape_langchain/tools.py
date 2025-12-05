"""
LangChain tool wrappers for Ape functions.

Provides StructuredTool integration for Ape tasks.
"""

from typing import Any, Optional, Dict, Callable
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

# LangChain imports (optional)
try:
    from langchain.tools import StructuredTool
    from langchain_core.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    StructuredTool = None  # type: ignore
    BaseTool = None  # type: ignore


class ApeLangChainTool:
    """
    Wrapper for Ape function as LangChain tool.

    Provides a bridge between Ape's deterministic execution
    and LangChain's tool interface.

    Example:
        >>> tool = ApeLangChainTool.from_ape_file("calc.ape", "add")
        >>> langchain_tool = tool.as_structured_tool()
        >>> result = langchain_tool.run({"a": 5, "b": 3})
    """

    def __init__(
        self,
        module: Any,
        function_name: str,
        description: Optional[str] = None
    ):
        """
        Initialize ApeLangChainTool.

        Args:
            module: Compiled ApeModule
            function_name: Name of the function to wrap
            description: Optional custom description
        """
        if not APE_AVAILABLE:
            raise ImportError("ape-langchain requires ape-lang to be installed")

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
    ) -> "ApeLangChainTool":
        """
        Create ApeLangChainTool from an Ape source file.

        Args:
            ape_file: Path to .ape source file
            function_name: Name of the function to wrap
            description: Optional custom description

        Returns:
            ApeLangChainTool instance
        """
        module = ape_compile(ape_file)
        ape_validate(module)
        return cls(module, function_name, description)

    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the Ape function with validation.

        Args:
            **kwargs: Function arguments

        Returns:
            Function execution result
        """
        # Validate arguments
        provided = set(kwargs.keys())
        required = set(self.signature.inputs.keys())
        
        missing = required - provided
        if missing:
            raise TypeError(f"Missing required arguments: {missing}")
        
        extra = provided - required
        if extra:
            raise TypeError(f"Unknown arguments: {extra}")

        # Execute via APE runtime
        try:
            result = self.module.call(self.function_name, **kwargs)
            return result
        except Exception as e:
            raise ApeExecutionError(
                f"Execution of '{self.function_name}' failed: {e}"
            ) from e

    def as_structured_tool(self) -> Any:
        """
        Convert to LangChain StructuredTool.

        Returns:
            LangChain StructuredTool instance
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain conversion requires langchain package. "
                "Install it with: pip install ape-langchain[langchain]"
            )

        from ape_langchain.schema import create_pydantic_model
        from ape_langchain import ApeTask

        # Create task representation
        task = ApeTask(
            name=self.signature.name,
            inputs=self.signature.inputs,
            output=self.signature.output,
            description=self.description or self.signature.description
        )

        # Create Pydantic model for args
        args_schema = create_pydantic_model(task)

        # Create StructuredTool
        tool = StructuredTool(
            name=task.name,
            description=task.description or f"Deterministic Ape task: {task.name}",
            func=self.execute,
            args_schema=args_schema
        )

        return tool

    def __repr__(self) -> str:
        return f"ApeLangChainTool(function='{self.function_name}')"


def create_langchain_tool(
    ape_file: str | Path,
    function_name: str,
    description: Optional[str] = None
) -> Any:
    """
    Create a LangChain StructuredTool from an Ape file.

    Convenience function that combines loading and conversion.

    Args:
        ape_file: Path to .ape source file
        function_name: Name of the function to wrap
        description: Optional custom description

    Returns:
        LangChain StructuredTool instance

    Example:
        >>> tool = create_langchain_tool("calc.ape", "add")
        >>> result = tool.run({"a": 5, "b": 3})
    """
    ape_tool = ApeLangChainTool.from_ape_file(ape_file, function_name, description)
    return ape_tool.as_structured_tool()


__all__ = [
    "ApeLangChainTool",
    "create_langchain_tool",
]
