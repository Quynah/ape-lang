"""
APE Standard Library - Collections Module

Pure collection manipulation functions.
"""

from typing import Any, List, Callable


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
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"reduce requires list, got {type(items).__name__}")
    
    if not callable(reducer):
        raise TypeError(f"reduce requires callable reducer, got {type(reducer).__name__}")
    
    if not items:
        return initial
    
    if initial is None:
        if not items:
            raise ValueError("reduce of empty sequence with no initial value")
        acc = items[0]
        start_idx = 1
    else:
        acc = initial
        start_idx = 0
    
    for item in items[start_idx:]:
        acc = reducer(acc, item)
    
    return acc


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
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"reverse requires list, got {type(items).__name__}")
    
    return items[::-1]


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
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"sort requires list, got {type(items).__name__}")
    
    return sorted(items, key=key, reverse=reverse)


def zip_lists(list1: List[Any], list2: List[Any]) -> List[tuple]:
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
    Status: Decision Engine v2024
    """
    if not isinstance(list1, list):
        raise TypeError(f"zip requires list, got {type(list1).__name__}")
    if not isinstance(list2, list):
        raise TypeError(f"zip requires list, got {type(list2).__name__}")
    
    return list(zip(list1, list2))


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
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"enumerate_items requires list, got {type(items).__name__}")
    
    return list(enumerate(items, start=start))


def range_list(start: int, stop: int = None, step: int = 1) -> List[int]:
    """
    Generate a list of integers in a range.
    
    Example:
        range_list(5)  # [0, 1, 2, 3, 4]
        range_list(1, 5)  # [1, 2, 3, 4]
        range_list(0, 10, 2)  # [0, 2, 4, 6, 8]
    
    Args:
        start: Start value (or stop if stop is None)
        stop: Stop value (exclusive)
        step: Step size
    
    Returns:
        List of integers
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if stop is None:
        return list(range(start))
    return list(range(start, stop, step))


def group_by(items: List[Any], key_func: Callable[[Any], Any]) -> dict:
    """
    Group items by a key function.
    
    Example:
        records = [{"dept": "A", "score": 10}, {"dept": "B", "score": 20}, {"dept": "A", "score": 15}]
        grouped = group_by(records, lambda r: r["dept"])
        # {"A": [{...}, {...}], "B": [{...}]}
    
    Args:
        items: Collection to group
        key_func: Function to extract grouping key from each item
    
    Returns:
        Dict mapping keys to lists of items
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"group_by requires list, got {type(items).__name__}")
    
    if not callable(key_func):
        raise TypeError(f"group_by requires callable key_func, got {type(key_func).__name__}")
    
    result = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    
    return result


def unique(items: List[Any]) -> List[Any]:
    """
    Return unique items from a collection (preserving order).
    
    Example:
        unique([1, 2, 2, 3, 1])  # [1, 2, 3]
    
    Args:
        items: Collection to deduplicate
    
    Returns:
        New list with duplicates removed
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"unique requires list, got {type(items).__name__}")
    
    seen = set()
    result = []
    for item in items:
        # For unhashable types, fall back to linear search
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            if item not in result:
                result.append(item)
    
    return result


def max_value(items: List[Any], key: Callable[[Any], Any] = None) -> Any:
    """
    Find maximum value in a collection.
    
    Example:
        max_value([1, 5, 3])  # 5
        max_value(records, key=lambda r: r["score"])  # record with highest score
    
    Args:
        items: Collection to search
        key: Optional function to extract comparison value
    
    Returns:
        Maximum item
    
    Raises:
        ValueError: If collection is empty
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"max_value requires list, got {type(items).__name__}")
    
    if not items:
        raise ValueError("max_value of empty sequence")
    
    return max(items, key=key)


def min_value(items: List[Any], key: Callable[[Any], Any] = None) -> Any:
    """
    Find minimum value in a collection.
    
    Example:
        min_value([1, 5, 3])  # 1
        min_value(records, key=lambda r: r["score"])  # record with lowest score
    
    Args:
        items: Collection to search
        key: Optional function to extract comparison value
    
    Returns:
        Minimum item
    
    Raises:
        ValueError: If collection is empty
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"min_value requires list, got {type(items).__name__}")
    
    if not items:
        raise ValueError("min_value of empty sequence")
    
    return min(items, key=key)


def sum_values(items: List[Any]) -> Any:
    """
    Sum numeric values in a collection.
    
    Example:
        sum_values([1, 2, 3])  # 6
    
    Args:
        items: Collection of numeric values
    
    Returns:
        Sum of all values
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"sum_values requires list, got {type(items).__name__}")
    
    return sum(items)


def any_match(items: List[Any], predicate: Callable[[Any], bool]) -> bool:
    """
    Check if any item matches a predicate.
    
    Example:
        any_match([1, 2, 3], lambda x: x > 2)  # True
    
    Args:
        items: Collection to check
        predicate: Function returning True for matching items
    
    Returns:
        True if at least one item matches
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"any_match requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"any_match requires callable predicate, got {type(predicate).__name__}")
    
    return any(predicate(item) for item in items)


