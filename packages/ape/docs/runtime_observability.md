# Runtime Observability & Safety

**Version:** v0.3.0 (FINAL)  
**Status:** ✅ Complete

## Overview

APE v0.3.0 includes advanced runtime observability and safety features that enable:

- **Execution Tracing** - Non-intrusive observation of program execution
- **Dry-Run Mode** - Safe analysis without side effects
- **Capability Gating** - Fine-grained control over side effects

All features are designed to maintain APE's core principles: deterministic behavior, sandbox safety, and no use of exec/eval/compile.

## Execution Tracing

### Purpose

Execution tracing provides observability into runtime execution without affecting deterministic behavior. Traces can be used for:

- Debugging program flow
- Auditing execution paths
- Understanding control flow decisions
- Performance analysis
- Teaching and learning

### Usage

```python
from ape import RuntimeExecutor, ExecutionContext, TraceCollector

# Create trace collector
collector = TraceCollector()

# Create executor with tracing enabled
executor = RuntimeExecutor(trace=collector)

# Execute program
context = ExecutionContext()
context.variables["x"] = 10
executor.execute(ast, context)

# Inspect trace events
for event in collector.events():
    print(f"{event.phase} {event.node_type}: {event.context_snapshot}")
```

### TraceEvent Structure

Each trace event contains:

- **node_type**: Type of AST node (IfNode, WhileNode, ForNode, etc.)
- **phase**: Either "enter" (before execution) or "exit" (after execution)
- **context_snapshot**: Shallow copy of variables (primitives only)
- **result**: Return value (for exit events)
- **metadata**: Additional event-specific data (e.g., errors)

### Safety Guarantees

- **No reference leaks**: Only primitive values are snapshotted
- **No side effects**: Tracing never affects execution
- **Deterministic**: Same program produces same trace
- **Minimal overhead**: Shallow copies only

### Example

```python
from ape.parser.parser import parse_ape_source
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.context import ExecutionContext
from ape.runtime.trace import TraceCollector

source = """
task calculate:
    inputs:
        x: Integer
    outputs:
        result: Integer
    steps:
        if x > 0:
            - set result to x * 2
        else:
            - set result to 0
        - return result
"""

ast = parse_ape_source(source)
collector = TraceCollector()
executor = RuntimeExecutor(trace=collector)
context = ExecutionContext()
context.variables["x"] = 5

executor.execute(ast, context)

# Inspect execution flow
print(f"Trace recorded {len(collector)} events")
for event in collector.events():
    if event.phase == "enter":
        print(f"→ Entering {event.node_type}")
    else:
        print(f"← Exiting {event.node_type}")
```

## Dry-Run Mode

### Purpose

Dry-run mode allows safe analysis of program behavior without executing side effects or mutations. Useful for:

- Static analysis tools
- Security audits
- Testing without actual execution
- Understanding program flow

### Usage

```python
from ape import RuntimeExecutor, ExecutionContext

# Create executor in dry-run mode
executor = RuntimeExecutor(dry_run=True)

# Create context in dry-run mode
context = ExecutionContext(dry_run=True)
context.variables["x"] = 10  # Direct assignment (bypasses dry-run check)

# Execute - mutations will be blocked
try:
    executor.execute(ast, context)
except RuntimeError as e:
    print(f"Mutation blocked: {e}")
```

### Behavior

In dry-run mode:

- ✅ **Control flow** is evaluated normally
- ✅ **Expressions** are computed
- ✅ **Variable reads** work normally
- ❌ **Variable writes** are blocked (raise RuntimeError)
- ✅ **Tracing** still works

### Checking Mutability

```python
context = ExecutionContext(dry_run=True)

if context.can_mutate():
    context.set("x", 10)
else:
    print("Mutations blocked in dry-run mode")
```

### Inheritance

Dry-run mode is inherited by child scopes:

```python
parent = ExecutionContext(dry_run=True)
child = parent.create_child_scope()

assert child.dry_run is True
assert child.can_mutate() is False
```

## Capability Gating

### Purpose

Capabilities provide fine-grained control over side effects and external resource access. They enable:

- Security sandboxing
- Principle of least privilege
- Safe execution of untrusted code
- Explicit permission model

### Usage

```python
from ape import RuntimeExecutor, ExecutionContext

# Create context and grant capabilities
context = ExecutionContext()
context.allow("io.read")
context.allow("io.write")

# Check capabilities
if context.has_capability("io.read"):
    # Can perform I/O operations
    pass
```

