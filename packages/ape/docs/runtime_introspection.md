# APE Runtime Introspection Layer

**Version:** 0.3.x-dev  
**Status:** Development  
**Date:** December 2025

This document describes APE's Runtime Introspection Layer, which extends the v0.3.0 FINAL runtime with explanation, replay, and profile capabilities for explainable and reproducible execution.

## Overview

The Runtime Introspection Layer builds on APE's existing tracing infrastructure to provide three key capabilities:

1. **Explanation Engine** - Converts execution traces into human-readable explanations
2. **Replay Engine** - Validates deterministic execution through trace replay
3. **Runtime Profiles** - Predefined configurations for common use cases

### Design Principles

- **No new language features** - Pure runtime extensions
- **No parser/AST changes** - Only works with existing trace infrastructure
- **Fully deterministic** - No LLM, no randomness, no side effects
- **Backwards compatible** - All features are opt-in
- **No execution** - Replay validates traces without re-executing code

## Explanation Engine

The `ExplanationEngine` converts low-level `TraceEvent` objects into high-level `ExplanationStep` objects with human-readable summaries.

### Core Concepts

**ExplanationStep** - A single step in the execution explanation:
```python
@dataclass
class ExplanationStep:
    index: int                    # Step number (0-indexed)
    node_type: str                # AST node type (IF, WHILE, FOR, etc.)
    summary: str                  # Human-readable one-line summary
    details: Dict[str, Any]       # Structured additional information
```

**ExplanationEngine** - Generates explanations from traces:
```python
class ExplanationEngine:
    def from_trace(self, trace: TraceCollector) -> List[ExplanationStep]:
        """Convert trace events to human-readable explanations"""
```

### Example Usage

```python
from ape import RuntimeExecutor, ExecutionContext, TraceCollector, ExplanationEngine

# Execute with tracing
trace = TraceCollector()
executor = RuntimeExecutor(trace=trace)
context = ExecutionContext()
executor.execute(ast, context)

# Generate explanations
explainer = ExplanationEngine()
explanations = explainer.from_trace(trace)

# Print human-readable output
for step in explanations:
    print(f"Step {step.index}: {step.summary}")
```

### Explanation Examples

#### IF Statement
**Trace Event:**
```python
TraceEvent(
    node_type="IF",
    phase="enter",
    context_snapshot={"x": 5},
    metadata={"condition_result": True, "branch_taken": "then"}
)
```

**Explanation:**
```
"Condition evaluated to true → entered then branch"
```

#### WHILE Loop
**Trace Event:**
```python
TraceEvent(
    node_type="WHILE",
    phase="enter",
    context_snapshot={"i": 0},
    metadata={"iterations": 3, "final_condition_result": False}
)
```

**Explanation:**
```
"Loop terminated after 3 iterations (condition became false)"
```

#### FOR Loop
**Trace Event:**
```python
TraceEvent(
    node_type="FOR",
    phase="enter",
    context_snapshot={},
    metadata={"collection_size": 5, "loop_var": "item", "iterations": 2}
)
```

**Explanation:**
```
"Iterating over collection of 5 items (iteration 2)"
```

#### Assignment (Dry-Run)
**Trace Event:**
```python
TraceEvent(
    node_type="EXPRESSION",
    phase="enter",
    context_snapshot={"x": 5},
    metadata={"variable": "y", "dry_run": True}
)
```

**Explanation:**
```
"Variable 'y' would be set to 10 (dry-run)"
```

### Supported Node Types

The ExplanationEngine provides context-aware explanations for:

- **IF** - Condition evaluation and branch selection
- **WHILE** - Loop iterations and termination
- **FOR** - Collection iteration
- **STEP** - Step execution (with dry-run awareness)
- **EXPRESSION** - Variable assignment
- **MODULE/TASKDEF/FLOWDEF** - Definition nodes
- **Generic** - Fallback for unknown nodes

## Replay Engine

The `ReplayEngine` validates deterministic execution by replaying trace events without re-executing code.

### Core Concepts

**ReplayEngine** - Validates trace structure:
```python
class ReplayEngine:
    def replay(self, trace: TraceCollector) -> TraceCollector:
        """Validate and replay trace events"""
    
    def validate_determinism(self, trace1: TraceCollector, trace2: TraceCollector) -> bool:
        """Validate two traces are deterministically equivalent"""
```

