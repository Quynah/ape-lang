"""
APE Standard Library - Collections Module

Pure collection manipulation functions.

All collection operations are:
- Deterministic (same input → same output)
- Type-strict (explicit type checking)
- Order-preserving (when applicable)
"""

from typing import Any, List, Callable, Union
from ape.std.errors import CollectionTypeError, EmptyCollectionError, MathTypeError


def count(items: List[Any]) -> int:
    """
    Return the length of a collection.
    
    Args:
        items: Collection to count
        
    Returns:
        Number of items in collection
        
    Raises:
        TypeError: If items is not a list
    """
    if not isinstance(items, list):
        raise TypeError(f"count requires list, got {type(items).__name__}")
    
    return len(items)


def is_empty(items: List[Any]) -> bool:
    """
    Check if a collection is empty.
    
    Args:
        items: Collection to check
        
    Returns:
        True if collection is empty, False otherwise
        
    Raises:
        TypeError: If items is not a list
    """
    if not isinstance(items, list):
        raise TypeError(f"is_empty requires list, got {type(items).__name__}")
    
    return len(items) == 0


def contains(items: List[Any], value: Any) -> bool:
    """
    Check if a value is in a collection.
    
    Args:
        items: Collection to search
        value: Value to find
        
    Returns:
        True if value is in collection, False otherwise
        
    Raises:
        TypeError: If items is not a list
    """
    if not isinstance(items, list):
        raise TypeError(f"contains requires list, got {type(items).__name__}")
    
    return value in items


