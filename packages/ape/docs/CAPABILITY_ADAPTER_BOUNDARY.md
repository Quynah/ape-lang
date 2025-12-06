# APE Capability & Adapter Boundary

**Version:** 1.0.0  
**Status:** Architectural Specification  
**Last Updated:** December 6, 2025

This document defines the hard boundary between APE's side-effect-free runtime core and external adapters that implement actual side effects.

## Philosophy

**Core Principle:** APE runtime never performs side effects. It only declares intent through capabilities.

```
┌─────────────────────────────────────────────────────────┐
│  APE RUNTIME (Side-Effect Free)                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  • Parses code                                    │  │
│  │  • Validates semantics                            │  │
│  │  • Executes control flow                          │  │
│  │  • Tracks execution (tracing)                     │  │
│  │  • Declares intent (capabilities)                 │  │
│  │  • ❌ NO actual IO                                │  │
│  │  • ❌ NO filesystem access                        │  │
│  │  • ❌ NO network access                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Capability Check
                            ▼
┌─────────────────────────────────────────────────────────┐
│  ADAPTERS (External, Optional, Replaceable)             │
│  ┌───────────────────────────────────────────────────┐  │
│  │  • Implement actual side effects                  │  │
│  │  • Respect capability boundaries                  │  │
│  │  • Pluggable & replaceable                        │  │
│  │  • NOT part of core APE                           │  │
│  └───────────────────────────────────────────────────┘  │
│  Examples:                                               │
│  • FileSystemAdapter                                     │
│  • NetworkAdapter                                        │
│  • DatabaseAdapter                                       │
│  • UserInputAdapter                                      │
└─────────────────────────────────────────────────────────┘
```

---

## What Are Capabilities?

**Capabilities are names (strings) that represent intent, not implementation.**

### Properties of Capabilities

1. **Declarative** - State what you want to do, not how
2. **Permission-based** - Must be explicitly granted
3. **Traceable** - Can be recorded in execution traces
4. **Gated** - Checked before operation attempts
5. **No-op by default** - Missing capability = operation skipped or error raised

### Built-in Capabilities (v1.0)

| Capability | Intent | APE Runtime Behavior |
|------------|--------|----------------------|
| `io.read` | Read external input | Raises `CapabilityError` if not granted |
| `io.write` | Write external output | Raises `CapabilityError` if not granted |
| `io.stdout` | Write to standard output | Raises `CapabilityError` if not granted |
| `io.stdin` | Read from standard input | Raises `CapabilityError` if not granted |
| `sys.exit` | Terminate execution | Raises `CapabilityError` if not granted |

**Important:** APE runtime **validates** these capabilities but **does not implement** the actual operations.

### Example

```python
from ape import ExecutionContext, CapabilityError

context = ExecutionContext()

# Without capability - would raise CapabilityError
try:
    if not context.has_capability('io.write'):
        raise CapabilityError('io.write', 'write_file')
except CapabilityError as e:
    print(f"Blocked: {e.message}")

# With capability - intent declared, but no actual IO performed
context.allow('io.write')
print(f"Capability granted: {context.has_capability('io.write')}")
# Runtime stops here - actual IO requires adapter
```

---

## APE Runtime: What It Does

### ✅ Runtime Responsibilities

1. **Parse & Validate** - Ensure code is syntactically and semantically valid
2. **Execute Control Flow** - Run if/while/for without side effects
3. **Manage Scope** - Variable bindings in deterministic manner
4. **Trace Execution** - Record events for observability
5. **Check Capabilities** - Validate permissions before operations
6. **Raise Errors** - When capabilities missing or execution fails

### ❌ Runtime Does NOT Do

1. **Filesystem Operations** - No file read/write
2. **Network Operations** - No HTTP requests, sockets
3. **Environment Access** - No env vars, system calls
4. **User Input** - No stdin reading
5. **User Output** - No stdout/stderr writing
6. **Time/Random** - No non-deterministic operations
7. **Database Access** - No SQL, no persistence

### Code Example: What Runtime Does

```python
from ape import RuntimeExecutor, ExecutionContext

# This works - pure computation, no side effects
code = """
if x > 5:
    y = x * 2
else:
    y = x + 2
"""

context = ExecutionContext()
context.set('x', 10)

executor = RuntimeExecutor()
result = executor.execute(parse(code), context)

# Runtime executes control flow and returns result
# NO actual IO happens here
```

---

## Adapters: What They Do

**Adapters are external components (not part of APE core) that implement actual side effects.**

### Adapter Characteristics

1. **External** - Not shipped with APE
2. **Optional** - APE works without them
3. **Pluggable** - Can be swapped
4. **Respect Boundaries** - Check capabilities before acting
5. **User-Provided** - Implemented by APE users or ecosystem

### Adapter Pattern (Conceptual)

```python
class IOAdapter:
    """
    Example adapter (NOT part of APE core).
    
    Implements actual filesystem operations while respecting
    capability boundaries.
    """
    
    def __init__(self, context: ExecutionContext):
        self.context = context
    
    def read_file(self, path: str) -> str:
        # Check capability
        if not self.context.has_capability('io.read'):
            raise CapabilityError('io.read', 'read_file')
        
        # Perform actual IO (external to APE runtime)
        with open(path, 'r') as f:
            return f.read()
    
    def write_file(self, path: str, content: str) -> None:
        # Check capability
        if not self.context.has_capability('io.write'):
            raise CapabilityError('io.write', 'write_file')
        
        # Perform actual IO (external to APE runtime)
        with open(path, 'w') as f:
            f.write(content)


# Usage (hypothetical)
context = ExecutionContext()
context.allow('io.read')
context.allow('io.write')

adapter = IOAdapter(context)
content = adapter.read_file('input.txt')
adapter.write_file('output.txt', content.upper())
```

