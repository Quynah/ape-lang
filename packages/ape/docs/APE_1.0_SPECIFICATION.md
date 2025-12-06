# APE 1.0 Language Specification

**Version:** 1.0.0  
**Status:** Specification Freeze  
**Date:** December 6, 2025  
**Authority:** Definitive language specification for APE v1.x releases

This document defines the APE programming language as stabilized for the 1.0.0 release and all subsequent 1.x releases. This specification is frozen - changes require a major version bump to 2.0.0.

---

## 1. Purpose & Philosophy

### 1.1 What APE Is

**APE (Autonomous Programming Environment) is a deterministic, constraint-based programming language designed for unambiguous communication between humans and AI systems.**

Core principles:
- **Determinism** - Same input always produces same output
- **Explicitness** - No implicit behavior or "magic"
- **Inspectability** - Execution can be traced, explained, and replayed
- **Safety** - No arbitrary code execution, no uncontrolled side effects
- **Predictability** - Behavior is always documented and guaranteed

### 1.2 Who APE Is For

- **AI Systems** - Can generate APE reliably because syntax is unambiguous
- **Human Developers** - Benefit from explicit, traceable execution
- **Enterprise/Governance** - Audit trails, replay validation, capability gating
- **Safety-Critical Applications** - Deterministic, side-effect-free core

### 1.3 What APE Is NOT

APE is explicitly NOT:
- ❌ A general-purpose systems programming language
- ❌ Optimized for execution speed
- ❌ Designed for concurrent/parallel programming
- ❌ A framework for autonomous agent behavior
- ❌ Magic - no implicit AI behavior or "do what I mean"

---

## 2. Language Scope (Frozen for 1.x)

### 2.1 Included Features

**✅ Control Flow**
- `if` / `else if` / `else` - Conditional branching
- `while` - Condition-based loops
- `for ... in` - Iteration over collections

**✅ Expressions**
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Logical: `and`, `or`, `not`
- Variable assignment: `set x to value`

**✅ Module System**
- `module <name>` - Module declarations
- `import <module>` - Import statements
- Qualified identifiers: `module.task(...)`
- Deterministic module resolution

**✅ Task Definitions**
- `task <name>:` - Task declarations
- `inputs:` - Input parameters
- `outputs:` - Output parameters
- `constraints:` - Execution constraints
- `steps:` - Execution steps

**✅ Standard Library (v0.1)**
- `sys` - System operations (print, exit)
- `io` - Input/output declarations
- `math` - Arithmetic operations

### 2.2 Explicitly NOT Included (1.x)

❌ Type system beyond basic types  
❌ Classes or object-oriented programming  
❌ First-class functions or lambdas  
❌ Async/await or concurrency  
❌ Exception handling (beyond runtime errors)  
❌ Metaprogramming or macros  
❌ File I/O implementation (capability-gated only)  
❌ Network operations  
❌ Database access  
❌ Random number generation  
❌ Time/date operations  

**These may be added in 2.0.0, but are out of scope for 1.x.**

---

## 3. Execution Model

### 3.1 AST-Based Execution

APE programs execute via Abstract Syntax Tree (AST) interpretation:

1. **Parse** - Source code → AST
2. **Validate** - Semantic checks, type validation
3. **Link** - Resolve module dependencies
4. **Execute** - AST-driven evaluation (NO `exec()`/`eval()`)

```
Source Code → Lexer → Parser → AST → Validator → Linker → Executor
```

**Key Point:** APE does NOT use Python's `exec()`, `eval()`, or `compile()`. All execution is AST-driven for full control and safety.

### 3.2 Deterministic Behavior

**Guarantee:** Given the same input (source code + initial context), APE always produces the same output.

**Determinism Properties:**
- ✅ No randomness
- ✅ No time-dependent behavior
- ✅ No filesystem reads (unless via adapter with fixed input)
- ✅ No network calls
- ✅ No environment variable access
- ✅ Iteration order is specified

**Example:**
```python
# This APE code
if x > 5:
    y = x * 2

# With x=10, ALWAYS produces y=20
# Never y=19, y=21, or anything else
```

### 3.3 Sandbox Safety

APE runtime is sandbox-safe by design:

**No Direct Access To:**
- Filesystem
- Network
- Operating system
- Environment variables
- Arbitrary Python code
- External processes

**All side effects require:**
1. Explicit capability declaration
2. Capability granted via `ExecutionContext.allow()`
3. External adapter implementation (not part of APE core)

### 3.4 Execution Limits

Safety guardrails prevent infinite loops and resource exhaustion:

- **Max Iterations:** Default 10,000 per loop
- **Stack Depth:** Limited by Python (typically ~1000)
- **Memory:** Limited by Python VM

