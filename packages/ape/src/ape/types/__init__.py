"""
APE Structured Types System (v1.0.0 Scaffold)

This package provides structured data types for APE:
- List<T> - Ordered collections
- Map<K, V> - Key-value mappings
- Record - Named field structures
- Tuple - Fixed-size heterogeneous collections

Author: David Van Aelst
Status: Scaffold - implementation pending
"""

from .list_type import ApeList
from .map_type import ApeMap
from .record_type import ApeRecord
from .tuple_type import ApeTuple

__all__ = ['ApeList', 'ApeMap', 'ApeRecord', 'ApeTuple']
