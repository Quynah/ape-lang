# Linker Implementation for Ape v0.2.0

## Overview

This document describes the implementation of the **Linker** component for Ape v0.2.0, which provides deterministic module resolution, dependency graph management, and circular dependency detection.

## Components Implemented

### 1. Core Linker (`src/ape/linker.py`)

The linker consists of several key classes:

#### `LinkError`
- Custom exception for link-time errors
- Used for module resolution failures and circular dependencies

#### `ResolvedModule`
- Dataclass representing a resolved module
- Contains:
  - `module_name`: The declared or inferred module name
  - `file_path`: Absolute path to the source file
  - `ast`: Parsed AST of the module
  - `imports`: List of imported module names
  - `depends_on`: Set of module names this module depends on

#### `LinkedProgram`
- Result of successful linking
- Contains:
  - `entry_module`: The entry point module
  - `modules`: List of modules in topological order (dependencies first)
  - `module_map`: Dictionary for fast module lookup by name

#### `Linker`
- Main linker class with the following capabilities:

**Module Resolution**:
- Deterministic search order:
  1. `./lib/<module>.ape`
  2. `./<module>.ape`
  3. `<APE_INSTALL>/ape_std/<module>.ape`
- No fallbacks or ambiguous resolution
- Resolves hierarchical module paths (e.g., `strings.upper` → `strings/upper.ape`)

**Circular Dependency Detection**:
- Detects cycles during resolution using a resolution stack
- Provides clear error messages showing the cycle path (e.g., `a -> b -> c -> a`)
- Works with cycles of any length
- Distinguishes between cycles and diamond dependencies

**Dependency Graph**:
- Builds a complete dependency graph during resolution
- Performs topological sort to order modules
- Ensures dependencies are compiled before dependents

**API**:
- `link(entry_file: Path) -> LinkedProgram`: Main entry point
- `get_dependency_graph() -> Dict[str, List[str]]`: Get adjacency list

### 2. CLI Integration (`src/ape/cli.py`)

Updated CLI to use the linker:

**Changes**:
- `build_project()`: Now uses `Linker` instead of parsing single file
- `cmd_validate()`: Added `LinkError` handling with graceful error reporting
- `cmd_build()`: Added `LinkError` handling

**Impact**:
- All CLI commands now support multi-file projects
- Imports are resolved correctly
- Circular dependencies are caught early with helpful error messages

### 3. IR Builder Updates (`src/ape/ir/ir_builder.py`)

**Changes**:
- Updated import processing to use new AST structure
- Changed from `imp.module_path` to `imp.module_name`

### 4. Comprehensive Test Suite

Created 22 comprehensive tests covering all linker functionality:

#### Basic Tests (`tests/linker/test_linker_basic.py`)
- Single file with no imports
- Single file with module declaration
- Import from same directory
- Import from lib/ subfolder
- Multiple imports
- Transitive dependencies (A → B → C)
- Diamond dependencies (A → B,C; B,C → D)
- Module not found error
- Entry file not found error
- Import without module declaration

#### Resolution Order Tests
- lib/ takes precedence over same directory
- ape_std/ as fallback

#### Dependency Graph Tests
- Correct dependency graph construction
- Topological ordering

#### Cycle Detection Tests (`tests/linker/test_linker_cycles.py`)
- Simple 2-module cycle (A ↔ B)
- 3-module cycle (A → B → C → A)
- Longer cycles (4+ modules)
- Cycle with common dependency
- No false positive on diamond dependencies
- Cycle error message shows full path
- Cycles in lib/ folder
- Indirect cycle detection
- Multiple entry points without cycles

## Key Design Decisions

### 1. Deterministic Resolution
- Fixed search order with no fallbacks
- No environment-dependent behavior
- Errors are explicit and actionable

### 2. Early Cycle Detection
- Cycles detected during resolution, not during compilation
- Clear error messages with full cycle path
- Prevents wasting time on invalid module graphs

### 3. Resolution Stack vs. Resolved Modules
- **Resolution Stack**: Tracks modules currently being resolved (for cycle detection)
- **Resolved Modules**: Cache of fully resolved modules (for efficiency)
- Critical insight: Must check resolution stack BEFORE checking resolved cache to catch cycles

### 4. Topological Sort
- Orders modules so dependencies come before dependents
- Ensures correct compilation order
- Acts as a fallback cycle detector (though cycles should be caught earlier)

## Bug Fixes During Implementation

### Bug #1: Early Return in `_resolve_import`
**Problem**: The `_resolve_import` method had an early return if a module was already in `resolved_modules`, which bypassed the cycle detection in `_resolve_module_from_file`.

**Symptom**: Cycles like A → B → A were not detected because:
1. A starts resolving (added to stack)
2. A imports B (B starts resolving)
3. B imports A
4. `_resolve_import("a")` returned early because A was in `resolved_modules`
5. Cycle check never executed

**Fix**: Removed the early return from `_resolve_import`. All resolution paths now go through `_resolve_module_from_file`, which performs the cycle check.

**Code Change**:
```python
# BEFORE (incorrect)
def _resolve_import(self, module_name: str, from_file: Path):
    if module_name in self.resolved_modules:
        return self.resolved_modules[module_name]  # ← Bypasses cycle check!
    # ... find file and call _resolve_module_from_file

# AFTER (correct)
def _resolve_import(self, module_name: str, from_file: Path):
    # ... find file and call _resolve_module_from_file directly
```

## Testing Results

- **All 22 new linker tests**: ✅ Passing
- **All 105 existing tests**: ✅ Passing
- **Total**: 127/127 tests passing
- **Backward compatibility**: Fully maintained

## Usage Example

```python
from pathlib import Path
from ape.linker import Linker, LinkError

try:
    linker = Linker()
    program = linker.link(Path("main.ape"))
    
    # Access modules in dependency order
    for module in program.modules:
        print(f"Module: {module.module_name} from {module.file_path}")
    
    # Get dependency graph
    graph = linker.get_dependency_graph()
    for mod, deps in graph.items():
        print(f"{mod} depends on: {deps}")
        
except LinkError as e:
    print(f"Link error: {e}")
```

## Integration with Compilation Pipeline

```
Entry File (main.ape)
    ↓
Linker.link()
    ↓
LinkedProgram (modules in topological order)
    ↓
IR Builder (for each module in order)
    ↓
Semantic Validator
    ↓
Code Generator
    ↓
Output
```

## Compliance with Specification

The implementation fully complies with the specification in `docs/modules_and_imports.md`:

- ✅ Deterministic module resolution with fixed search order
- ✅ No ambiguous or environment-dependent resolution
- ✅ Circular dependency detection with clear error messages
- ✅ Dependency graph construction and topological ordering
- ✅ Support for lib/ folder for project libraries
- ✅ Support for ape_std/ standard library
- ✅ Hierarchical module paths (e.g., `strings.upper`)
- ✅ Graceful error handling with actionable messages
- ✅ Full backward compatibility with single-file programs

## Future Enhancements

Potential future improvements (not in scope for v0.2.0):

1. **Incremental Linking**: Cache resolved modules across invocations
2. **Parallel Resolution**: Resolve independent modules in parallel
3. **Import Aliases**: Support `import foo as bar` syntax
4. **Selective Imports**: Support `from foo import bar, baz` syntax
5. **Module Namespaces**: Full namespace management and symbol resolution
6. **Link-time Optimization**: Dead code elimination across modules

## Conclusion

The linker implementation provides a solid foundation for multi-file Ape programs with deterministic, predictable behavior. All requirements from the v0.2.0 specification have been met, and the implementation is fully tested with 100% backward compatibility.