**Configurable:**
```python
executor = RuntimeExecutor(max_iterations=50_000)
```

---

## 4. Type System (1.0)

### 4.1 Basic Types

APE 1.0 supports these primitive types:

- **Integer** - Whole numbers (backed by Python int)
- **Float** - Floating-point numbers (backed by Python float)
- **String** - Text (backed by Python str)
- **Boolean** - True/False (backed by Python bool)
- **None** - Absence of value (backed by Python None)
- **List** - Ordered collection (backed by Python list)
- **Dict** - Key-value mapping (backed by Python dict)

### 4.2 Type Constraints

Types can be declared in task signatures:

```ape
task calculate:
    inputs:
        x: Integer
        y: Integer
    outputs:
        result: Integer
```

**Validation:** Type mismatches raise `ValidationError` at compile time.

### 4.3 Future Type System

Advanced types (planned for 2.0+):
- Union types
- Optional types
- Generic types
- Custom types
- Algebraic data types

**Not in 1.x releases.**

---

## 5. Control Flow Semantics

### 5.1 If/Else If/Else

```ape
if condition:
    - steps...
else if another_condition:
    - steps...
else:
    - steps...
```

**Semantics:**
- Conditions evaluated left-to-right
- First true condition executes its block
- `else` executes if no condition true
- Blocks create child scopes (variables inherit from parent)

### 5.2 While Loops

```ape
while condition:
    - steps...
```

**Semantics:**
- Condition evaluated before each iteration
- Loop terminates when condition false
- Safety limit: `max_iterations` (default 10,000)
- Raises `MaxIterationsExceeded` if limit reached

### 5.3 For Loops

```ape
for item in collection:
    - steps...
```

**Semantics:**
- Iterates over collection (list, tuple, range)
- Loop variable (`item`) assigned each element
- Iteration order: left-to-right
- Empty collection → zero iterations

---

## 6. Module System

### 6.1 Module Declaration

```ape
module calculator
```

- One module per file
- Module name matches filename (without `.ape`)
- Module creates namespace for tasks

### 6.2 Import System

```ape
import math
import sys
```

**Resolution Order:**
1. Current directory
2. `./lib/` subdirectory
3. Standard library (`ape_std/`)

**Deterministic:** Same project structure always resolves same modules.

### 6.3 Qualified Identifiers

```ape
call math.add with x and y
```

- Syntax: `module.task`
- Prevents naming conflicts
- Makes dependencies explicit

### 6.4 Circular Import Detection

Linker detects and rejects circular imports:

```
A imports B
B imports C
C imports A  # Error: circular dependency
```

Raises `LinkerError` with import chain.

---

## 7. Capabilities & Side Effects

### 7.1 Capability Philosophy

**Core Principle:** APE runtime declares intent; external adapters implement side effects.

```
[APE Runtime: Side-Effect Free]
         ↓
   Capability Check
         ↓
[External Adapter: Performs IO]
```

### 7.2 Built-in Capabilities

| Capability | Intent |
|-----------|--------|
| `io.read` | Read external input |
| `io.write` | Write external output |
| `io.stdout` | Write to standard output |
| `io.stdin` | Read from standard input |
| `sys.exit` | Terminate execution |

### 7.3 Capability Lifecycle

1. **Declare** (in constraints)
2. **Grant** (`context.allow('io.read')`)
3. **Check** (`context.has_capability('io.read')`)
4. **Trace** (recorded in execution trace)
5. **Implement** (external adapter performs actual operation)

### 7.4 Missing Capability Behavior

When required capability not granted:
- Raises `CapabilityError`
- Includes capability name and operation
- Execution stops (deterministic failure)

**No silent failures or assumptions.**

---

## 8. Runtime Observability

### 8.1 Execution Tracing

**Purpose:** Non-intrusive observation of program execution.

**Features:**
- Enter/exit events for every AST node
- Context snapshots (shallow copy of variables)
- No side effects on execution
- Deterministic: same code → same trace

**API:**
```python
trace = TraceCollector()
executor = RuntimeExecutor(trace=trace)
executor.execute(ast, context)
events = trace.events()  # List of TraceEvent
```

### 8.2 Dry-Run Mode

**Purpose:** Analyze code without mutations.

**Features:**
- Control flow executes normally
- Variable writes blocked (raise `RuntimeError`)
- Read operations allowed
- Useful for static analysis

**API:**
```python
context = ExecutionContext(dry_run=True)
# OR
executor = RuntimeExecutor(dry_run=True)
```

### 8.3 Explanation

**Purpose:** Convert traces to human-readable narratives.

**Features:**
- Context-aware summaries (IF, WHILE, FOR, etc.)
- Dry-run awareness
- Fully deterministic (no LLM)