**ReplayError** - Raised when replay validation fails:
```python
class ReplayError(Exception):
    """Indicates non-deterministic behavior or corrupted trace"""
```

### What Replay Validates

1. **Enter/Exit Symmetry** - Every enter has a matching exit
2. **Node Type Consistency** - Exit matches enter node type
3. **Proper Nesting** - Events nest correctly (stack discipline)
4. **Context Integrity** - Snapshots have valid types

### What Replay Does NOT Do

- ❌ Re-execute code
- ❌ Modify state
- ❌ Perform calculations
- ❌ Access external resources

Replay is **validation**, not execution.

### Example Usage

```python
from ape import ReplayEngine, TraceCollector

# Original execution produced trace1
trace1 = execute_with_tracing(ast, context)

# Replay validates structure
replayer = ReplayEngine()
try:
    replayed = replayer.replay(trace1)
    print("✓ Trace is valid and deterministic")
except ReplayError as e:
    print(f"✗ Trace validation failed: {e}")
```

### Determinism Validation

Compare two traces from separate executions:

```python
# Execute twice
trace1 = execute_with_tracing(ast, context1)
trace2 = execute_with_tracing(ast, context2)

# Validate determinism
replayer = ReplayEngine()
try:
    replayer.validate_determinism(trace1, trace2)
    print("✓ Execution is deterministic")
except ReplayError as e:
    print(f"✗ Non-deterministic behavior: {e}")
```

### Error Examples

**Unclosed Events:**
```python
trace.record(TraceEvent("IF", "enter", {...}))
# Missing exit event

replayer.replay(trace)
# ReplayError: Unclosed events at end of trace: ['IF']
```

**Mismatched Enter/Exit:**
```python
trace.record(TraceEvent("IF", "enter", {...}))
trace.record(TraceEvent("WHILE", "exit", {...}))  # Wrong type

replayer.replay(trace)
# ReplayError: Exit event node_type mismatch: expected IF, got WHILE
```

**Exit Without Enter:**
```python
trace.record(TraceEvent("IF", "exit", {...}))  # No enter

replayer.replay(trace)
# ReplayError: Exit event for IF without matching enter
```

## Runtime Profiles

Runtime Profiles are predefined configurations that combine dry-run, tracing, and capability settings for common use cases.

### Built-in Profiles

| Profile | Description | Dry-Run | Tracing | Capabilities |
|---------|-------------|---------|---------|--------------|
| **analysis** | Safe analysis mode | ✓ Yes | ✓ Yes | None |
| **execution** | Full execution mode | ✗ No | ✗ No | All (*) |
| **audit** | Audit mode | ✓ Yes | ✓ Yes | All (*) |
| **debug** | Debug mode | ✗ No | ✓ Yes | All (*) |
| **test** | Test mode | ✗ No | ✓ Yes | io.stdout only |

### Profile API

```python
from ape.runtime.profile import (
    get_profile,
    list_profiles,
    create_context_from_profile,
    create_executor_config_from_profile,
)

# List available profiles
profiles = list_profiles()
# ['analysis', 'execution', 'audit', 'debug', 'test']

# Get profile configuration
config = get_profile("analysis")
# {'dry_run': True, 'tracing': True, 'capabilities': [], ...}

# Create context from profile
context = create_context_from_profile("analysis")
# ExecutionContext with dry_run=True, no capabilities

# Create executor config from profile
executor_config = create_executor_config_from_profile("debug")
executor = RuntimeExecutor(**executor_config)
```

### Profile Use Cases

#### Analysis Profile
**Use when:** Analyzing code structure without execution  
**Ideal for:** Static analysis, code review, learning

```python
context = create_context_from_profile("analysis")
executor = RuntimeExecutor(dry_run=True, trace=TraceCollector())

# Analyze without mutations
executor.execute(ast, context)
```

#### Execution Profile
**Use when:** Running production code  
**Ideal for:** Normal execution, deployed code

```python
context = create_context_from_profile("execution")
executor = RuntimeExecutor()

# Full execution with all capabilities
executor.execute(ast, context)
```

#### Audit Profile
**Use when:** Auditing code with full trace  
**Ideal for:** Compliance, security review, governance

