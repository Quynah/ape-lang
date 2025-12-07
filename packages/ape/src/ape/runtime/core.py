"""
Ape Runtime Core

Minimal runtime support for Ape flows and tasks.
This will be extended with logging, determinism tracking, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class RunContext:
    """
    Runtime context for Ape flows.
    
    Provides execution context and metadata for flow orchestration.
    Future extensions may include:
    - Logging and tracing
    - Determinism enforcement
    - Resource management
    - Error handling
    """
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FunctionSignature:
    """
    Metadata about an Ape function signature.
    
    Used by integration layers (e.g., ape-langchain) to introspect
    and validate function calls.
    """
    name: str
    inputs: Dict[str, str]  # param_name -> type_name
    output: Optional[str] = None  # output type name
    description: Optional[str] = None


class ApeModule:
    """
    Runtime representation of a compiled Ape module.
    
    This class provides a stable API for executing Ape code from Python,
    particularly for integration layers like ape-langchain.
    
    Attributes:
        module_name: The original Ape module name
        generated_module: The generated Python module object
        functions: Available function signatures in this module
    """
    
    def __init__(self, module_name: str, generated_module: Any):
        """
        Initialize an ApeModule.
        
        Args:
            module_name: Name of the Ape module
            generated_module: The compiled Python module object
        """
        self.module_name = module_name
        self.generated_module = generated_module
        self._functions: Dict[str, FunctionSignature] = {}
        self._discover_functions()
    
    def _discover_functions(self) -> None:
        """
        Discover callable functions in the generated module.
        
        Looks for functions that don't start with underscore and
        extracts their signatures.
        """
        for name in dir(self.generated_module):
            if name.startswith('_'):
                continue
            
            attr = getattr(self.generated_module, name)
            if callable(attr):
                # Extract signature from function annotations if available
                inputs = {}
                output = None
                
                if hasattr(attr, '__annotations__'):
                    annotations = attr.__annotations__
                    output = annotations.get('return')
                    inputs = {k: v for k, v in annotations.items() if k != 'return'}
                
                # Convert type objects to strings
                inputs_str = {k: (v.__name__ if hasattr(v, '__name__') else str(v)) 
                             for k, v in inputs.items()}
                output_str = output.__name__ if hasattr(output, '__name__') else (str(output) if output else None)
                
                self._functions[name] = FunctionSignature(
                    name=name,
                    inputs=inputs_str,
                    output=output_str,
                    description=attr.__doc__
                )
    
    def call(self, function_name: str, **kwargs) -> Any:
        """
        Execute a function from this compiled module.
        
        Args:
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            The function's return value
            
        Raises:
            AttributeError: If function doesn't exist
            TypeError: If arguments are invalid
        """
        if not hasattr(self.generated_module, function_name):
            available = ', '.join(self.list_functions())
            raise AttributeError(
                f"Function '{function_name}' not found in module '{self.module_name}'. "
                f"Available functions: {available}"
            )
        
        func = getattr(self.generated_module, function_name)
        return func(**kwargs)
    
    def list_functions(self) -> List[str]:
        """
        List all callable functions in this module.
        
        Returns:
            List of function names
        """
        return list(self._functions.keys())
    
    def get_function_signature(self, function_name: str) -> FunctionSignature:
        """
        Get metadata for a specific function.
        
        Args:
            function_name: Name of the function
            
        Returns:
            FunctionSignature with input/output metadata
            
        Raises:
            KeyError: If function doesn't exist
        """
        if function_name not in self._functions:
            available = ', '.join(self.list_functions())
            raise KeyError(
                f"Function '{function_name}' not found. "
                f"Available functions: {available}"
            )
        
        return self._functions[function_name]
    
    def __repr__(self) -> str:
        funcs = ', '.join(self.list_functions())
        return f"ApeModule('{self.module_name}', functions=[{funcs}])"