**API:**
```python
explainer = ExplanationEngine()
explanations = explainer.from_trace(trace)
for step in explanations:
    print(f"{step.index}: {step.summary}")
```

### 8.4 Replay

**Purpose:** Validate deterministic execution.

**Features:**
- Validates trace structure (enter/exit symmetry)
- Compares two traces for equivalence
- Does NOT re-execute code

**API:**
```python
replayer = ReplayEngine()
validated_trace = replayer.replay(trace)
replayer.validate_determinism(trace1, trace2)
```

---

## 9. Error Model

### 9.1 Error Hierarchy

All APE errors inherit from `ApeError`:

```
ApeError (base)
├── ParseError
├── ValidationError
├── LinkerError
├── RuntimeExecutionError
│   ├── ExecutionError
│   └── MaxIterationsExceeded
├── CapabilityError
├── ReplayError
└── ProfileError
```

### 9.2 Error Context

Every error includes:
- `message: str` - Human-readable description
- `context: ErrorContext` - Semantic context

ErrorContext provides:
- `node_type: Optional[str]` - AST node where error occurred
- `trace_index: Optional[int]` - Position in trace
- `line_number: Optional[int]` - Source line number
- `details: Dict[str, Any]` - Additional information

### 9.3 No Python Stacktraces

**Guarantee:** APE errors never expose Python implementation details to end users.

**Instead:** Semantic context (node type, trace position, source location).

---

## 10. Safety Guarantees

### 10.1 What APE Guarantees

**✅ Determinism**
- Same input → same output, always
- No hidden state or randomness

**✅ Sandbox Safety**
- No arbitrary code execution
- No filesystem access (without adapter)
- No network access
- No environment variable reading

**✅ Predictability**
- Behavior documented and stable
- Breaking changes only in major versions

**✅ Inspectability**
- Every execution traceable
- Traces explainable and replayable

**✅ Capability Gating**
- All side effects require explicit permission
- Missing capability → deterministic failure

### 10.2 What APE Does NOT Guarantee

**❌ Performance**
- Optimized for correctness, not speed
- No performance SLA

**❌ Resource Limits**
- Memory limited by Python VM
- No built-in CPU limits

**❌ Concurrency Safety**
- Single-threaded execution model
- No thread-safe guarantees

**❌ External Adapter Behavior**
- Adapters are external to APE
- APE doesn't control adapter implementations

---

## 11. Non-Goals

APE explicitly does NOT aim to be:

### 11.1 Fast
- Execution speed is not a priority
- Correctness and inspectability > performance

### 11.2 Concurrent
- No async/await
- No threading or multiprocessing
- Single-threaded deterministic execution

### 11.3 Autonomous
- No agent autonomy built-in
- No LLM integration in core
- Human/AI collaboration, not AI autonomy

### 11.4 Magical
- No implicit behavior
- No "do what I mean" interpretation
- Everything explicit and documented

### 11.5 A Framework
- Language + runtime, not framework
- No opinionated project structure
- No build system or package manager (v1.0)

---

## 12. Backward Compatibility Promise

### 12.1 What Stays Stable in 1.x

**✅ Syntax**
- All v1.0 syntax remains valid
- New syntax may be added (with new keywords)

**✅ Semantics**
- Execution behavior unchanged
- Deterministic output guaranteed

**✅ Public API**
- All public API remains compatible
- See PUBLIC_API_CONTRACT.md for details

**✅ Error Types**
- Error hierarchy stable
- New error types may be added (non-breaking)

**✅ Capabilities**
- Built-in capabilities remain
- New capabilities may be added

### 12.2 What May Change in 1.x

**⚠️ Non-Breaking Additions**
- New stdlib modules
- New capabilities
- Performance improvements
- Bug fixes
- Documentation clarifications

**⚠️ Semi-Internal APIs**
- AST node structure (with deprecation notice)
- Code generation output format
- Internal module APIs

See RELEASE_GOVERNANCE.md for deprecation process.

### 12.3 What Requires 2.0

**❌ Breaking Changes**
- Syntax changes (removing keywords)
- Semantic changes (changing execution behavior)
- Public API removals or signature changes
- Type system overhaul
- New execution model

---

## 13. Standard Library (v0.1)

### 13.1 sys Module

```ape
import sys

task main:
    steps:
        - call sys.print with "Hello, world!"
        - call sys.exit with 0
```

**Operations:**
- `print(message: String)` - Requires `io.stdout` capability
- `exit(code: Integer)` - Requires `sys.exit` capability

### 13.2 io Module

```ape
import io

task main:
    steps:
        - call io.read_line to get input
        - call io.write_file with path and content
```

**Operations:**
- `read_line()` - Requires `io.stdin` capability
- `write_file(path, content)` - Requires `io.write` capability
- `read_file(path)` - Requires `io.read` capability

