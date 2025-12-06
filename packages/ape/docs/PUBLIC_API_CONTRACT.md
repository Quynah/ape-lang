# APE v1.0 Public API Contract

**Status:** v1.0.0-ready  
**Stability:** Stable across 1.x releases  
**Last Updated:** December 6, 2025

This document defines the public API contract for APE v1.0.0 and establishes stability guarantees for the 1.x release series.

## API Stability Levels

APE components are marked with one of three stability levels:

### ✅ Public API (Stable)
- **Guarantee:** Will not break across 1.x releases
- **Changes:** Only additions (new functions, parameters with defaults)
- **Deprecation:** Minimum 1 minor version notice before removal
- **Semantic Versioning:** Breaking changes require 2.0.0

### ⚠️ Semi-Internal (Use with Caution)
- **Guarantee:** May change in minor releases with deprecation notice
- **Changes:** Refactoring, signature changes possible
- **Usage:** Advanced users only
- **Semantic Versioning:** Changes documented in CHANGELOG

### ❌ Internal Only (No Guarantees)
- **Guarantee:** None - may change without notice
- **Changes:** Any change allowed
- **Usage:** Do not import or depend on these
- **Semantic Versioning:** Not covered by semver

---

## ✅ PUBLIC API

These components are stable and will not break across 1.x releases.

### Core Compilation

```python
from ape import compile, validate, run
```

#### `compile(source_or_path: Union[str, Path]) -> ApeModule`
**Status:** ✅ Public API  
**Stability:** Stable

Compiles APE source code or file to executable module.

**Guarantees:**
- Function signature will not change
- Return type (`ApeModule`) interface stable
- Source code and file path inputs supported
- Raises `ApeCompileError` on failure

#### `validate(source_or_path: Union[str, Path]) -> bool`
**Status:** ✅ Public API  
**Stability:** Stable

Validates APE source code without compiling.

**Guarantees:**
- Returns `True` if valid, raises exception if invalid
- Raises `ApeValidationError` with semantic context

#### `run(source_or_path: Union[str, Path], context: Optional[Dict] = None) -> Any`
**Status:** ✅ Public API  
**Stability:** Stable

Executes APE source code directly.

**Guarantees:**
- Accepts optional context dictionary for initial variables
- Returns execution result
- Raises `ApeExecutionError` on runtime failure

### Runtime Execution

```python
from ape import ExecutionContext, RuntimeExecutor
```

#### `ExecutionContext`
**Status:** ✅ Public API  
**Stability:** Stable

Manages variable bindings and scope for execution.

**Public Methods:**
- `get(name: str) -> Any` - Get variable value
- `set(name: str, value: Any) -> None` - Set variable value
- `has(name: str) -> bool` - Check if variable exists
- `allow(capability: str) -> None` - Grant capability
- `has_capability(capability: str) -> bool` - Check capability
- `can_mutate() -> bool` - Check if mutations allowed (dry-run mode)
- `create_child_scope() -> ExecutionContext` - Create child scope

**Public Attributes:**
- `variables: Dict[str, Any]` - Current scope variables (read-only recommended)
- `dry_run: bool` - Whether in dry-run mode
- `capabilities: Set[str]` - Granted capabilities (read-only recommended)
- `max_iterations: int` - Safety limit for loops

**Guarantees:**
- Method signatures stable
- Attributes readable (writing discouraged but supported)
- Child scopes inherit parent settings

#### `RuntimeExecutor`
**Status:** ✅ Public API  
**Stability:** Stable

AST-based executor for APE programs.

**Constructor:**
```python
RuntimeExecutor(
    max_iterations: int = 10_000,
    trace: Optional[TraceCollector] = None,
    dry_run: bool = False
)
```

**Public Methods:**
- `execute(node: ASTNode, context: ExecutionContext) -> Any` - Execute AST node

**Guarantees:**
- Constructor signature stable (new parameters may be added with defaults)
- `execute()` method signature stable
- Deterministic behavior: same input → same output
- No side effects (filesystem, network, environment)

### Tracing & Observability

```python
from ape import TraceCollector, TraceEvent, ExplanationEngine, ReplayEngine
```

#### `TraceCollector`
**Status:** ✅ Public API  
**Stability:** Stable

Collects execution trace events.

**Public Methods:**
- `record(event: TraceEvent) -> None` - Record event
- `events() -> List[TraceEvent]` - Get all events
- `clear() -> None` - Clear all events
- `__len__() -> int` - Number of events
- `__bool__() -> bool` - Always True

**Guarantees:**
- Non-intrusive (no effect on execution)
- Shallow copy snapshots only
- Method signatures stable

#### `TraceEvent`
**Status:** ✅ Public API  
**Stability:** Stable

Single execution trace event (dataclass).

**Public Attributes:**
- `node_type: str` - AST node type
- `phase: Literal["enter", "exit"]` - Execution phase
- `context_snapshot: Dict[str, Any]` - Variable snapshot
- `result: Optional[Any]` - Result value (exit events)
- `metadata: Dict[str, Any]` - Additional data

