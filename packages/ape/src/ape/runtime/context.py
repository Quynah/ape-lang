"""
Ape Runtime Context

Execution context for AST-based runtime without Python exec().
Maintains variable bindings and scope in a deterministic, sandbox-safe manner.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Set

# Import errors from unified hierarchy (backwards compatibility maintained)
from ape.errors import ExecutionError, MaxIterationsExceeded


@dataclass
class ExecutionContext:
    """
    Execution context for Ape runtime.
    
    Manages variable bindings and scope without any I/O or side effects.
    Design for sandbox safety: no filesystem, network, or environment access.
    
    Attributes:
        variables: Current scope variable bindings
        parent: Parent scope (for nested scopes)
        max_iterations: Safety limit for loops (default 10,000)
        dry_run: If True, mutations are blocked (dry-run mode)
        capabilities: Set of allowed capabilities for gated operations
    """
    variables: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['ExecutionContext'] = None
    max_iterations: int = 10_000
    dry_run: bool = False
    capabilities: Set[str] = field(default_factory=set)
    
    def get(self, name: str) -> Any:
        """
        Get variable value from current or parent scope.
        
        Args:
            name: Variable name
            
        Returns:
            Variable value
            
        Raises:
            NameError: If variable not found in any scope
        """
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not defined")
    
    def set(self, name: str, value: Any) -> None:
        """
        Set variable value in current scope.
        
        In dry-run mode, this operation is blocked.
        
        Args:
            name: Variable name
            value: Variable value
            
        Raises:
            RuntimeError: If in dry-run mode
        """
        if self.dry_run:
            # In dry-run mode, mutations are blocked
            # Caller should log this as "would_write" in trace
            raise RuntimeError(f"Cannot mutate variable '{name}' in dry-run mode")
        self.variables[name] = value
    
    def has(self, name: str) -> bool:
        """
        Check if variable exists in current or parent scope.
        
        Args:
            name: Variable name
            
        Returns:
            True if variable exists, False otherwise
        """
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.has(name)
        return False
    
    def create_child_scope(self) -> 'ExecutionContext':
        """
        Create a child scope (for loops, if blocks, etc.).
        
        Child inherits dry_run and capabilities from parent.
        
        Returns:
            New ExecutionContext with this context as parent
        """
        return ExecutionContext(
            parent=self,
            max_iterations=self.max_iterations,
            dry_run=self.dry_run,
            capabilities=self.capabilities.copy()
        )
    
    def can_mutate(self) -> bool:
        """
        Check if mutations are allowed.
        
        Returns:
            True if mutations allowed, False in dry-run mode
        """
        return not self.dry_run
    
    def allow(self, capability: str) -> None:
        """
        Grant a capability to this context.
        
        Capabilities gate access to side effects and external resources.
        
        Args:
            capability: Name of capability to grant
        """
        self.capabilities.add(capability)
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if a capability is granted.
        
        Args:
            capability: Name of capability to check
            
        Returns:
            True if capability is granted, False otherwise
        """
        return capability in self.capabilities
    
    def get_all_variables(self) -> Dict[str, Any]:
        """
        Get all variables from current scope and parent scopes.
        
        Returns:
            Dictionary of all accessible variables
        """
        if self.parent:
            result = self.parent.get_all_variables().copy()
            result.update(self.variables)
            return result
        return self.variables.copy()



__all__ = ['ExecutionContext', 'ExecutionError', 'MaxIterationsExceeded']
