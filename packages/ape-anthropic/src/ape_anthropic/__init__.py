"""
ape-anthropic: Anthropic Claude integration for APE.

Provides schema conversion, execution, and code generation
for Claude tool use with APE validation.
"""

from typing import Dict, Optional, Any

# Try to import ape-lang (required dependency)
try:
    from ape import compile, validate, ApeModule
    from ape import ApeCompileError, ApeValidationError, ApeExecutionError
    from ape.runtime.core import FunctionSignature
    APE_AVAILABLE = True
except ImportError:
    APE_AVAILABLE = False
    compile = None  # type: ignore
    validate = None  # type: ignore
    ApeModule = None  # type: ignore
    ApeCompileError = Exception  # type: ignore
    ApeValidationError = Exception  # type: ignore
    ApeExecutionError = Exception  # type: ignore
    FunctionSignature = None  # type: ignore


# Public API
from ape_anthropic.schema import ape_task_to_claude_schema
from ape_anthropic.executor import execute_claude_call, ApeAnthropicFunction
from ape_anthropic.generator import generate_ape_from_nl


class ApeTask:
    """
    Represents an Ape task for Claude integration.
    
    Wrapper around APE's FunctionSignature with a simpler interface.
    """
    
    def __init__(
        self,
        name: str,
        inputs: Dict[str, str],
        output: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.name = name
        self.inputs = inputs
        self.output = output
        self.description = description
    
    @classmethod
    def from_signature(cls, sig: Any) -> "ApeTask":
        """Create ApeTask from APE FunctionSignature."""
        return cls(
            name=sig.name,
            inputs=sig.inputs,
            output=sig.output,
            description=getattr(sig, 'description', None)
        )


__version__ = "0.1.1"

__all__ = [
    "ape_task_to_claude_schema",
    "execute_claude_call",
    "ApeAnthropicFunction",
    "generate_ape_from_nl",
    "ApeTask",
    "compile",
    "validate",
    "ApeModule",
    "ApeCompileError",
    "ApeValidationError",
    "ApeExecutionError",
]