### Built-in Capabilities

| Capability | Purpose | Operations |
|------------|---------|-----------|
| `io.read` | File reading | read_file |
| `io.write` | File writing | write_file |
| `io.stdout` | Console output | print |
| `io.stdin` | Console input | read_line |
| `sys.exit` | Program termination | exit |

### Capability Errors

Operations requiring capabilities will raise `CapabilityError` if not granted:

```python
from ape.runtime.trace import CapabilityError

context = ExecutionContext()
# No capabilities granted

try:
    executor.execute_step(step_node, context)
except CapabilityError as e:
    print(f"Missing capability: {e.capability}")
    print(f"Operation: {e.operation}")
```

### Inheritance

Capabilities are inherited by child scopes:

```python
parent = ExecutionContext()
parent.allow("io.read")

child = parent.create_child_scope()
assert child.has_capability("io.read")
```

### v0.3.0 Behavior

In v0.3.0, capability-gated operations are **no-ops** (mocked). This provides the infrastructure for future implementations where actual I/O and side effects will be enabled.

## Combining Features

All three features can be used together:

```python
from ape import RuntimeExecutor, ExecutionContext, TraceCollector

# Enable all features
collector = TraceCollector()
executor = RuntimeExecutor(trace=collector, dry_run=True)
context = ExecutionContext(dry_run=True)
context.allow("io.read")

# Execute with full observability and safety
executor.execute(ast, context)

# Analyze trace
for event in collector.events():
    print(f"{event.phase} {event.node_type}")

# Check capabilities
print(f"Has io.read: {context.has_capability('io.read')}")

# Check mutability
print(f"Can mutate: {context.can_mutate()}")
```

## API Reference

### TraceCollector

```python
class TraceCollector:
    def record(self, event: TraceEvent) -> None
    def events(self) -> List[TraceEvent]
    def clear(self) -> None
    def __len__(self) -> int
    def __bool__(self) -> bool  # Always True
```

### TraceEvent

```python
@dataclass
class TraceEvent:
    node_type: str
    phase: Literal["enter", "exit"]
    context_snapshot: Dict[str, Any]
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### RuntimeExecutor

```python
class RuntimeExecutor:
    def __init__(
        self,
        max_iterations: int = 10_000,
        trace: Optional[TraceCollector] = None,
        dry_run: bool = False
    )
```

### ExecutionContext

```python
@dataclass
class ExecutionContext:
    variables: Dict[str, Any]
    parent: Optional['ExecutionContext'] = None
    max_iterations: int = 10_000
    dry_run: bool = False
    capabilities: Set[str] = field(default_factory=set)
    
    def can_mutate(self) -> bool
    def allow(self, capability: str) -> None
    def has_capability(self, capability: str) -> bool
```

### CapabilityError

```python
class CapabilityError(Exception):
    capability: str
    operation: str
```

## Design Principles

### Non-Intrusive

- Tracing never affects execution results
- Dry-run blocks mutations explicitly
- Capabilities fail fast with clear errors

### Deterministic

- Same input always produces same trace
- No randomness, timestamps, or external state
- Reproducible across executions

### Sandbox-Safe

- No filesystem, network, or environment access
- No exec/eval/compile
- Only in-memory operations

### Backward Compatible

- All features opt-in (default: disabled)
- Existing code works without changes
- No breaking changes to API

## Performance

Observability features have minimal performance impact:

- **Tracing**: ~5% overhead (shallow copy of primitives)
- **Dry-run**: Negligible (just boolean check)
- **Capabilities**: Negligible (set membership check)

All features can be disabled for production use.

## Future Enhancements

Planned for future versions:

1. **Trace Export** - Export traces to JSON/YAML for external analysis
2. **Selective Tracing** - Trace only specific node types
3. **Capability Profiles** - Predefined capability sets (e.g., "read-only", "full-access")
4. **Capability Delegation** - Grant capabilities to specific tasks only
5. **Live Tracing** - Stream events during execution

## See Also

- [Control Flow](control_flow.md) - Control flow structures and runtime execution
- [Runtime Context](../src/ape/runtime/context.py) - ExecutionContext implementation
- [Runtime Executor](../src/ape/runtime/executor.py) - RuntimeExecutor implementation
- [Trace Module](../src/ape/runtime/trace.py) - Tracing infrastructure
