# APE Standard Library v0 (Pure, Deterministic Core)

## Overview

The APE Standard Library v0 provides a foundational set of pure, deterministic functions that form the computational core of the language. These functions are implemented as **runtime intrinsics** and are available without requiring any capability grants.

**Version**: 0.1.0  
**Status**: Stable  
**License**: MIT

## Philosophy

### Pure Functions Only

Every function in stdlib v0 is **pure**:
- Same input → same output (deterministic)
- No side effects
- No mutations to input data
- No IO, filesystem, or network access
- No environment dependencies

### Runtime Intrinsics

Stdlib functions are implemented as **runtime intrinsics**, meaning:
- They are built into the RuntimeExecutor
- They do not require capability checks
- They execute directly without external dependencies
- They are fully traceable in execution logs
- They are available in all execution modes (normal, dry-run, replay)

### Type Safety

All stdlib functions perform runtime type validation:
- Clear error messages for invalid input types
- Explicit type requirements in function signatures
- No silent type coercion
- TypeError raised for type mismatches

### No Language Extensions

Stdlib v0 adds **no new language features**:
- No parser changes
- No AST modifications
- No runtime semantics changes
- Pure Python implementation
- Fully backward compatible

## Modules

### std.logic - Boolean Logic & Assertions

Pure boolean logic and assertion functions.

#### `assert_condition(condition: bool, message: str = None) -> None`

Validate a condition and raise an error if false.

**Parameters:**
- `condition` (bool): Boolean condition to check
- `message` (str, optional): Custom error message if condition is false

**Raises:**
- `RuntimeError`: If condition is false
- `TypeError`: If condition is not a boolean

**Example:**
```python
# In APE syntax (future integration)
TASK validate_age:
    std.logic.assert_condition(age >= 18, "Must be 18 or older")
```

#### `all_true(values: List[Any]) -> bool`

Check if all values in a list are truthy.

**Parameters:**
- `values` (List[Any]): List of values to check

**Returns:**
- `bool`: True if all values are truthy, False otherwise

**Raises:**
- `TypeError`: If values is not a list

**Example:**
```python
result = std.logic.all_true([True, 1, "yes", [1]])  # True
result = std.logic.all_true([True, 0, "yes"])       # False
```

#### `any_true(values: List[Any]) -> bool`

Check if any value in a list is truthy.

**Parameters:**
- `values` (List[Any]): List of values to check

**Returns:**
- `bool`: True if any value is truthy, False otherwise

**Raises:**
- `TypeError`: If values is not a list

**Example:**
```python
result = std.logic.any_true([False, 0, "", 1])  # True
result = std.logic.any_true([False, 0, ""])     # False
```

#### `none_true(values: List[Any]) -> bool`

Check if no values in a list are truthy.

**Parameters:**
- `values` (List[Any]): List of values to check

**Returns:**
- `bool`: True if no values are truthy, False otherwise

**Raises:**
- `TypeError`: If values is not a list

**Example:**
```python
result = std.logic.none_true([False, 0, "", []])  # True
result = std.logic.none_true([False, 0, 1])       # False
```

#### `equals(a: Any, b: Any) -> bool`

Check equality between two values.

**Parameters:**
- `a` (Any): First value
- `b` (Any): Second value

**Returns:**
- `bool`: True if values are equal, False otherwise

**Example:**
```python
result = std.logic.equals(42, 42)           # True
result = std.logic.equals("hello", "world") # False
```

#### `not_equals(a: Any, b: Any) -> bool`

Check inequality between two values.

**Parameters:**
- `a` (Any): First value
- `b` (Any): Second value

**Returns:**
- `bool`: True if values are not equal, False otherwise

**Example:**
```python
result = std.logic.not_equals(42, 43)  # True
result = std.logic.not_equals(42, 42)  # False
```

---

### std.collections - Collection Operations

Pure collection manipulation functions.

#### `count(items: List[Any]) -> int`

Return the length of a collection.

**Parameters:**
- `items` (List[Any]): Collection to count

**Returns:**
- `int`: Number of items in collection

**Raises:**
- `TypeError`: If items is not a list

**Example:**
```python
result = std.collections.count([1, 2, 3])  # 3
result = std.collections.count([])         # 0
```

#### `is_empty(items: List[Any]) -> bool`

Check if a collection is empty.

**Parameters:**
- `items` (List[Any]): Collection to check

**Returns:**
- `bool`: True if collection is empty, False otherwise

**Raises:**
- `TypeError`: If items is not a list

**Example:**
```python
result = std.collections.is_empty([])      # True
result = std.collections.is_empty([1, 2])  # False
```