**Key Point:** `IOAdapter` is external to APE. APE runtime provides the capability mechanism but doesn't implement the adapter.

---

## Why This Boundary Exists

### 1. **Determinism**
APE runtime must be fully deterministic. IO is inherently non-deterministic (files change, network fails).

### 2. **Safety**
Runtime can run untrusted code safely because it can't perform side effects.

### 3. **Testability**
Pure runtime can be tested without mocking IO, filesystem, or network.

### 4. **Portability**
Same APE code runs anywhere. Adapters handle platform-specific details.

### 5. **Governance**
Capability checks create audit trail of what code wants to do, even if adapter denies it.

### 6. **Replaceability**
Different adapters for different environments (dev, test, prod, sandboxed).

---

## Capability Lifecycle

### 1. **Declaration** (APE Code)
```ape
task read_config:
    constraints:
        - requires io.read
```

### 2. **Grant** (Execution Context)
```python
context = ExecutionContext()
context.allow('io.read')
```

### 3. **Check** (Runtime)
```python
if not context.has_capability('io.read'):
    raise CapabilityError('io.read', 'read_config')
```

### 4. **Trace** (Observability)
```python
trace_event = TraceEvent(
    node_type='TASK',
    phase='enter',
    context_snapshot={...},
    metadata={'capabilities': ['io.read']}
)
```

### 5. **Implement** (Adapter)
```python
adapter.read_file('config.json')  # Actual IO happens here
```

---

## v1.0 Capability Policy

### What's Included

- **Capability names** - String identifiers (e.g., 'io.read')
- **Capability checking** - `has_capability()`, `allow()`
- **Capability gating** - `CapabilityError` when missing
- **Capability tracing** - Record in execution traces
- **Capability inheritance** - Child scopes inherit from parent

### What's NOT Included

- **Adapter implementations** - Not part of core
- **Standard adapters** - No built-in IO adapters
- **Adapter discovery** - Users provide their own
- **Adapter composition** - External to APE

### Future Directions (Post-1.0)

Potential future work (not committed for 1.0):

- **Standard adapter interfaces** - Define adapter contracts
- **Adapter registry** - Pluggable adapter system
- **Capability composition** - Combine capabilities into policies
- **Capability inference** - Automatic capability detection
- **Adapter sandbox** - Isolate adapters from each other

**None of these are in scope for v1.0.0.**

---

## Design Guarantees

### APE Runtime Will Never:

1. ❌ Perform actual IO operations
2. ❌ Access filesystem directly
3. ❌ Make network requests
4. ❌ Read environment variables for side effects
5. ❌ Execute arbitrary system commands
6. ❌ Include built-in adapters for side effects

### APE Runtime Will Always:

1. ✅ Remain side-effect free
2. ✅ Be fully deterministic
3. ✅ Check capabilities before declaring intent
4. ✅ Raise `CapabilityError` when capability missing
5. ✅ Trace capability usage for audit
6. ✅ Allow users to implement their own adapters

---

## Comparison: Other Languages

### Python (No Capability System)
```python
# Python: Direct IO, no capability check
with open('file.txt', 'r') as f:
    content = f.read()
```

### Wasm (Capability-Based)
```
; WebAssembly: WASI capabilities
(import "wasi_snapshot_preview1" "fd_read" ...)
```

### APE (Capability + Adapter)
```ape
task read_file:
    constraints:
        - requires io.read
    # APE runtime validates capability
    # External adapter performs actual IO
```

---

## FAQ

**Q: Why not include a standard IO adapter?**  
A: Keeps core simple, portable, and deterministic. Users can choose their own adapters.

**Q: How do I actually perform IO?**  
A: Implement an adapter that checks capabilities and performs IO. See adapter pattern above.

**Q: Can I use APE without adapters?**  
A: Yes! Pure computation, tracing, explanation, replay all work without adapters.

**Q: Will adapters ever be part of APE core?**  
A: No. Adapters are fundamentally external to maintain determinism and safety.

**Q: What if I want different IO behavior in different environments?**  
A: Use different adapters! Same APE code, different adapter implementations.

**Q: Can adapters be sandboxed?**  
A: Yes, but that's the adapter implementer's responsibility, not APE runtime's.

**Q: How do I test code that needs IO?**  
A: Use mock adapters that respect capabilities but don't perform real IO.

---

## Summary

| Component | Responsibility | Side Effects? | Part of APE? |
|-----------|----------------|---------------|--------------|
| **APE Runtime** | Parse, validate, execute, trace, check capabilities | ❌ No | ✅ Yes |
| **Capabilities** | Declare intent, gate operations | ❌ No | ✅ Yes |
| **Adapters** | Implement actual IO/side effects | ✅ Yes | ❌ No |

**Key Insight:** APE runtime is a pure, deterministic execution engine. Side effects happen in external adapters that respect capability boundaries.

---

## References

- [APE_1.0_SPECIFICATION.md](APE_1.0_SPECIFICATION.md) - Language specification
- [PUBLIC_API_CONTRACT.md](PUBLIC_API_CONTRACT.md) - API stability guarantees
- [runtime_observability.md](runtime_observability.md) - Tracing and observability
- [RELEASE_GOVERNANCE.md](RELEASE_GOVERNANCE.md) - Versioning policy

---

**Status:** Finalized for v1.0.0  
**Last Updated:** December 6, 2025  
**Architectural Guarantee:** This boundary will not change in 1.x releases
