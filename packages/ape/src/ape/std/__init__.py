"""
APE Standard Library v0 (Pure, Deterministic Core)

This is the foundational standard library for APE, containing only pure,
deterministic functions with no side effects. All functions are implemented
as runtime intrinsics and do not require capability checks.

Modules:
- logic: Boolean logic and assertion functions
- collections: List/collection operations
- strings: String manipulation functions
- math: Mathematical operations

Design Principles:
- Pure functions only (no side effects)
- Deterministic (same input → same output)
- Full traceability and explainability
- Clear error messages for invalid inputs
- No IO, filesystem, or network operations
"""

from ape.std import logic, collections, strings, math

__all__ = [
    'logic',
    'collections',
    'strings',
    'math',
]