#### `contains(items: List[Any], value: Any) -> bool`

Check if a value is in a collection.

**Parameters:**
- `items` (List[Any]): Collection to search
- `value` (Any): Value to find

**Returns:**
- `bool`: True if value is in collection, False otherwise

**Raises:**
- `TypeError`: If items is not a list

**Example:**
```python
result = std.collections.contains([1, 2, 3], 2)  # True
result = std.collections.contains([1, 2, 3], 4)  # False
```

#### `filter_items(items: List[Any], predicate: Callable[[Any], bool]) -> List[Any]`

Filter collection using a predicate function.

**Parameters:**
- `items` (List[Any]): Collection to filter
- `predicate` (Callable): Function that returns True for items to keep

**Returns:**
- `List[Any]`: New list containing only items where predicate returned True

**Raises:**
- `TypeError`: If items is not a list or predicate is not callable

**Example:**
```python
result = std.collections.filter_items([1, 2, 3, 4], lambda x: x > 2)
# Result: [3, 4]
```

#### `map_items(items: List[Any], transformer: Callable[[Any], Any]) -> List[Any]`

Transform collection using a transformer function.

**Parameters:**
- `items` (List[Any]): Collection to transform
- `transformer` (Callable): Function to apply to each item

**Returns:**
- `List[Any]`: New list containing transformed items

**Raises:**
- `TypeError`: If items is not a list or transformer is not callable

**Example:**
```python
result = std.collections.map_items([1, 2, 3], lambda x: x * 2)
# Result: [2, 4, 6]
```

---

### std.strings - String Manipulation

Pure string manipulation functions.

#### `lower(text: str) -> str`

Convert text to lowercase.

**Parameters:**
- `text` (str): String to convert

**Returns:**
- `str`: Lowercase version of text

**Raises:**
- `TypeError`: If text is not a string

**Example:**
```python
result = std.strings.lower("HELLO")  # "hello"
result = std.strings.lower("HeLLo")  # "hello"
```

#### `upper(text: str) -> str`

Convert text to uppercase.

**Parameters:**
- `text` (str): String to convert

**Returns:**
- `str`: Uppercase version of text

**Raises:**
- `TypeError`: If text is not a string

**Example:**
```python
result = std.strings.upper("hello")  # "HELLO"
result = std.strings.upper("HeLLo")  # "HELLO"
```

#### `trim(text: str) -> str`

Remove leading and trailing whitespace.

**Parameters:**
- `text` (str): String to trim

**Returns:**
- `str`: Trimmed string

**Raises:**
- `TypeError`: If text is not a string

**Example:**
```python
result = std.strings.trim("  hello  ")  # "hello"
result = std.strings.trim("\thello\n")  # "hello"
```

#### `starts_with(text: str, prefix: str) -> bool`

Check if text starts with a prefix.

**Parameters:**
- `text` (str): String to check
- `prefix` (str): Prefix to look for

**Returns:**
- `bool`: True if text starts with prefix, False otherwise

**Raises:**
- `TypeError`: If text or prefix is not a string

**Example:**
```python
result = std.strings.starts_with("hello world", "hello")  # True
result = std.strings.starts_with("hello world", "world")  # False
```

#### `ends_with(text: str, suffix: str) -> bool`

Check if text ends with a suffix.

**Parameters:**
- `text` (str): String to check
- `suffix` (str): Suffix to look for

**Returns:**
- `bool`: True if text ends with suffix, False otherwise

**Raises:**
- `TypeError`: If text or suffix is not a string

**Example:**
```python
result = std.strings.ends_with("hello world", "world")  # True
result = std.strings.ends_with("hello world", "hello")  # False
```

#### `contains_text(text: str, fragment: str) -> bool`

Check if text contains a fragment.

**Parameters:**
- `text` (str): String to search
- `fragment` (str): Fragment to find

**Returns:**
- `bool`: True if text contains fragment, False otherwise

**Raises:**
- `TypeError`: If text or fragment is not a string

**Example:**
```python
result = std.strings.contains_text("hello world", "lo wo")  # True
result = std.strings.contains_text("hello world", "xyz")    # False
```

---

### std.math - Mathematical Operations

Pure mathematical functions.

#### `abs_value(x: Union[int, float]) -> Union[int, float]`

Return absolute value of a number.

**Parameters:**
- `x` (int|float): Number to process

**Returns:**
- `int|float`: Absolute value of x

**Raises:**
- `TypeError`: If x is not a number