```python
context = create_context_from_profile("audit")
executor_config = create_executor_config_from_profile("audit")
executor = RuntimeExecutor(**executor_config)

# Dry-run with full trace and all capabilities checked
executor.execute(ast, context)
```

#### Debug Profile
**Use when:** Debugging with lower iteration limits  
**Ideal for:** Development, troubleshooting

```python
executor_config = create_executor_config_from_profile("debug")
executor = RuntimeExecutor(**executor_config)
# max_iterations=1000, tracing enabled
```

#### Test Profile
**Use when:** Running tests with limited capabilities  
**Ideal for:** Unit tests, CI/CD

```python
context = create_context_from_profile("test")
# Only io.stdout capability granted
```

### Custom Profiles

Register your own profiles:

```python
from ape.runtime.profile import register_profile

custom = {
    "description": "Custom strict mode",
    "dry_run": False,
    "tracing": True,
    "capabilities": ["io.stdout"],
    "max_iterations": 500
}

register_profile("strict", custom)

# Now use it
context = create_context_from_profile("strict")
```

## Complete Example

Here's a complete example showing all three introspection features:

```python
from ape import (
    RuntimeExecutor,
    ExecutionContext,
    TraceCollector,
    ExplanationEngine,
    ReplayEngine,
    create_context_from_profile,
    create_executor_config_from_profile,
)

# Example APE code (parsed to AST)
# if x > 5:
#     y = x * 2
# else:
#     y = x + 2

# 1. Execute with audit profile (dry-run + tracing + all capabilities)
context = create_context_from_profile("audit")
executor_config = create_executor_config_from_profile("audit")
executor = RuntimeExecutor(**executor_config)

# Set initial values
context.set("x", 10)

# Execute (dry-run, so no mutations)
executor.execute(ast, context)

# 2. Explain execution
explainer = ExplanationEngine()
explanations = explainer.from_trace(executor.trace)

print("Execution Explanation:")
for step in explanations:
    print(f"  {step.index}. {step.summary}")
    if step.details.get("dry_run"):
        print(f"     (dry-run mode - no actual mutations)")

# Output:
# Execution Explanation:
#   0. Condition evaluated to true → entered then branch
#      (dry-run mode - no actual mutations)
#   1. Variable 'y' would be set to 20 (dry-run)
#      (dry-run mode - no actual mutations)

# 3. Replay and validate
replayer = ReplayEngine()
try:
    replayed = replayer.replay(executor.trace)
    print(f"✓ Trace validated: {len(replayed)} events")
except ReplayError as e:
    print(f"✗ Validation failed: {e}")

# 4. Compare with second execution (determinism check)
executor2 = RuntimeExecutor(**executor_config)
context2 = create_context_from_profile("audit")
context2.set("x", 10)
executor2.execute(ast, context2)

try:
    replayer.validate_determinism(executor.trace, executor2.trace)
    print("✓ Execution is deterministic")
except ReplayError as e:
    print(f"✗ Non-deterministic: {e}")
```

## API Reference

### ExplanationEngine

```python
class ExplanationEngine:
    def __init__(self) -> None:
        """Initialize explanation engine"""
    
    def from_trace(self, trace: TraceCollector) -> List[ExplanationStep]:
        """Generate explanations from trace events"""
```

### ExplanationStep

```python
@dataclass
class ExplanationStep:
    index: int                    # Step number (0-indexed)
    node_type: str                # AST node type
    summary: str                  # Human-readable summary
    details: Dict[str, Any]       # Additional information
```

### ReplayEngine

```python
class ReplayEngine:
    def __init__(self) -> None:
        """Initialize replay engine"""
    
    def replay(self, trace: TraceCollector) -> TraceCollector:
        """Validate and replay trace"""
    
    def validate_determinism(
        self, 
        trace1: TraceCollector, 
        trace2: TraceCollector
    ) -> bool:
        """Validate two traces are deterministically equivalent"""
```

### ReplayError

```python
class ReplayError(Exception):
    """Raised when replay validation fails"""
    
    def __init__(
        self, 
        message: str, 
        expected: Optional[TraceEvent] = None,
        actual: Optional[TraceEvent] = None
    ):
        """Initialize with failure details"""
```

### Profile Functions

