# Code Generator Extensions for Module-Qualified Identifiers

## Overview

This document describes the implementation of deterministic name mangling for module-qualified identifiers in the Ape v0.2.0 code generator. The implementation ensures that tasks and flows defined in modules get unique, predictable names in the generated Python code.

## Implementation Summary

### 1. Name Mangling Function (`mangle_name`)

**Location**: `src/ape/codegen/python_codegen.py`

**Purpose**: Single source of truth for deterministic name mangling

**Rule**: `<module>.<symbol>` → `<module>__<symbol>`

**Signature**:
```python
def mangle_name(module_name: Optional[str], symbol_name: str) -> str
```

**Behavior**:
- If `module_name` is `None` or empty: returns `symbol_name` unchanged (backward compatible)
- Otherwise: returns `f"{module_name}__{symbol_name}"`

**Examples**:
```python
mangle_name("math", "add")      # → "math__add"
mangle_name("strings", "upper") # → "strings__upper"
mangle_name(None, "calculate")  # → "calculate"
mangle_name("", "process")      # → "process"
```

### 2. Code Generator Updates

**Changes to `PythonCodeGenerator` class**:

1. **Added `current_module_name` tracking**:
   - Tracks the current module being generated
   - Set in `_generate_module()` method
   - Used by `_emit_task()` and `_emit_flow()` for name mangling