**Example:**
```python
result = std.math.abs_value(-42)   # 42
result = std.math.abs_value(3.14)  # 3.14
```

#### `min_value(a: Union[int, float], b: Union[int, float]) -> Union[int, float]`

Return minimum of two values.

**Parameters:**
- `a` (int|float): First value
- `b` (int|float): Second value

**Returns:**
- `int|float`: Minimum of a and b

**Raises:**
- `TypeError`: If a or b is not a number

**Example:**
```python
result = std.math.min_value(5, 10)  # 5
result = std.math.min_value(42, 42) # 42
```

#### `max_value(a: Union[int, float], b: Union[int, float]) -> Union[int, float]`

Return maximum of two values.

**Parameters:**
- `a` (int|float): First value
- `b` (int|float): Second value

**Returns:**
- `int|float`: Maximum of a and b

**Raises:**
- `TypeError`: If a or b is not a number

**Example:**
```python
result = std.math.max_value(5, 10)  # 10
result = std.math.max_value(42, 42) # 42
```

#### `clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]`

Clamp a value to a range.

**Parameters:**
- `value` (int|float): Value to clamp
- `min_val` (int|float): Minimum value
- `max_val` (int|float): Maximum value

**Returns:**
- `int|float`: Value clamped between min_val and max_val

**Raises:**
- `TypeError`: If any argument is not a number
- `ValueError`: If min_val > max_val

**Example:**
```python
result = std.math.clamp(5, 0, 10)   # 5
result = std.math.clamp(-5, 0, 10)  # 0
result = std.math.clamp(15, 0, 10)  # 10
```

#### `sum_values(values: List[Union[int, float]]) -> Union[int, float]`

Return sum of a collection of numbers.

**Parameters:**
- `values` (List[int|float]): List of numbers to sum

**Returns:**
- `int|float`: Sum of all values

**Raises:**
- `TypeError`: If values is not a list or contains non-numbers

**Example:**
```python
result = std.math.sum_values([1, 2, 3, 4])  # 10
result = std.math.sum_values([])            # 0
result = std.math.sum_values([1.5, 2.5])    # 4.0
```

---

## Usage from APE Programs

### Current Status (v0.1.0)

**Note**: Full APE syntax integration is planned for a future release. Current implementation provides Python-callable functions that will be exposed to APE programs through the runtime executor.

### Future Integration Example

```ape
# Example of how stdlib will be used from APE (future release)

TASK process_data:
    # Logic operations
    std.logic.assert_condition(age >= 18, "Must be adult")
    is_valid = std.logic.all_true([has_name, has_email, has_phone])
    
    # Collection operations
    item_count = std.collections.count(items)
    filtered = std.collections.filter_items(items, is_active)
    names = std.collections.map_items(users, get_name)
    
    # String operations
    normalized = std.strings.trim(std.strings.lower(input))
    is_greeting = std.strings.starts_with(message, "Hello")
    
    # Math operations
    total = std.math.sum_values(prices)
    clamped_score = std.math.clamp(score, 0, 100)
```

---

## What is NOT Included

The stdlib v0 deliberately **excludes**:

### ❌ IO Operations
- No file reading/writing
- No network access
- No console output
- No environment variable access

**Rationale**: IO operations require capabilities and are side effects. They belong in capability-gated modules, not the pure stdlib.

### ❌ Time/Date Operations
- No current time
- No date parsing
- No timezone operations

**Rationale**: Time operations are non-deterministic and environment-dependent. Not suitable for pure stdlib.

### ❌ Random Numbers
- No random number generation
- No UUID generation

**Rationale**: Non-deterministic. Would break traceability and replay.

### ❌ State Mutation
- No global variables
- No caches
- No memoization

**Rationale**: Pure functions must not maintain hidden state.

### ❌ External Libraries
- No NumPy
- No Pandas
- No third-party dependencies

**Rationale**: Stdlib must be self-contained and deterministic.

---

## Design Principles

### 1. Determinism

Every stdlib function is **deterministic**:
```python
# Same input always produces same output
assert std.math.abs_value(-5) == std.math.abs_value(-5)
assert std.strings.lower("HELLO") == std.strings.lower("HELLO")
```

### 2. Purity

No side effects:
```python
# Original data is never mutated
items = [1, 2, 3]
filtered = std.collections.filter_items(items, lambda x: x > 1)
# items is still [1, 2, 3]
```

### 3. Traceability

All calls are visible in execution traces:
```python
# Every stdlib call is recorded in trace
executor = RuntimeExecutor(trace=TraceCollector())
result = executor.execute(program)
# Trace contains all std.* calls
```

