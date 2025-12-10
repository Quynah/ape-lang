"""
APE List Type - List<T>

Immutable, ordered collections (following Ape's deterministic principles).

Author: David Van Aelst
Status: v1.x production
"""

from typing import TypeVar, Generic, List as PyList, Optional, Iterator, Callable, Any

T = TypeVar('T')


class ApeList(Generic[T]):
    """
    Immutable list implementation for APE.
    
    Example:
        my_list: List<Integer> = [1, 2, 3]
        my_list[0]  # Returns 1
        len(my_list)  # Returns 3
    
    Operations:
        - Indexing: list[i] (read-only)
        - Length: len(list)
        - Iteration: for item in list
        - Concatenation: list1 + list2
        - Membership: item in list
        - Equality: list1 == list2 (value-based, order-sensitive)
    
    Note: Lists are IMMUTABLE. Operations return new lists.
    """
    
    def __init__(self, items: Optional[PyList[T]] = None):
        """
        Initialize a list.
        
        Args:
            items: Optional initial items (will be copied for immutability)
        """
        self._items: PyList[T] = list(items) if items is not None else []
    
    def __getitem__(self, index: int) -> T:
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
            raise TypeError(f"List indices must be integers, not {type(index).__name__}")
        
        try:
            return self._items[index]
        except IndexError:
            raise IndexError(f"List index out of range: {index} (size: {len(self._items)})")
    
    def __len__(self) -> int:
        """Return number of items."""
        return len(self._items)
    
    def __iter__(self) -> Iterator[T]:
        """Support iteration over list elements."""
        return iter(self._items)
    
    def __contains__(self, item: T) -> bool:
        """Support membership testing (item in list)."""
        return item in self._items
    
    def __eq__(self, other: Any) -> bool:
        """
        Value-based equality comparison (order-sensitive).
        
        Args:
            other: Object to compare with
            
        Returns:
            True if other is ApeList with same values in same order
        """
        if not isinstance(other, ApeList):
            return False
        return self._items == other._items
    
    def __add__(self, other: 'ApeList[T]') -> 'ApeList[T]':
        """
        Concatenate two lists (returns new list).
        
        Args:
            other: List to concatenate
            
        Returns:
            New list with combined elements
            
        Raises:
            TypeError: If other is not an ApeList
        """
        if not isinstance(other, ApeList):
            raise TypeError(f"Cannot concatenate ApeList with {type(other).__name__}")
        
        return ApeList(self._items + other._items)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ApeList({self._items})"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return str(self._items)
    
    def to_python(self) -> PyList[T]:
        """Convert to Python list (creates a copy)."""
        return list(self._items)


# ============================================================================
# List Operations (Pure Functions)
# ============================================================================

def list_map(lst: ApeList[T], fn: Callable[[T], Any]) -> ApeList:
    """
    Map function over list elements (returns new list).
    
    Args:
        lst: Input list
        fn: Function to apply to each element
        
    Returns:
        New list with transformed elements
    """
    return ApeList([fn(item) for item in lst])


def list_filter(lst: ApeList[T], predicate: Callable[[T], bool]) -> ApeList[T]:
    """
    Filter list by predicate (returns new list).
    
    Args:
        lst: Input list
        predicate: Function that returns True for items to keep
        
    Returns:
        New list with filtered elements
    """
    return ApeList([item for item in lst if predicate(item)])


def list_reduce(lst: ApeList[T], initial: Any, fn: Callable[[Any, T], Any]) -> Any:
    """
    Reduce list to single value.
    
    Args:
        lst: Input list
        initial: Initial accumulator value
        fn: Function(accumulator, item) -> new_accumulator
        
    Returns:
        Final accumulated value
    """
    result = initial
    for item in lst:
        result = fn(result, item)
    return result


def list_concat(lists: PyList[ApeList[T]]) -> ApeList[T]:
    """
    Concatenate multiple lists.
    
    Args:
        lists: Python list of ApeLists
        
    Returns:
        New list with all elements
    """
    result = []
    for lst in lists:
        result.extend(lst._items)
    return ApeList(result)