### 13.3 math Module

```ape
import math

task calculate:
    steps:
        - call math.add with 5 and 3 to get result
        - call math.sqrt with 16 to get root
```

**Operations:**
- Arithmetic: `add`, `subtract`, `multiply`, `divide`
- Advanced: `power`, `sqrt`, `factorial`, `abs`

**Note:** Math operations do NOT require capabilities (pure computation).

---

## 14. Future Extensions (Post-1.0)

These features are NOT in 1.0 but may be added in future versions:

### 14.1 Multi-Language Surface Syntax (Consolidated in v1.0.0)

**Status:** ✅ Implemented in v1.0.0

APE now supports multi-language surface syntax via deterministic language adapters:
- Supported languages: EN (canonical), NL, FR, DE, ES, IT, PT (Latin script only)
- Keywords-only translation (identifiers unchanged)
- Adapter runs before tokenization
- Identical AST and runtime behavior across all languages
- No NLP, no heuristics, no ambiguity

See [docs/multilanguage.md](multilanguage.md) for details.

### 14.2 Standard Library v0 - Pure, Deterministic Core (Consolidated in v1.0.0)

**Status:** ✅ Implemented in v1.0.0

APE now includes a foundational standard library with pure, deterministic functions:

**Modules:**
- `std.logic` - Boolean logic and assertions (6 functions)
- `std.collections` - Collection operations (5 functions)
- `std.strings` - String manipulation (6 functions)
- `std.math` - Mathematical operations (5 functions)

**Characteristics:**
- Pure functions (no side effects)
- Deterministic (same input → same output)
- Runtime intrinsics (no capabilities required)
- Full type safety with clear error messages
- 86 comprehensive tests, all passing
- Fully traceable in execution logs

**What is NOT included:**
- ❌ IO operations (require capabilities)
- ❌ Time/date operations (non-deterministic)
- ❌ Random numbers (non-deterministic)
- ❌ State mutation (not pure)

See [docs/stdlib.md](stdlib.md) for complete documentation.

### 14.3 Type System Enhancements (2.0)
- Union types: `String | Integer`
- Optional types: `Optional[String]`
- Generic types: `List[T]`
- Custom type definitions

### 14.4 First-Class Functions (2.0)
- Lambda expressions
- Function types
- Higher-order functions

### 14.5 Pattern Matching (2.0)
- Match expressions
- Destructuring
- Exhaustiveness checking

### 14.6 Package Manager (2.x)
- Dependency declaration
- Version management
- Package registry

### 14.7 Formal Verification (3.0)
- Proof obligations
- Contract checking
- Static analysis integration

**None of these are committed. Subject to community feedback and priorities.**

---

## 15. Specification Compliance

### 15.1 Reference Implementation

The Python-based APE compiler and runtime (github.com/Quynah/ape-lang) is the reference implementation for this specification.

**Version:** APE v1.0.0  
**Language:** Python 3.11+

### 15.2 Alternative Implementations

Alternative implementations must:
- Pass the official test suite
- Maintain deterministic behavior
- Implement all v1.0 features
- Respect safety guarantees

### 15.3 Test Suite

Official compliance test suite:
- 265+ tests covering all features
- Determinism validation
- Error behavior validation
- Module system validation

---

## 16. Governance

### 16.1 Specification Authority

This specification is the authoritative definition of APE 1.x.

**Precedence:**
1. This specification (APE_1.0_SPECIFICATION.md)
2. PUBLIC_API_CONTRACT.md
3. CAPABILITY_ADAPTER_BOUNDARY.md
4. Reference implementation

### 16.2 Changes to Specification

**1.x Releases:**
- No semantic changes
- Clarifications allowed (non-normative)
- Errata fixed in patch releases

**2.0 Release:**
- Breaking changes allowed
- Requires specification rewrite
- Deprecation notices in 1.x

See RELEASE_GOVERNANCE.md for process.

---

## 17. Acknowledgments

APE is inspired by:
- **Wasm** - Capability-based security
- **Rust** - Safety guarantees and explicit behavior
- **Dafny** - Verification and constraints
- **Haskell** - Purity and determinism

---

## 18. References

- **PUBLIC_API_CONTRACT.md** - API stability guarantees
- **CAPABILITY_ADAPTER_BOUNDARY.md** - Side effect boundaries
- **RELEASE_GOVERNANCE.md** - Version management
- **APE_Spec_v0.1.md** - Original specification (superseded)

---

**Status:** ✅ Specification Freeze  
**Version:** 1.0.0  
**Date:** December 6, 2025  
**Authority:** Definitive for all v1.x releases  
**Changes:** Require 2.0.0 (major version bump)

This specification will remain stable across all 1.x releases. Breaking changes require a new major version (2.0.0).
