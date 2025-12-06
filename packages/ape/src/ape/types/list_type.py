"""
APE List Type - List<T>

Ordered, mutable collections with type constraints.

Author: David Van Aelst
Status: v1.0.0 scaffold - implementation pending
"""

from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')


class ApeList(Generic[T]):
    """
    Type-safe list implementation for APE.
    
    Example:
        my_list: List<Integer> = [1, 2, 3]
        my_list.append(4)
        my_list[0]  # Returns 1
    
    Operations:
        - Indexing: list[i]
        - Slicing: list[start:end]
        - Append: list.append(item)
        - Length: list.length()
        - Iteration: for item in list
    
    TODO:
        - Implement __init__ with type parameter
        - Implement index access with bounds checking
        - Implement slice operations
        - Implement append, insert, remove
        - Implement iteration protocol
        - Implement type validation on all operations
    """
    
    def __init__(self, item_type: type, items: Optional[List[T]] = None):
        """
        Initialize a typed list.
        
        Args:
            item_type: The type of items this list can contain
            items: Optional initial items (must all match item_type)
        """
        self._item_type = item_type
        self._items: List[T] = items if items is not None else []
        # TODO: Validate all items match item_type
    
    def __getitem__(self, index: int) -> T:
        """TODO: Implement with bounds checking"""
        raise NotImplementedError("List indexing not yet implemented")
    
    def __setitem__(self, index: int, value: T) -> None:
        """TODO: Implement with type checking"""
        raise NotImplementedError("List item assignment not yet implemented")
    
    def append(self, item: T) -> None:
        """TODO: Implement with type checking"""
        raise NotImplementedError("List.append() not yet implemented")
    
    def length(self) -> int:
        """TODO: Return number of items"""
        raise NotImplementedError("List.length() not yet implemented")
    
    def __repr__(self) -> str:
        return f"ApeList<{self._item_type.__name__}>({self._items})"
