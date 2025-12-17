"""
APE Structured Types System

This package provides structured data types for APE:
- List<T> - Immutable ordered collections (v1.x production)
- Tuple - Immutable fixed-size heterogeneous collections (v1.x production)
- Map<K, V> - Key-value mappings (v1.0.0 scaffold)
- Record - Named field structures (v1.0.0 scaffold)
- DateTime - Temporal points (Decision Engine v2024)
- Duration - Time spans (Decision Engine v2024)

Author: David Van Aelst
Status: Lists and Tuples are production-ready; Map and Record are scaffolded
"""

from .list_type import ApeList, list_map, list_filter, list_reduce, list_concat
from .map_type import ApeMap
from .record_type import ApeRecord
from .tuple_type import ApeTuple
from .datetime_type import ApeDateTime, ApeDuration

__all__ = [
    'ApeList', 'list_map', 'list_filter', 'list_reduce', 'list_concat',
    'ApeMap', 'ApeRecord', 'ApeTuple',
    'ApeDateTime', 'ApeDuration'
]