def all_match(items: List[Any], predicate: Callable[[Any], bool]) -> bool:
    """
    Check if all items match a predicate.
    
    Example:
        all_match([1, 2, 3], lambda x: x > 0)  # True
    
    Args:
        items: Collection to check
        predicate: Function returning True for matching items
    
    Returns:
        True if all items match
    
    Author: David Van Aelst
    Status: Decision Engine v2024
    """
    if not isinstance(items, list):
        raise TypeError(f"all_match requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"all_match requires callable predicate, got {type(predicate).__name__}")
    
    return all(predicate(item) for item in items)


def find(items: List[Any], predicate: Callable[[Any], bool], default: Any = None) -> Any:
    """
    Find first item matching a predicate.
    
    Example:
        find([1, 2, 3, 4], lambda x: x > 2)  # 3
        find([1, 2], lambda x: x > 5, default=-1)  # -1
    
    Args:
        items: Collection to search
        predicate: Function returning True for match
        default: Value to return if no match found
    
    Returns:
        First matching item, or default if none found
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"find requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"find requires callable predicate, got {type(predicate).__name__}")
    
    for item in items:
        if predicate(item):
            return item
    return default


def find_index(items: List[Any], predicate: Callable[[Any], bool]) -> int:
    """
    Find index of first item matching a predicate.
    
    Example:
        find_index([1, 2, 3, 4], lambda x: x > 2)  # 2
        find_index([1, 2], lambda x: x > 5)  # -1
    
    Args:
        items: Collection to search
        predicate: Function returning True for match
    
    Returns:
        Index of first matching item, or -1 if none found
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"find_index requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"find_index requires callable predicate, got {type(predicate).__name__}")
    
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def partition(items: List[Any], predicate: Callable[[Any], bool]) -> tuple:
    """
    Partition collection into two lists based on predicate.
    
    Example:
        partition([1, 2, 3, 4], lambda x: x % 2 == 0)
        # ([2, 4], [1, 3])
    
    Args:
        items: Collection to partition
        predicate: Function returning True for items in first partition
    
    Returns:
        Tuple of (matched_items, unmatched_items)
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"partition requires list, got {type(items).__name__}")
    
    if not callable(predicate):
        raise TypeError(f"partition requires callable predicate, got {type(predicate).__name__}")
    
    matched = []
    unmatched = []
    for item in items:
        if predicate(item):
            matched.append(item)
        else:
            unmatched.append(item)
    
    return (matched, unmatched)


def take(items: List[Any], n: int) -> List[Any]:
    """
    Take first n items from a collection.
    
    Example:
        take([1, 2, 3, 4, 5], 3)  # [1, 2, 3]
    
    Args:
        items: Collection to take from
        n: Number of items to take
    
    Returns:
        New list with first n items
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"take requires list, got {type(items).__name__}")
    
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"take requires non-negative integer, got {n}")
    
    return items[:n]


def skip(items: List[Any], n: int) -> List[Any]:
    """
    Skip first n items from a collection.
    
    Example:
        skip([1, 2, 3, 4, 5], 2)  # [3, 4, 5]
    
    Args:
        items: Collection to skip from
        n: Number of items to skip
    
    Returns:
        New list with first n items removed
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"skip requires list, got {type(items).__name__}")
    
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"skip requires non-negative integer, got {n}")
    
    return items[n:]


def slice_items(items: List[Any], start: int, end: int = None) -> List[Any]:
    """
    Extract a slice of items from a collection.
    
    Example:
        slice_items([1, 2, 3, 4, 5], 1, 4)  # [2, 3, 4]
    
    Args:
        items: Collection to slice
        start: Starting index (inclusive)
        end: Ending index (exclusive), None for end of list
    
    Returns:
        New list with sliced items
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"slice_items requires list, got {type(items).__name__}")
    
    return items[start:end]


def chunk(items: List[Any], size: int) -> List[List[Any]]:
    """
    Split collection into chunks of specified size.
    
    Example:
        chunk([1, 2, 3, 4, 5], 2)  # [[1, 2], [3, 4], [5]]
    
    Args:
        items: Collection to chunk
        size: Size of each chunk
    
    Returns:
        List of chunks (each chunk is a list)
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"chunk requires list, got {type(items).__name__}")
    
    if not isinstance(size, int) or size <= 0:
        raise ValueError(f"chunk requires positive integer, got {size}")
    
    return [items[i:i + size] for i in range(0, len(items), size)]


def join(items: List[str], separator: str = '') -> str:
    """
    Join string items with a separator.
    
    Example:
        join(["a", "b", "c"], ", ")  # "a, b, c"
    
    Args:
        items: Collection of strings
        separator: String to insert between items
    
    Returns:
        Joined string
    
    Author: David Van Aelst
    Status: Decision Engine v2024 - Complete
    """
    if not isinstance(items, list):
        raise TypeError(f"join requires list, got {type(items).__name__}")
    
    return separator.join(str(item) for item in items)


__all__ = [
    'count', 'is_empty', 'contains',
    'filter_items', 'map_items', 'reduce',
    'reverse', 'sort', 'zip_lists', 'enumerate_items',
    'group_by', 'unique',
    'max_value', 'min_value', 'sum_values',
    'any_match', 'all_match',
    'find', 'find_index', 'partition',
    'take', 'skip', 'slice_items', 'chunk', 'join',
    'range_list'
]