def filter_items(items: List[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """
    Filter collection using a predicate function.
    
    Args:
        items: Collection to filter
        predicate: Function that returns True for items to keep
        
    Returns:
        New list containing only items where predicate returned True
        
    Raises:
        TypeError: If items is not a list or predicate is not callable
    """
    if not isinstance(items, list):
        raise TypeError(f"filter_items requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"filter_items requires callable predicate, got {type(predicate).__name__}")
    
    return [item for item in items if predicate(item)]


def map_items(items: List[Any], transformer: Callable[[Any], Any]) -> List[Any]:
    """
    Transform collection using a transformer function.
    
    Args:
        items: Collection to transform
        transformer: Function to apply to each item
        
    Returns:
        New list containing transformed items
        
    Raises:
        TypeError: If items is not a list or transformer is not callable
    """
    if not isinstance(items, list):
        raise TypeError(f"map_items requires list, got {type(items).__name__}")
    
    if not callable(transformer):
        raise TypeError(f"map_items requires callable transformer, got {type(transformer).__name__}")
    
    return [transformer(item) for item in items]


# ============================================================================
# Extended Collection Functions (v1.0.0 scaffold)
# ============================================================================

def reduce(items: List[Any], reducer: Callable[[Any, Any], Any], initial: Any = None) -> Any:
    """
    Reduce a collection to a single value using a reducer function.
    
    Example:
        sum = reduce([1, 2, 3, 4], lambda acc, x: acc + x, 0)  # 10
    
    Args:
        items: Collection to reduce
        reducer: Function taking (accumulator, item) and returning new accumulator
        initial: Initial accumulator value
    
    Returns:
        Final accumulated value
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("reduce() not yet implemented")


def reverse(items: List[Any]) -> List[Any]:
    """
    Reverse the order of items in a collection.
    
    Example:
        reversed_list = reverse([1, 2, 3])  # [3, 2, 1]
    
    Args:
        items: Collection to reverse
    
    Returns:
        New list with items in reverse order
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("reverse() not yet implemented")


def sort(items: List[Any], key: Callable[[Any], Any] = None, reverse: bool = False) -> List[Any]:
    """
    Sort a collection.
    
    Example:
        sorted_list = sort([3, 1, 2])  # [1, 2, 3]
        sorted_desc = sort([3, 1, 2], reverse=True)  # [3, 2, 1]
    
    Args:
        items: Collection to sort
        key: Optional function to extract comparison key from each item
        reverse: If True, sort in descending order
    
    Returns:
        New sorted list
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("sort() not yet implemented")


def zip(list1: List[Any], list2: List[Any]) -> List[tuple]:
    """
    Combine two lists into a list of pairs.
    
    Example:
        pairs = zip([1, 2, 3], ["a", "b", "c"])  # [(1, "a"), (2, "b"), (3, "c")]
    
    Args:
        list1: First list
        list2: Second list
    
    Returns:
        List of tuples pairing corresponding elements
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("zip() not yet implemented")


def enumerate_items(items: List[Any], start: int = 0) -> List[tuple]:
    """
    Create index-value pairs for each item.
    
    Example:
        indexed = enumerate_items(["a", "b", "c"])  # [(0, "a"), (1, "b"), (2, "c")]
    
    Args:
        items: Collection to enumerate
        start: Starting index (default 0)
    
    Returns:
        List of (index, item) tuples
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("enumerate_items() not yet implemented")


def range_list(start: int, stop: int = None, step: int = 1) -> List[int]:
    """
    Generate a list of integers in a range.
    
    Example:
        range_list(5)  # [0, 1, 2, 3, 4]
        range_list(2, 8)  # [2, 3, 4, 5, 6, 7]
        range_list(0, 10, 2)  # [0, 2, 4, 6, 8]
    
    Args:
        start: Starting value (or stop if stop is None)
        stop: Ending value (exclusive)
        step: Step size
    
    Returns:
        List of integers
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    raise NotImplementedError("range_list() not yet implemented")


def sum_list(items: List[Union[int, float]]) -> Union[int, float]:
    """
    Sum all numbers in a collection.
    
    Args:
        items: List of numbers to sum
        
    Returns:
        Sum of all items (int if all int, float otherwise)
        
    Raises:
        CollectionTypeError: If items is not a list
        EmptyCollectionError: If list is empty
        MathTypeError: If any item is not a number
        
    Examples:
        sum_list([1, 2, 3]) → 6
        sum_list([1.5, 2.5]) → 4.0
        sum_list([]) → EmptyCollectionError
        sum_list([1, "2"]) → MathTypeError
    """
    if not isinstance(items, list):
        raise CollectionTypeError("sum_list", "list", type(items).__name__)
    
    if len(items) == 0:
        raise EmptyCollectionError("sum_list")
    
    # Validate all items are numbers
    for i, item in enumerate(items):
        if not isinstance(item, (int, float)) or isinstance(item, bool):
            raise MathTypeError("sum_list", f"items[{i}]", type(item).__name__)
    
    return sum(items)


def all_bool(items: List[bool]) -> bool:
    """
    Check if all booleans in list are True.
    
    Args:
        items: List of booleans
        
    Returns:
        True if all items are True, False otherwise
        True for empty list (vacuous truth)
        
    Raises:
        CollectionTypeError: If items is not a list or contains non-booleans
        
    Examples:
        all_bool([True, True]) → True
        all_bool([True, False]) → False
        all_bool([]) → True (vacuous truth)
        all_bool([1, 1]) → CollectionTypeError
    """
    if not isinstance(items, list):
        raise CollectionTypeError("all_bool", "list", type(items).__name__)
    
    # Validate all items are booleans
    for i, item in enumerate(items):
        if not isinstance(item, bool):
            raise CollectionTypeError("all_bool", f"bool at items[{i}]", type(item).__name__)
    
    return all(items)


def any_bool(items: List[bool]) -> bool:
    """
    Check if any boolean in list is True.
    
    Args:
        items: List of booleans
        
    Returns:
        True if any item is True, False otherwise
        False for empty list
        
    Raises:
        CollectionTypeError: If items is not a list or contains non-booleans
        
    Examples:
        any_bool([False, True]) → True
        any_bool([False, False]) → False
        any_bool([]) → False
        any_bool([1, 0]) → CollectionTypeError
    """
    if not isinstance(items, list):
        raise CollectionTypeError("any_bool", "list", type(items).__name__)
    
    # Validate all items are booleans
    for i, item in enumerate(items):
        if not isinstance(item, bool):
            raise CollectionTypeError("any_bool", f"bool at items[{i}]", type(item).__name__)
    
    return any(items)


def unique(items: List[Any]) -> List[Any]:
    """
    Return list with duplicates removed, preserving first occurrence order.
    
    Args:
        items: List to deduplicate
        
    Returns:
        New list with unique items in order of first appearance
        
    Raises:
        CollectionTypeError: If items is not a list
        
    Examples:
        unique([1, 2, 1, 3]) → [1, 2, 3]
        unique([]) → []
        unique(["a", "b", "a"]) → ["a", "b"]
        
    Note:
        Order is deterministic - first occurrence is kept.
        Uses equality comparison for duplicates.
    """
    if not isinstance(items, list):
        raise CollectionTypeError("unique", "list", type(items).__name__)
    
    seen = []
    result = []
    for item in items:
        if item not in seen:
            seen.append(item)
            result.append(item)
    
    return result


def length(items: List[Any]) -> int:
    """
    Return the number of items in a collection.
    
    Args:
        items: Collection to measure
        
    Returns:
        Number of items (0 for empty list)
        
    Raises:
        CollectionTypeError: If items is not a list
        
    Examples:
        length([1, 2, 3]) → 3
        length([]) → 0
        
    Note:
        This is an alias for count() for clarity.
    """
    if not isinstance(items, list):
        raise CollectionTypeError("length", "list", type(items).__name__)
    
    return len(items)


def count_value(items: List[Any], value: Any) -> int:
    """
    Count occurrences of a value in a collection.
    
    Pure function that counts how many times a value appears.
    Uses equality (==) for comparison.
    
    Args:
        items: Collection to search
        value: Value to count
        
    Returns:
        Number of times value appears in collection
        
    Raises:
        TypeError: If items is not a list
    """
    if not isinstance(items, list):
        raise TypeError(f"count_value requires list, got {type(items).__name__}")
    
    count = 0
    for item in items:
        if item == value:
            count += 1
    
    return count


def any_predicate(items: List[Any], predicate: Callable[[Any], bool]) -> bool:
    """
    Check if any item satisfies the predicate.
    
    Short-circuit evaluation: returns True as soon as predicate returns True.
    Empty collection returns False (no items satisfy predicate).
    
    Args:
        items: Collection to check
        predicate: Function that returns True/False for each item
        
    Returns:
        True if at least one item satisfies predicate, False otherwise
        
    Raises:
        TypeError: If items is not a list or predicate is not callable
    """
    if not isinstance(items, list):
        raise TypeError(f"any_predicate requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"any_predicate requires callable predicate, got {type(predicate).__name__}")
    
    for item in items:
        if predicate(item):
            return True
    
    return False


def all_predicate(items: List[Any], predicate: Callable[[Any], bool]) -> bool:
    """
    Check if all items satisfy the predicate.
    
    Short-circuit evaluation: returns False as soon as predicate returns False.
    Empty collection returns True (vacuous truth - no items fail predicate).
    
    Args:
        items: Collection to check
        predicate: Function that returns True/False for each item
        
    Returns:
        True if all items satisfy predicate, False otherwise
        
    Raises:
        TypeError: If items is not a list or predicate is not callable
    """
    if not isinstance(items, list):
        raise TypeError(f"all_predicate requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"all_predicate requires callable predicate, got {type(predicate).__name__}")
    
    for item in items:
        if not predicate(item):
            return False
    
    return True


__all__ = [
    'count',
    'is_empty',
    'contains',
    'filter_items',
    'map_items',
    'reduce',
    'reverse',
    'sort',
    'zip',
    'enumerate_items',
    'range_list',
    'sum_list',
    'all_bool',
    'any_bool',
    'unique',
    'length',
    'count_value',
    'any_predicate',
    'all_predicate',
]