**Guarantees:**
- Dataclass structure stable
- All attributes accessible
- New attributes may be added (non-breaking)

#### `ExplanationEngine`
**Status:** ✅ Public API  
**Stability:** Stable

Converts traces to human-readable explanations.

**Public Methods:**
- `from_trace(trace: TraceCollector) -> List[ExplanationStep]` - Generate explanations

**Guarantees:**
- Deterministic output for same trace
- No LLM or randomness
- Method signature stable

#### `ExplanationStep`
**Status:** ✅ Public API  
**Stability:** Stable

Single explanation step (dataclass).

**Public Attributes:**
- `index: int` - Step number
- `node_type: str` - AST node type
- `summary: str` - Human-readable summary
- `details: Dict[str, Any]` - Additional information

**Guarantees:**
- Dataclass structure stable
- Summary format may improve (non-breaking)

#### `ReplayEngine`
**Status:** ✅ Public API  
**Stability:** Stable

Validates deterministic execution.

**Public Methods:**
- `replay(trace: TraceCollector) -> TraceCollector` - Validate trace
- `validate_determinism(trace1, trace2) -> bool` - Compare traces

**Guarantees:**
- Does not re-execute code
- Validates structure only
- Method signatures stable

### Runtime Profiles

```python
from ape import RUNTIME_PROFILES, get_profile, list_profiles, create_context_from_profile
```

#### `RUNTIME_PROFILES: Dict[str, Dict[str, Any]]`
**Status:** ✅ Public API  
**Stability:** Stable

Built-in profile configurations.

**Profiles:**
- `analysis` - Dry-run + tracing, no capabilities
- `execution` - Full execution, all capabilities
- `audit` - Dry-run + tracing + all capabilities
- `debug` - Execution + tracing, lower iteration limit
- `test` - Limited capabilities (io.stdout only)

**Guarantees:**
- Built-in profiles will not be removed
- Profile structure keys stable
- New profiles may be added

#### `get_profile(name: str) -> Dict[str, Any]`
**Status:** ✅ Public API  
**Stability:** Stable

Get profile configuration by name.

**Guarantees:**
- Returns dictionary with profile settings
- Raises `ProfileError` if not found

#### `list_profiles() -> List[str]`
**Status:** ✅ Public API  
**Stability:** Stable

List all available profile names.

#### `create_context_from_profile(profile_name: str) -> ExecutionContext`
**Status:** ✅ Public API  
**Stability:** Stable

Create execution context from profile.

**Guarantees:**
- Returns configured `ExecutionContext`
- Applies profile settings (dry_run, capabilities)

### Error Hierarchy

```python
from ape import (
    ApeError,
    ParseError,
    RuntimeExecutionError,
    CapabilityError,
    ReplayError,
    ValidationError,
    LinkerError,
    ProfileError,
)
```

All errors inherit from `ApeError` and provide semantic context.

#### `ApeError`
**Status:** ✅ Public API  
**Stability:** Stable

Base class for all APE errors.

**Public Attributes:**
- `message: str` - Error message
- `context: ErrorContext` - Semantic context

**Public Methods:**
- `to_dict() -> Dict[str, Any]` - Serialize error

**Guarantees:**
- All APE errors inherit from this
- Attributes stable
- No Python stacktraces exposed to users

#### Specific Error Types

All error types are **✅ Public API** and **Stable**:

- **`ParseError`** - Source parsing failed
- **`RuntimeExecutionError`** - Execution failed (includes `ExecutionError`, `MaxIterationsExceeded`)
- **`CapabilityError`** - Required capability not granted
- **`ReplayError`** - Trace replay validation failed
- **`ValidationError`** - Semantic validation failed
- **`LinkerError`** - Module linking failed
- **`ProfileError`** - Profile configuration invalid

**Guarantees:**
- Constructor signatures stable
- Context information provided
- Raised consistently across 1.x

---

## ⚠️ SEMI-INTERNAL API

These components may change in minor releases with deprecation notice.

### AST Nodes

```python
from ape.parser.ast_nodes import ASTNode, IfNode, WhileNode, ForNode
```

**Status:** ⚠️ Semi-Internal  
**Stability:** May change in minor releases

AST node structure for advanced users.

**Usage Guidelines:**
- Read-only recommended
- Traversal patterns may change
- Use `RuntimeExecutor` instead of direct manipulation

**Changes Allowed:**
- New node types
- New attributes (with defaults)
- Internal refactoring

**Deprecation:** 1 minor version notice

### Code Generation

```python
from ape.codegen.python_codegen import PythonCodeGenerator
```

**Status:** ⚠️ Semi-Internal  
**Stability:** May change in minor releases

Generates Python code from APE AST.

**Usage Guidelines:**
- Use `compile()` instead for normal workflows
- Generated code format may change
- Internal optimizations may affect output

**Changes Allowed:**
- Output format changes
- New generation strategies
- Performance improvements

