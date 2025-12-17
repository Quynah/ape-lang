# APE Runtime Contract - Decision Engine v2024

## Overview

This document defines the explicit runtime contract between APE programs and Python host environments.  
**Contract Principle:** Deterministic, explicit, no silent failures.

## Data Type Mapping

### APE → Python (Output Contract)

| APE Type | Python Type | Serialization Rule |
|----------|-------------|-------------------|
| `Integer` | `int` | Direct mapping |
| `Float` | `float` | Direct mapping |
| `String` | `str` | UTF-8 encoded |
| `Boolean` | `bool` | `true` → `True`, `false` → `False` |
| `DateTime` | `str` | ISO-8601 UTC (e.g., `"2024-05-08T12:00:00Z"`) |
| `Duration` | `int` | Total seconds |
| `List` | `list` | Ordered sequence |
| `Map` | `dict` | Key-value mapping |
| `Record` | `dict` | Named fields as dict |
| `Any` / `Value` | Any Python type | Pass-through |

### Python → APE (Input Contract)

| Python Type | APE Type | Validation Rule |
|-------------|----------|-----------------|
| `int` | `Integer` | Range-checked (platform-dependent) |
| `float` | `Float` | IEEE 754 double |
| `str` | `String` | UTF-8 validated |
| `bool` | `Boolean` | Direct mapping |
| `list` | `List` | Element types validated if typed |
| `dict` | `Map` or `Record` | Key/value types validated if typed |
| `None` | Not allowed | Explicit error unless `Optional` |

## Collection Guarantees

### Lists
- **Immutability:** APE lists are conceptually immutable; operations return new lists
- **Ordering:** Preserved in all operations
- **Element Access:** Zero-indexed, out-of-bounds raises error
- **Empty List:** Valid, returns `[]` in Python

### Maps/Records
- **Key Uniqueness:** Last value wins on duplicate keys
- **Iteration Order:** Insertion order preserved (Python 3.7+)
- **Missing Keys:** `json.get` returns default, direct access may raise error
- **Nested Access:** `json.get("a.b.c", default)` never raises, always returns value or default

## DateTime Contract

### Representation
- **Internal:** `datetime.datetime` with UTC timezone
- **External:** ISO-8601 string with `Z` suffix (e.g., `"2024-12-17T10:30:00Z"`)
- **Timezone:** Always UTC; local times must be converted explicitly

### Operations
- **now():** Returns current UTC time
- **parse_iso8601(str):** Parses ISO-8601 string; raises `ValueError` if invalid
- **subtract_days(dt, n):** Subtracts `n` days (immutable, returns new DateTime)
- **add_days(dt, n):** Adds `n` days (immutable, returns new DateTime)
- **compare(dt1, dt2):** Returns `-1` (less), `0` (equal), `1` (greater)

### Arithmetic
- `dt.subtract_days(7)` → new DateTime 7 days earlier
- `dt.add_hours(2)` → new DateTime 2 hours later
- **No implicit conversions:** Explicit function calls required

## Error Handling

### Hard Failures (Exceptions)
- **Type Mismatch:** Function receives wrong type → `TypeError`
- **Invalid Data:** Parse failure, range overflow → `ValueError`
- **Missing Required Value:** Accessing undefined field → `KeyError`/`AttributeError`

### Graceful Degradation
- **`json.get(data, path, default)`:** Never fails, always returns default if path not found
- **Collection Empty Checks:** `count([])` returns `0`, not error

## Function Call Contract

### Purity Guarantee
All stdlib functions are **pure** (no side effects, deterministic output):
- `std.collections.*` – No mutations, returns new collections
- `std.datetime.*` – No system state modification
- `std.strings.*` – No external I/O
- `json.*` – Read-only operations

### Capability Gating (Future)
Functions requiring side effects (I/O, network) will be:
- Explicitly marked with capability requirements
- Rejected in dry-run mode
- Logged in execution trace

## Serialization Protocol

### Task Outputs
```python
{
  "result": {
    "timestamp": "2024-12-17T10:30:00Z",  # DateTime as ISO-8601
    "records": [                           # List as Python list
      {"id": "a", "score": 10},           # Record as dict
      {"id": "b", "score": 20}
    ],
    "total": 30                            # Integer as int
  },
  "meta": {
    "duration_seconds": 120                # Duration as seconds
  }
}
```

### Error Outputs
```python
{
  "error": {
    "code": "E2001",
    "category": "type",
    "message": "Type mismatch: expected Integer, got String",
    "location": "task.ape:15:10"
  }
}
```

## Implementation Files

- **DateTime Types:** `packages/ape/src/ape/types/datetime_type.py`
- **Collection Functions:** `packages/ape/src/ape/std/collections.py`
- **JSON Access:** `packages/ape/src/ape/std/json.py`
- **Type Validator:** `packages/ape/src/ape/compiler/semantic_validator.py`

## Versioning

**Version:** Decision Engine v2024  
**APE Base:** 1.0.5  
**Compatibility:** Breaking changes to runtime contract will increment major version  
**Stability:** Types and functions in this contract are production-stable
