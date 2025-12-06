"""
APE Tuple Type

Fixed-size heterogeneous collections.

Author: David Van Aelst
Status: v1.0.0 scaffold - implementation pending
"""

from typing import Tuple as PyTuple, Any


class ApeTuple:
    """
    Immutable, fixed-size tuple with type constraints.
    
    Example:
        point: Tuple<Integer, Integer> = (10, 20)
        point[0]  # Returns 10
        
        result: Tuple<String, Boolean, Integer> = ("success", true, 42)
    
    TODO:
        - Implement __init__ with type parameters
        - Implement index access (read-only)
        - Implement unpacking support
        - Implement iteration protocol
        - Implement type validation
    """
    
    def __init__(self, types: PyTuple[type, ...], values: PyTuple[Any, ...]):
        """
        Initialize a typed tuple.
        
        Args:
            types: Tuple of types for each position
            values: Tuple of values (must match types)
        """
        self._types = types
        self._values = values
        # TODO: Validate values match types
    
    def __getitem__(self, index: int) -> Any:
        """TODO: Implement with bounds checking"""
        raise NotImplementedError("Tuple indexing not yet implemented")
    
    def __len__(self) -> int:
        """TODO: Return tuple size"""
        raise NotImplementedError("Tuple length not yet implemented")
    
    def __repr__(self) -> str:
        types_str = ", ".join(t.__name__ for t in self._types)
        return f"ApeTuple<{types_str}>({self._values})"