**Deprecation:** 1 minor version notice

### Semantic Validation

```python
from ape.compiler.semantic_validator import SemanticValidator
```

**Status:** ⚠️ Semi-Internal  
**Stability:** May change in minor releases

Validates APE semantics.

**Usage Guidelines:**
- Use `validate()` instead for normal workflows
- Validation rules may be added/refined
- Error messages may change

---

## ❌ INTERNAL API

These components have no stability guarantees. Do not depend on them.

### Internal Modules

- `ape.lexer.*` - Tokenization internals
- `ape.parser.parser` - Parser implementation
- `ape.compiler.ir_builder` - IR construction
- `ape.linker.*` - Module resolution internals
- `ape.runtime.core` - Python module integration internals

**Status:** ❌ Internal Only  
**Stability:** None

**Changes Allowed:**
- Any change without notice
- Refactoring, removal, replacement
- Not covered by semver

**Recommendation:** Do not import or depend on these modules.

---

## What Can Change in 1.x?

### ✅ Allowed (Non-Breaking)
- New functions/methods
- New optional parameters (with defaults)
- New error types (subclasses)
- Performance improvements
- Bug fixes
- Documentation clarifications
- New profiles or capabilities
- Internal refactoring

### ❌ Not Allowed (Breaking Changes)
- Removing public functions/methods
- Changing public method signatures (without deprecation)
- Removing public attributes
- Changing error inheritance hierarchy
- Changing deterministic behavior
- Removing built-in profiles

### Deprecation Process

1. **Announce:** Add deprecation warning in code + CHANGELOG
2. **Grace Period:** Minimum 1 minor version (e.g., 1.2 → 1.3)
3. **Remove:** In next major version (2.0.0)

Example:
```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated, use new_function() instead. "
        "Will be removed in 2.0.0",
        DeprecationWarning,
        stacklevel=2
    )
```

---

## What Is Experimental?

Currently, **no features are marked experimental**. All public API is stable for 1.0.0.

Future experimental features will be:
- Clearly marked in documentation
- Separate from stable API
- Subject to change without major version bump
- Typically in separate modules (e.g., `ape.experimental.*`)

---

## Backwards Compatibility Promise

### v1.x Guarantee

All code using **✅ Public API** will continue to work across v1.x releases without modification.

**Example:**
```python
# This code will work in 1.0.0, 1.5.0, 1.9.0
from ape import compile, ExecutionContext, RuntimeExecutor, TraceCollector

module = compile("my_code.ape")
context = ExecutionContext()
executor = RuntimeExecutor(trace=TraceCollector())
result = executor.execute(module.ast, context)
```

### Migration to 2.0.0

Breaking changes will only occur in major version bumps (2.0.0, 3.0.0, etc.).

**Process:**
1. Deprecation warnings in 1.x
2. Migration guide published
3. Minimum 3 months notice
4. Clear changelog in 2.0.0

---

## API Evolution Strategy

### Adding Features

New features follow this pattern:

1. **Research** - Design and prototype
2. **Experimental** - Release in separate module with warnings
3. **Beta** - Move to public API with "beta" suffix
4. **Stable** - Remove suffix, full v1.x guarantee

### Refactoring

Internal refactoring must maintain public API compatibility:

1. **Create new implementation** - Keep old as wrapper
2. **Deprecate old** - Add warnings
3. **Grace period** - Wait 1+ minor versions
4. **Remove** - In major version bump

---

## How to Check API Stability

### In Documentation

Look for stability markers:
- **✅ Public API** - Stable, use freely
- **⚠️ Semi-Internal** - Use with caution
- **❌ Internal** - Do not use

### In Code

Public API is exported from top-level:
```python
from ape import *  # Only public API exported
```

Semi-internal requires deeper imports:
```python
from ape.parser.ast_nodes import IfNode  # Semi-internal
```

Internal requires direct module access:
```python
from ape.lexer.tokenizer import Token  # Internal only
```

---

## Questions & Clarifications

**Q: Can I depend on AST node structure?**  
A: ⚠️ Semi-internal - structure may change with deprecation notice. Use `RuntimeExecutor` instead.

**Q: Will trace event format change?**  
A: ✅ No breaking changes. New fields may be added, but existing fields stable.

**Q: Can I create custom profiles?**  
A: ✅ Yes, use `register_profile()` - fully supported and stable.

**Q: Will error messages change?**  
A: Message text may improve, but error types and attributes stable.

**Q: Is Python code generation output stable?**  
A: ⚠️ No - generated code format may change. Use as compilation target only.

---

## References

- [APE_1.0_SPECIFICATION.md](APE_1.0_SPECIFICATION.md) - Language specification
- [RELEASE_GOVERNANCE.md](RELEASE_GOVERNANCE.md) - Release process and semver
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

**Last Updated:** December 6, 2025  
**Valid For:** APE v1.0.0 and all v1.x releases  
**Status:** Stable - This contract will not change within 1.x
