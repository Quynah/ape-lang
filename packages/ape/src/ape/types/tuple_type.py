"""
APE Tuple Type

Fixed-size heterogeneous collections (immutable).

Author: David Van Aelst
Status: v1.x production
"""

from typing import Tuple as PyTuple, Any, Iterator


class ApeTuple:
    """
    Immutable, fixed-size tuple with optional type constraints.
    
    Example:
        point: Tuple<Integer, Integer> = (10, 20)
        point[0]  # Returns 10
        
        result: Tuple<String, Boolean, Integer> = ("success", true, 42)
    
    Features:
        - Immutable (no modification after creation)
        - Fixed size (arity)
        - Heterogeneous (different types per position)
        - Index access (read-only)
        - Iteration support
        - Value-based equality
    """
    
    def __init__(self, values: PyTuple[Any, ...]):
        """
        Initialize a tuple.
        
        Args:
            values: Tuple of values
        """
        if not isinstance(values, tuple):
            values = tuple(values)
        self._values = values
    
    def __getitem__(self, index: int) -> Any:
        """
        Get item at index (read-only).
        
        Args:
            index: Zero-based index
            
        Returns:
            Value at index
            
        Raises:
            IndexError: If index out of bounds
            TypeError: If index is not an integer
        """
        if not isinstance(index, int):
            raise TypeError(f"Tuple indices must be integers, not {type(index).__name__}")
        
        try:
            return self._values[index]
        except IndexError:
            raise IndexError(f"Tuple index out of range: {index} (size: {len(self._values)})")
    
    def __len__(self) -> int:
        """Return tuple size."""
        return len(self._values)
    
    def __iter__(self) -> Iterator[Any]:
        """Support iteration over tuple elements."""
        return iter(self._values)
    
    def __eq__(self, other: Any) -> bool:
        """
        Value-based equality comparison.
        
        Args:
            other: Object to compare with
            
        Returns:
            True if other is ApeTuple with same values in same order
        """
        if not isinstance(other, ApeTuple):
            return False
        return self._values == other._values
    
    def __hash__(self) -> int:
        """Make tuples hashable (immutable)."""
        return hash(self._values)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ApeTuple({self._values})"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return str(self._values)
    
    def to_python(self) -> PyTuple[Any, ...]:
        """Convert to Python tuple."""
        return self._values