### 4. Type Safety

Clear type validation:
```python
# TypeError with clear message
try:
    std.math.abs_value("not a number")
except TypeError as e:
    print(e)  # "abs_value requires number, got str"
```

### 5. Composability

Functions compose naturally:
```python
# Chain stdlib functions
result = std.strings.trim(
    std.strings.lower(
        input_text
    )
)
```

---

## Testing

Stdlib v0 has **86 comprehensive tests** covering:

- ✅ Happy path for all functions
- ✅ Type validation for all parameters
- ✅ Edge cases (empty lists, zero, boundaries)
- ✅ Error messages
- ✅ Determinism
- ✅ Purity (no mutations)

**Test suite**: `tests/std/test_stdlib_core.py`

**Run tests**:
```bash
pytest tests/std/test_stdlib_core.py -v
```

**All tests passing**: 86/86 ✅

---

## Performance Characteristics

All stdlib functions have **predictable performance**:

| Function | Time Complexity | Space Complexity |
|----------|----------------|------------------|
| `std.logic.*` | O(1) or O(n) | O(1) |
| `std.collections.count` | O(1) | O(1) |
| `std.collections.is_empty` | O(1) | O(1) |
| `std.collections.contains` | O(n) | O(1) |
| `std.collections.filter_items` | O(n) | O(n) |
| `std.collections.map_items` | O(n) | O(n) |
| `std.strings.*` | O(n) | O(n) |
| `std.math.*` | O(1) or O(n) | O(1) |

Where:
- `n` = length of input collection or string
- All functions use constant memory except those creating new collections

---

## Version History

### v0.1.0 (Current)

**Release Date**: 2024

**Modules**:
- `std.logic` - 6 functions
- `std.collections` - 5 functions
- `std.strings` - 6 functions
- `std.math` - 5 functions

**Total Functions**: 22

**Test Coverage**: 86 tests, 100% passing

**Status**: Stable, production-ready

---

## Future Extensions

### Planned for v0.2.0

**Potential additions** (subject to community input):

1. **std.logic**:
   - `xor(a, b)` - Exclusive OR
   - `implies(a, b)` - Logical implication

2. **std.collections**:
   - `reverse(items)` - Reverse collection
   - `sort(items)` - Sort collection
   - `unique(items)` - Remove duplicates
   - `zip(items1, items2)` - Combine two collections

3. **std.strings**:
   - `split(text, delimiter)` - Split string
   - `join(items, separator)` - Join strings
   - `replace(text, old, new)` - Replace substring
   - `repeat(text, count)` - Repeat string

4. **std.math**:
   - `pow(base, exponent)` - Power
   - `sqrt(x)` - Square root
   - `floor(x)` - Floor
   - `ceil(x)` - Ceiling
   - `round_value(x, decimals)` - Round

### Guidelines for Future Extensions

All future stdlib functions must:
1. ✅ Be pure (no side effects)
2. ✅ Be deterministic (same input → same output)
3. ✅ Have clear type validation
4. ✅ Have comprehensive tests
5. ✅ Have clear documentation
6. ✅ Not require capabilities
7. ✅ Be traceable

---

## FAQ

### Q: Why no print() function?

**A**: `print()` is a side effect (IO operation). It requires the `io.stdout` capability and belongs in capability-gated modules, not the pure stdlib.

### Q: Why no random number generation?

**A**: Random numbers are non-deterministic. They would break execution replay and traceability. For deterministic pseudo-random numbers, use a future `std.prng` module with explicit seed.

### Q: Why no JSON parsing?

**A**: JSON parsing from strings is deterministic and could be added in v0.2.0. JSON loading from files requires IO capabilities.

### Q: Why no regex?

**A**: Regex is deterministic and could be added in v0.2.0 as `std.patterns` module.

### Q: Can I add my own stdlib modules?

**A**: Not yet. Stdlib v0 is built-in only. Future releases may support user-defined stdlib extensions through a plugin system.

### Q: Why Python callables for filter/map?

**A**: Current implementation uses Python lambdas for testing. Future APE integration will use APE function references (e.g., `FUNCTION is_positive(x) -> x > 0`).

### Q: Is stdlib v0 stable?

**A**: Yes. Stdlib v0 is production-ready with 86 passing tests and full documentation.

---

## See Also

- [APE 1.0 Specification](APE_1.0_SPECIFICATION.md)
- [Multi-Language Documentation](multilanguage.md)
- [Runtime Executor](../src/ape/runtime/executor.py)
- [Stdlib Tests](../tests/std/test_stdlib_core.py)

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Status**: Final