2. **Smart module name detection**:
   - Only uses module name for mangling if it's an actual module name
   - Filters out filenames (containing `.ape`, `/`, or `\`)
   - Ensures backward compatibility with legacy code

3. **Updated `_emit_task()` method**:
   - Now calls `mangle_name(self.current_module_name, task.name)`
   - Generates mangled function names for tasks in modules
   - Preserves original names for tasks without modules

4. **Updated `_emit_flow()` method**:
   - Now calls `mangle_name(self.current_module_name, flow.name)`
   - Generates mangled function names for flows in modules
   - Preserves original names for flows without modules

5. **Added `resolve_qualified_name()` method**:
   - Resolves qualified identifiers in expressions
   - Handles simple identifiers (no change)
   - Handles qualified identifiers (e.g., `math.add` → `math__add`)
   - Handles deeply nested paths (e.g., `strings.utils.upper` → `strings.utils__upper`)

### 3. Backward Compatibility

**Design Decisions**:

1. **No module declaration** → No mangling
   - Files without `module` declarations generate unmangled names
   - Maintains compatibility with existing Ape code

2. **Filename fallback filtering**:
   - IR builder uses filename as fallback module name
   - Codegen detects filenames (by presence of `.ape`, `/`, `\`)
   - Treats filenames as "no module declaration" case

3. **Empty module name** → No mangling
   - `ModuleNode(name="")` or `ModuleNode(name=None)` generates unmangled names
   - Explicit way to request backward-compatible behavior

### 4. Test Coverage

**New Test File**: `tests/codegen/python/test_namespaced_calls.py` (15 tests)

**Test Categories**:

1. **Name Mangling Tests** (3 tests):
   - Mangling with module name
   - No mangling without module name
   - Symbol name preservation

2. **Module-Aware Task Generation** (4 tests):
   - Task in named module (mangled)
   - Task without module declaration (not mangled)
   - Task in module with None name (not mangled)
   - Multiple tasks in same module (all mangled)

3. **Module-Aware Flow Generation** (2 tests):
   - Flow in named module (mangled)
   - Flow without module (not mangled)

4. **Qualified Identifier Resolution** (3 tests):
   - Simple identifier resolution
   - Qualified identifier resolution
   - Deeply nested identifier resolution

5. **Multi-Module Projects** (2 tests):
   - Two modules with different task names
   - Two modules with same task name (different mangled names)

6. **Backward Compatibility** (1 test):
   - Legacy single file without module declaration

**Updated Tests**: Modified 2 existing tests in `test_codegen.py` to use empty module names

### 5. Integration with Linker

**Current State**:
- Code generator receives modules from linker in topological order
- Each module has a deterministic name (from module declaration or filename)
- Name mangling uses module names consistently across the project

**Future Work** (not in scope for v0.2.0):
- Parse and transform function calls in step text
- Generate actual function invocations using mangled names
- Symbol table management across modules

## Usage Examples

### Example 1: Basic Module with Tasks

**Ape Source**:
```ape
module math

task add:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: Integer
    steps:
        - return sum of a and b
```

**Generated Python**:
```python
def math__add(a: int, b: int) -> int:
    """Auto-generated from Ape task 'add'."""
    raise NotImplementedError
```

### Example 2: Multi-Module Project

**math.ape**:
```ape
module math

task add:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: Integer
```

**main.ape**:
```ape
module main

import math

task calculate:
    inputs:
        x: Integer
        y: Integer
    outputs:
        result: Integer
    steps:
        - call math.add with x and y
```

**Generated Python** (math_gen.py):
```python
def math__add(a: int, b: int) -> int:
    """Auto-generated from Ape task 'add'."""
    raise NotImplementedError
```

**Generated Python** (main_gen.py):
```python
def main__calculate(x: int, y: int) -> int:
    """Auto-generated from Ape task 'calculate'."""
    # Future: Would generate: result = math__add(x, y)
    raise NotImplementedError
```

### Example 3: Backward Compatible (No Module)

**Ape Source** (no module declaration):
```ape
task calculate:
    inputs:
        x: Integer
    outputs:
        result: Integer
```

**Generated Python**:
```python
def calculate(x: int) -> int:
    """Auto-generated from Ape task 'calculate'."""
    raise NotImplementedError
```

## API Reference

### `mangle_name(module_name, symbol_name) -> str`

Deterministically mangle a module-qualified symbol name.

**Parameters**:
- `module_name` (Optional[str]): Module name or None
- `symbol_name` (str): Symbol name to mangle

**Returns**: Mangled name or original name if no module

### `PythonCodeGenerator.resolve_qualified_name(qualified_name) -> str`

Resolve a qualified identifier to its mangled form.

**Parameters**:
- `qualified_name` (str): Qualified identifier like "math.add" or simple name

**Returns**: Mangled name if qualified, original name if simple

**Examples**:
```python
codegen = PythonCodeGenerator(project)
codegen.resolve_qualified_name("math.add")     # → "math__add"
codegen.resolve_qualified_name("calculate")    # → "calculate"
```

## Design Rationale

### Why Double Underscore (`__`)?

1. **Python Convention**: Double underscore is used for name mangling in Python
2. **Readability**: Clear separation between module and symbol
3. **Uniqueness**: Unlikely to conflict with user-chosen names
4. **Consistency**: Matches Python's own mangling practices

### Why Module-Level Mangling (Not File-Level)?

1. **Deterministic**: Module names are explicit in source code
2. **Portable**: Independent of file system structure
3. **Semantic**: Reflects logical organization, not physical layout
4. **Linker Integration**: Aligns with module resolution semantics

### Why Filter Filenames?

1. **Backward Compatibility**: Legacy code doesn't have module declarations
2. **IR Builder Behavior**: Uses filename as fallback module name
3. **User Expectation**: Filename-as-module would be surprising for old code
4. **Gradual Migration**: Allows incremental adoption of module system

## Testing Results

**All Tests Passing**: ✅ 142/142

**Test Breakdown**:
- Original tests: 127 (all passing, backward compatible)
- New namespaced tests: 15 (all passing)

**Coverage**:
- ✅ Name mangling function
- ✅ Task generation with modules
- ✅ Flow generation with modules
- ✅ Qualified identifier resolution
- ✅ Multi-module projects
- ✅ Backward compatibility
- ✅ Edge cases (None name, empty name, filenames)

## Future Enhancements

Potential improvements for future versions:

1. **Function Call Transformation**:
   - Parse step text for function calls
   - Transform `math.add(1, 2)` to `math__add(1, 2)` in generated code
   - Requires step text parsing and AST transformation

2. **Import Statement Generation**:
   - Generate Python imports based on Ape imports
   - Handle cross-module dependencies explicitly

3. **Symbol Table Management**:
   - Track all symbols across modules
   - Validate references at code generation time
   - Detect undefined symbol errors early

4. **Namespace Aliasing**:
   - Support `import math as m` syntax
   - Generate code with aliased names

5. **Selective Imports**:
   - Support `from math import add, subtract` syntax
   - Generate code with direct symbol names (no module prefix)

## Compliance with Requirements

✅ **Deterministic name mangling**: `<module>.<symbol>` → `<module>__<symbol>`

✅ **Single source of truth**: `mangle_name()` function used consistently

✅ **Function definitions**: Tasks and flows in modules get mangled names

✅ **Backward compatibility**: Non-module code generates unchanged names

✅ **Integration ready**: Works with linker's module ordering

✅ **Comprehensive tests**: 15 new tests covering all scenarios

✅ **All tests passing**: 142/142 tests pass

## Conclusion

The code generator now correctly handles module-qualified identifiers with deterministic name mangling. The implementation is:

- **Deterministic**: Same input always produces same output
- **Backward Compatible**: Existing code without modules works unchanged
- **Well-Tested**: Comprehensive test coverage validates all scenarios
- **Future-Ready**: Architecture supports upcoming enhancements
- **Standards-Compliant**: Follows Python naming conventions

The Ape v0.2.0 module system now has full support from specification through parsing, linking, and code generation.