```python
def get_profile(name: str) -> Dict[str, Any]:
    """Get profile configuration by name"""

def list_profiles() -> List[str]:
    """List all available profile names"""

def get_profile_description(profile_name: str) -> str:
    """Get human-readable profile description"""

def create_context_from_profile(profile_name: str) -> ExecutionContext:
    """Create ExecutionContext from profile"""

def create_executor_config_from_profile(profile_name: str) -> Dict[str, Any]:
    """Create RuntimeExecutor config from profile"""

def validate_profile(profile_config: Dict[str, Any]) -> None:
    """Validate profile configuration structure"""

def register_profile(name: str, config: Dict[str, Any]) -> None:
    """Register custom profile"""
```

### ProfileError

```python
class ProfileError(Exception):
    """Raised when profile configuration is invalid"""
```

## Implementation Details

### Explanation Algorithm

1. **Event Pairing** - Match enter/exit events
2. **Node Dispatch** - Route to node-specific explainer
3. **Summary Generation** - Create human-readable text
4. **Detail Collection** - Gather structured metadata

### Replay Validation

1. **Stack Tracking** - Maintain enter/exit stack
2. **Symmetry Check** - Validate every enter has exit
3. **Type Validation** - Ensure matching node types
4. **Context Validation** - Check snapshot integrity

### Profile Resolution

1. **Lookup** - Find profile by name
2. **Context Creation** - Build ExecutionContext with flags
3. **Capability Grant** - Apply capability rules
4. **Executor Config** - Generate RuntimeExecutor kwargs

## Comparison with Tracing

| Feature | Tracing | Explanation | Replay |
|---------|---------|-------------|--------|
| **Output** | TraceEvent objects | Human text | Validated trace |
| **Audience** | Developers | All users | Systems |
| **Purpose** | Debugging | Understanding | Validation |
| **Format** | Structured data | Natural language | Pass/fail |
| **Execution** | Records during run | Post-processing | Post-processing |

All three work together:
1. **Tracing** captures execution
2. **Explanation** makes it readable
3. **Replay** validates correctness

## Design Constraints

Following the v0.3.x-dev requirements:

- ✅ No parser or AST changes
- ✅ No exec/eval/compile
- ✅ No IO/filesystem/network/time/random
- ✅ No new runtime flags that change behavior implicitly
- ✅ Only extensions on tracing + executor
- ✅ Backwards compatible
- ✅ Version stays 0.3.0 (dev work)

## Testing

The introspection layer includes 35 comprehensive tests:

- **ExplanationEngine**: 9 tests
  - Empty trace handling
  - IF/WHILE/FOR explanations
  - Dry-run awareness
  - Multiple event sequences

- **ReplayEngine**: 10 tests
  - Empty trace handling
  - Valid enter/exit pairing
  - Nested event validation
  - Mismatch detection
  - Determinism validation

- **Runtime Profiles**: 14 tests
  - Profile listing and retrieval
  - Context/executor creation
  - Profile validation
  - Custom profile registration

- **Integration**: 2 tests
  - Complete workflow (trace → explain → replay)
  - Profile + executor integration

All tests pass alongside existing 230 tests (total: 265 tests).

## Future Extensions

Potential future work (not in scope for v0.3.x-dev):

- **Trace Export** - Export traces to JSON/XML for external tools
- **Explanation Templates** - Customizable explanation formats
- **Replay Modes** - Interactive replay, step-by-step debugging
- **Profile Inheritance** - Hierarchical profile composition
- **Performance Profiling** - Execution time analysis

## References

- [Runtime Observability](runtime_observability.md) - v0.3.0 FINAL tracing/dry-run/capabilities
- [Control Flow Implementation](../CONTROL_FLOW_IMPLEMENTATION.md) - v0.3.0 control flow
- [APE Specification](../spec/APE_Spec_v0.1.md) - Language specification

## Changelog

### v0.3.x-dev (December 2025)
- Added ExplanationEngine for human-readable trace interpretation
- Added ReplayEngine for deterministic validation
- Added Runtime Profiles (analysis, execution, audit, debug, test)
- Added 35 comprehensive tests
- All 265 tests passing (230 existing + 35 new)

---

**Status:** Complete and tested  
**Tests:** 35 new tests, all passing  
**Total Tests:** 265 (230 + 35)  
**Compatibility:** Backwards compatible with v0.3.0 FINAL
