"""
APE Standard Library v0 (Pure, Deterministic Core)

This is the foundational standard library for APE, containing only pure,
deterministic functions with no side effects. All functions are implemented
as runtime intrinsics and do not require capability checks.

Modules:
- comparison: Strict type-safe comparisons (eq, neq, lt, lte, gt, gte)
- logic: Boolean logic operations (and_op, or_op, not_op) and assertions
- collections: List/collection operations (sum_list, unique, all_bool, any_bool)
- strings: String manipulation functions
- math: Mathematical operations (add, sub, mul, div, abs, min, max)
- errors: Explicit error types for deterministic error handling

Design Principles:
- Pure functions only (no side effects)
- Deterministic (same input → same output)
- Type-strict (no implicit coercion)
- Full traceability and explainability
- Clear error messages for invalid inputs
- No IO, filesystem, or network operations
"""

from ape.std import comparison, logic, collections, strings, math, errors

__all__ = [
    'comparison',
    'logic',
    'collections',
    'strings',
    'math',
    'errors',
]
