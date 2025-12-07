# APE Language Roadmap

**Last Updated:** December 6, 2025  
**Current Version:** v1.0.0  
**Status:** Complete Language Release

## Introduction

APE (Autonomous Programming Environment) is a deterministic AI-first programming language designed for unambiguous human-AI collaboration. This roadmap reflects the actual implementation status of features across all versions.

**Core Principles:**
- **Deterministic execution** - Same input always produces same output
- **AST-based runtime** - No use of Python's `exec()`, `eval()`, or `compile()`
- **Sandbox safety** - No arbitrary code execution, capability-gated side effects
- **Observability** - Full tracing, explanation, and replay capabilities
- **Explicitness** - No implicit behavior or "magic"

This document tracks what has been implemented, what is in progress, and what is planned for future versions.

**Author:** David Van Aelst

---

## Version History & Status

| Version | Focus | Status | Notes |
|---------|-------|--------|-------|
| v0.2.0 | Module system + stdlib | DONE | Module/import system, stdlib (sys/io/math), linker |
| v0.2.2 | Packaging fix | DONE | Distribution rebuild, no functional changes |
| v0.3.0 | Control flow + runtime + observability | DONE | If/while/for, AST executor, tracing, dry-run, capabilities, explanation, replay, profiles |
| v1.0.0 | Complete language release | DONE | Specification freeze, API stability, unified error model, multi-language, **v0.4.0-v0.6.0 features scaffolded** |
| v0.4.0 | Error model + structured types | MERGED INTO v1.0.0 | Scaffolded: Try/catch, List<T>, Map<K,V>, Record, Tuple |
| v0.5.0 | Expanded stdlib | MERGED INTO v1.0.0 | Scaffolded: JSON, extended math, extended collections |
| v0.6.0 | Compiler backend + VM | MERGED INTO v1.0.0 | Scaffolded: Optimizer, bytecode VM, benchmarking |

**Legend:**
- **DONE** - Fully implemented, tested, documented
- **MERGED INTO v1.0.0** - Scaffolded in v1.0.0 (structure + docs complete, implementation pending)
- **PLANNED** - Future implementation beyond v1.0.0

---

## v0.2.0 — Module System & Standard Library

**Status:** ✅ DONE  
**Release Date:** December 4, 2025  
**Focus:** Module/import system, standard library foundation, linker

### Implementation

**Module System**
- Files: `src/ape/parser/ast_nodes.py` (ModuleNode, ImportNode)
- Files: `src/ape/linker.py` (LinkerImpl, module resolution)
- Syntax: `module <name>` declarations, `import <module>` statements
- Qualified identifiers: `module.task(...)` for imported tasks
- Deterministic resolution order: `./lib/` → `./` → `<APE_INSTALL>/ape_std/`

**Linker**
- Dependency graph construction
- Circular dependency detection
- Topological sorting for compilation order
- Clear error messages for missing modules

**Standard Library v0.1**
- Location: `ape_std/` directory
- Modules: `sys.ape`, `io.ape`, `math.ape`
- Functions: 8 total (print, exit, read_line, write_file, read_file, add, subtract, multiply, divide, power)

**Code Generation**
- Name mangling: `<module>.<symbol>` → `<module>__<symbol>`
- Multi-file generation support
- Backward compatible with non-module files

### Tests

- `tests/linker/` - 25+ linker tests
- `tests/codegen/` - Module codegen tests
- `tests/examples/` - End-to-end module system tests
- Total: ~192 tests passing

### Documentation

- `docs/modules_and_imports.md` - Complete module system specification
- `docs/linker_implementation.md` - Linker design and implementation
- `docs/stdlib_v0.1.md` - Standard library API reference
- `docs/codegen_namespacing.md` - Name mangling strategy

---

## v0.2.2 — Packaging Fix

**Status:** ✅ DONE  
**Release Date:** December 6, 2025  
**Focus:** Distribution rebuild, documentation updates

### Changes

- Rebuilt PyPI distribution with all modules
- Documentation updates for version consistency
- No functional code changes
- Removed outdated artifacts

---

## v0.3.0 — Control Flow, Runtime, & Observability

**Status:** ✅ DONE  
**Release Date:** December 6, 2025  
**Focus:** Control flow constructs, AST-based runtime executor, observability layer

### Implementation

**Control Flow**
- Files: `src/ape/parser/ast_nodes.py` (IfNode, WhileNode, ForNode)
- Files: `src/ape/runtime/executor.py` (control flow execution)
- Syntax: `if/else if/else`, `while`, `for ... in`
- Expressions: arithmetic (`+`, `-`, `*`, `/`, `%`), comparison (`<`, `>`, `<=`, `>=`, `==`, `!=`), logical (`and`, `or`, `not`)

**AST-Based Runtime**
- Files: `src/ape/runtime/executor.py` (RuntimeExecutor)
- Files: `src/ape/runtime/context.py` (ExecutionContext)
- No use of Python's `exec()`, `eval()`, or `compile()`
- Pure AST interpretation for complete control
- Deterministic evaluation guarantees
- Sandbox-safe execution (no filesystem/network/env access)
- Configurable iteration limits (default: 10,000)

**Execution Tracing**
- Files: `src/ape/runtime/trace.py` (TraceCollector, TraceEvent)
- Non-intrusive observation of program execution
- Records enter/exit events for all AST nodes
- Context snapshots with shallow copy of primitives
- Zero side effects - tracing never affects execution

**Dry-Run Mode**
- Safe analysis without mutations or side effects
- Control flow evaluated normally, writes blocked
- Inherited by child scopes
- Use case: auditing, what-if analysis, testing in production

**Capability Gating**
- Fine-grained control over side effects and resource access
- Built-in capabilities: `io.read`, `io.write`, `io.stdout`, `io.stdin`, `sys.exit`
- `allow(capability)` to grant permissions
- `has_capability(capability)` to check permissions
- Raises `CapabilityError` when required capability missing

**Explanation Engine**
- Files: `src/ape/runtime/explain.py` (ExplanationEngine, ExplanationStep)
- Converts traces into human-readable explanations
- Context-aware explanations for all control flow nodes
- Fully deterministic (no LLM, pure trace interpretation)
- Dry-run awareness ("would be set" vs "set")

**Replay Engine**
- Files: `src/ape/runtime/replay.py` (ReplayEngine, ReplayError)
- Validates deterministic execution without re-running code
- Checks enter/exit symmetry, node type consistency, proper nesting
- Compares traces for deterministic equivalence
- Validation only - no code re-execution

**Runtime Profiles**
- Files: `src/ape/runtime/profile.py` (RUNTIME_PROFILES, ProfileError)
- Predefined configurations: `analysis`, `execution`, `audit`, `debug`, `test`
- Convenience layer over ExecutionContext and RuntimeExecutor settings
- Custom profile registration support

### Tests

- `tests/runtime/test_control_flow.py` - 20+ control flow tests
- `tests/runtime/test_observability.py` - 18+ observability tests
- `tests/runtime/test_introspection.py` - 35+ introspection tests
- Total: ~265 tests passing

### Documentation

- `docs/control_flow.md` - Control flow syntax and semantics
- `docs/runtime_observability.md` - Tracing, dry-run, capabilities guide
- `docs/runtime_introspection.md` - Explanation and replay API reference
- `README.md` - Updated with runtime features section

---

## v1.0.0 — Complete Minimal Language

**Status:** ✅ DONE  
**Release Date:** December 6, 2025 (Specification Freeze)  
**Focus:** API stability, specification freeze, unified error model, release governance

### Implementation

**Unified Error Hierarchy**
- Files: `src/ape/runtime/context.py` (ApeError base class + 8 specific errors)
- All errors inherit from `ApeError` with semantic context
- Error types: `ExecutionError`, `MaxIterationsExceeded`, `CapabilityError`, `ReplayError`, `ProfileError`, `RuntimeExecutionError`, `ParseError`, `ValidationError`, `LinkerError`
- `ErrorContext` dataclass for structured error information (no Python stacktraces)

**Public API Contract**
- Files: `docs/PUBLIC_API_CONTRACT.md`
- Clear stability markers: ✅ Public, ⚠️ Semi-Internal, ❌ Internal
- Stable public API: `compile()`, `validate()`, `run()`, `ApeModule`, `ExecutionContext`, `RuntimeExecutor`
- Observability: `TraceCollector`, `TraceEvent`, `ExplanationEngine`, `ReplayEngine`
- SemVer guarantees for public APIs

**Capability-Adapter Boundary**
- Files: `docs/CAPABILITY_ADAPTER_BOUNDARY.md`
- Hard architectural boundary: runtime = side-effect free, adapters = side effects
- Runtime requests capabilities, adapters implement them externally
- No side effects leak into core runtime

**Language Specification**
- Files: `docs/APE_1.0_SPECIFICATION.md` (793 lines, comprehensive)
- Definitive language specification frozen for 1.x releases
- Defines scope: control flow, expressions, modules, stdlib
- Explicitly excludes: OOP, async, exceptions, metaprogramming, I/O implementation, networking, databases, random, time/date
- Execution model: AST-based, deterministic, sandbox-safe
- Backward compatibility promise for all 1.x releases

**Release Governance**
- Files: `docs/RELEASE_GOVERNANCE.md`
- SemVer policy (breaking changes → 2.0.0)
- Deprecation process (warnings for one minor version)
- Release checklist for version bumps

### What 1.0.0 Includes

**Language Features**
- ✅ Control flow: if/else if/else, while, for
- ✅ Expressions: arithmetic, comparison, logical
- ✅ Module system: module declarations, imports, qualified identifiers
- ✅ Task definitions: inputs, outputs, constraints, steps
- ✅ Basic types: Integer, Boolean, String

**Runtime Features**
- ✅ AST-based executor (no exec/eval)
- ✅ Deterministic execution
- ✅ Sandbox safety
- ✅ Iteration limits
- ✅ Variable scoping (parent/child contexts)

**Observability Features**
- ✅ Execution tracing
- ✅ Dry-run mode
- ✅ Capability gating
- ✅ Explanation engine
- ✅ Replay validation
- ✅ Runtime profiles

**Standard Library**
- ✅ sys: print, exit
- ✅ io: read_line, write_file, read_file (capability-gated)
- ✅ math: add, subtract, multiply, divide, power

### Tests

- Total: 265+ tests passing
- Coverage: parser, linker, codegen, runtime, observability, introspection
- No regressions from 0.3.0

### Documentation

- `docs/APE_1.0_SPECIFICATION.md` - Authoritative language spec
- `docs/PUBLIC_API_CONTRACT.md` - API stability guarantees
- `docs/CAPABILITY_ADAPTER_BOUNDARY.md` - Architecture boundary
- `docs/RELEASE_GOVERNANCE.md` - Version management policy
- `README.md` - Updated with "APE v1.0 Readiness" section

### v1.0 Guarantees

When using APE v1.0.x, you can rely on:
- **Backward Compatibility** - All v1.0 code runs on v1.x (no breaking changes)
- **Stable Public API** - Core functions and classes will not change
- **Deterministic Execution** - Same input → same output, always
- **Semantic Versioning** - Breaking changes require 2.0.0
- **Safety Guarantees** - No arbitrary code execution, capability-gated side effects

---

## v1.0.1 — Multi-Language + Tutorials + Tests

**Status:** ✅ DONE  
**Release Date:** December 6, 2025  
**Focus:** Multi-language surface syntax, tutorial scenarios, comprehensive test expansion

### Implementation

**Multi-Language Surface Syntax**
- Files: `src/ape/lang/` directory
- Files: `src/ape/lang/base.py` (LanguageAdapter base class)
- Files: `src/ape/lang/registry.py` (adapter lookup and validation)
- Individual adapters: `en.py`, `nl.py`, `fr.py`, `de.py`, `es.py`, `it.py`, `pt.py`
- 7 languages supported: English (canonical), Dutch, French, German, Spanish, Italian, Portuguese
- Latin script only (v1.0.1 restriction)
- Keywords-only translation - identifiers and literals remain unchanged
- Adapters run before tokenization (parser/runtime unchanged)
- Deterministic normalization: all languages produce identical AST
- No NLP, no heuristics - pure lookup-based keyword matching

**Extended API**
- `run()` function with optional `language` parameter (default: "en")
- New functions: `get_adapter()`, `list_supported_languages()`
- Unsupported language codes raise `ValidationError`
- Backward compatible: English code works identically

**Tutorial Scenarios**
- Location: `tutorials/` directory with 8 scenario subdirectories
- 9 tutorial files (multilanguage scenario has EN + NL variants)
- Scenarios:
  1. `scenario_ai_input_governance/` - Multi-factor policy validation (3 inputs, 3 decision points)
  2. `scenario_ape_anthropic/` - Safety-first reasoning (3-tier classification)
  3. `scenario_ape_langchain/` - LangChain workflow validation (4 inputs, cascading checks)
  4. `scenario_ape_openai/` - OpenAI request governance (3 request types)
  5. `scenario_dry_run_auditing/` - Safe analysis mode (4 inputs, high-risk scoring)
  6. `scenario_explainable_decisions/` - 4-tier risk rating
  7. `scenario_multilanguage_team/` - EN/NL parallel examples (manual override logic)
  8. `scenario_risk_classification/` - 3-tier risk classification (4 factors)
- Each scenario includes: `.ape` file, `README.md`, test coverage
- Enriched tutorials: realistic multi-factor logic (not toy examples)
- GDPR compliance, safety tiers, risk scoring patterns

**Test Expansion**
- File: `tests/tutorials/test_tutorials_execute.py`
- 46 tutorial tests (was 29, +17 new cases)
- Coverage: execution, validation, structure, multiple paths per scenario
- Additional test cases: happy path + unhappy paths for each scenario
- Test data: `SCENARIO_CONTEXTS` dict with input parameters
- `ADDITIONAL_TEST_CASES` list with 17 edge case scenarios

**Enrichment Summary**
- File: `tutorials/ENRICHMENT_SUMMARY.md`
- Documents tutorial enrichment process
- Metrics: +113% code richness, +67% input parameters, +133% decision points
- Quality assurance: no regressions, backward compatible

### Tests

- Total: 439 tests passing (+174 from v0.3.0)
- Tutorial tests: 46 (29 baseline + 17 additional paths)
- Multi-language tests: 35+ comprehensive language adapter tests
- Baseline tests: 393 (no regressions)
- Test execution time: ~0.95s

### Documentation

- `docs/multilanguage.md` - Complete multi-language guide (60+ sections)
- `tutorials/ENRICHMENT_SUMMARY.md` - Tutorial hardening documentation
- Each tutorial: dedicated `README.md` with "How It Works" section
- Updated `README.md` with multi-language section and tutorial links
- Updated `docs/APE_1.0_SPECIFICATION.md` with multi-language in Future Extensions

### Design Guarantees

- ✅ Parser unchanged
- ✅ Runtime unchanged
- ✅ AST canonical and identical across languages
- ✅ Determinism preserved
- ✅ Safety maintained
- ✅ Backward compatible (English works identically)

---

## v0.4.0 — Error Model + Structured Types

**Status:** 🧱 SCAFFOLDED (Structure exists, not integrated)  
**Expected:** Q1 2026  
**Focus:** Enhanced error handling, structured data types

### What Currently Exists (Scaffolded)

**Error Handling Infrastructure**
- ✅ AST nodes for try/catch/finally exist in `src/ape/parser/ast_nodes.py`
- ✅ Documentation: `docs/error_model.md`
- ❌ Not integrated into executor
- ❌ Not wired into semantic validator
- ❌ Returns `NotImplementedError` if executed

**Structured Types Infrastructure**
- ✅ Type classes exist: `src/ape/types/list_type.py`, `map_type.py`, `record_type.py`, `tuple_type.py`
- ✅ Documentation: `docs/typesystem.md`
- ✅ Type validator scaffold: `src/ape/validator/types.py` (**SCAFFOLDED** header added)
- ❌ Not integrated into type system
- ❌ Not wired into semantic validation
- ❌ No runtime support for operations

**Current Error Handling (Implemented)**
- ✅ Unified error hierarchy (ApeError + 8 specific types)
- ✅ ErrorContext for semantic information
- ✅ Runtime errors with clear messages
- ❌ No user-level exception handling
- ❌ No try/catch constructs in execution flow

**Current Type Support (Implemented)**
- ✅ Basic types: Integer, Boolean, String
- ✅ Type annotations in task inputs/outputs
- ✅ Type validation at runtime
- ❌ No structured types (lists, maps, records)
- ❌ No generic types
- ❌ No type inference

### Integration Work Required

1. Wire try/catch/finally AST nodes into `RuntimeExecutor.execute()`
2. Implement exception propagation in execution context
3. Connect type validator to semantic validation pipeline
4. Add runtime support for List<T>, Map<K,V> operations
5. Implement type inference engine
6. Add comprehensive tests for exception handling
7. Add comprehensive tests for structured types

### Planned Features (After Integration)

**Enhanced Error Model**
- Exception handling constructs (`try`/`catch`/`finally`)
- User-defined error types
- Error propagation semantics
- Structured error recovery

**Structured Types**
- Lists: `List<T>` with indexing, iteration, manipulation
- Maps/Dictionaries: `Map<K, V>` with key-value storage
- Records: Named field collections (structs)
- Tuples: Fixed-size heterogeneous collections
- Type inference for collections

**Type System Expansion**
- Generic types: `List<Integer>`, `Map<String, Boolean>`
- Type constraints and validation
- Type aliases for clarity
- Union types (maybe)

### Documentation Status

- ✅ `docs/error_model.md` - Complete specification
- ✅ `docs/typesystem.md` - Complete specification
- ❌ Integration guide needed
- ❌ Migration guide from 1.x to 0.4.x needed

---

## v0.5.0 — Expanded Standard Library

**Status:** 🧱 SCAFFOLDED (Structure exists, not integrated)  
**Expected:** Q2 2026  
**Focus:** String operations, JSON parsing, extended math

### What Currently Exists (Scaffolded)

**JSON Module (Scaffolded)**
- ✅ File exists: `src/ape/std/json.py`
- ✅ Documentation: `docs/stdlib_json.md`
- ❌ Stub implementations only
- ❌ Not wired into runtime intrinsics
- ❌ Returns `NotImplementedError` if called

**Extended Math Module (Scaffolded)**
- ✅ File exists: `src/ape/std/math_ext.py`
- ✅ Documentation: `docs/stdlib_math_ext.md`
- ❌ Stub implementations only
- ❌ Not wired into runtime intrinsics
- ❌ Returns `NotImplementedError` if called

**Current Standard Library (Implemented)**
- ✅ **logic** - `src/ape/std/logic.py` (and_op, or_op, not_op, if_then_else)
- ✅ **strings** - `src/ape/std/strings.py` (11 functions: length, upper, lower, contains, concat, split, join, trim, starts_with, ends_with, substring)
- ✅ **collections** - `src/ape/std/collections.py` (13 functions: length, head, tail, is_empty, contains, map, filter, sort, sum_list, all_bool, any_bool, unique)
- ✅ **math** - `src/ape/std/math.py` (15 functions: add, sub, mul, div, div_int, mod, power, abs, sqrt, factorial, min, max, clamp)
- ✅ **comparison** - `src/ape/std/comparison.py` (6 functions: eq, neq, lt, lte, gt, gte)
- ✅ 22 functions total, 158+ tests passing
- ✅ Pure functions, deterministic, built into executor as runtime intrinsics
- ✅ See: `docs/stdlib.md`, `docs/deterministic_math_and_logic.md`

**Note on v1.0.2 stdlib extension:**
Added deterministic primitives for comparison, logic, math, collections with:
- Type-strict operations (no coercion: 1 ≠ 1.0)
- Explicit error types (StdLibError hierarchy)
- No truthy/falsy evaluation
- Determinism validation (100-iteration tested)
- Complete documentation

### Integration Work Required

1. Implement JSON parser (use Python's `json` module internally)
2. Implement JSON serializer with type safety
3. Implement extended math functions (trig, log, rounding)
4. Wire new functions into runtime intrinsics
5. Add comprehensive tests for JSON and extended math
6. Update stdlib documentation

### Planned Features (After Integration)

**JSON Module**
- JSON parsing: parse JSON strings to structured data
- JSON serialization: convert structured data to JSON strings
- Type-safe JSON access
- Error handling for malformed JSON

**Extended Math Module**
- Trigonometry: sin, cos, tan, asin, acos, atan
- Logarithms: log, log10, ln
- Rounding: round, floor, ceil
- Constants: pi, e
- Statistical functions: min, max, sum, average (some exist)

**Extended Collections Module**
- Advanced operations: reduce, zip, enumerate, range
- Set operations: union, intersection, difference
- More list operations: reverse, partition

### Documentation Status

- ✅ `docs/stdlib_json.md` - Complete specification
- ✅ `docs/stdlib_math_ext.md` - Complete specification
- ✅ `docs/stdlib.md` - Covers implemented functions
- ✅ `docs/deterministic_math_and_logic.md` - v1.0.2 extension guide
- ❌ Integration guide needed

---

## v0.6.0 — Compiler Backend & VM

**Status:** 🧱 SCAFFOLDED (Structure exists, not integrated)  
**Expected:** Q3 2026  
**Focus:** Compiler optimizations, bytecode VM exploration

### What Currently Exists (Scaffolded)

**Compiler Optimizer (Scaffolded)**
- ✅ File exists: `src/ape/compiler/optimizer.py` (**SCAFFOLDED** header added)
- ✅ Documentation: `docs/compiler_optimization.md`
- ✅ Classes defined: `OptimizationPass`, `ConstantFolder`, `DeadCodeEliminator`, `CommonSubexpressionEliminator`, `LoopOptimizer`, `TailCallOptimizer`, `OptimizationPipeline`
- ❌ Not wired into compilation pipeline
- ❌ Stub implementations only
- ❌ Returns `NotImplementedError` if called

**Bytecode VM (Scaffolded)**
- ✅ Files exist: `src/ape/vm/vm.py` (**SCAFFOLDED** header added), `src/ape/vm/instructions.py` (**SCAFFOLDED** header added)
- ✅ Documentation: `docs/bytecode_vm.md`
- ✅ Classes defined: `VirtualMachine`, `StackFrame`, `ExecutionContext`, instruction specs (30+ opcodes)
- ❌ Not integrated into execution flow
- ❌ Stub implementations only
- ❌ No bytecode compiler exists

**Benchmarking Infrastructure (Scaffolded)**
- ✅ File exists: `src/ape/benchmarks/benchmark_runner.py` (**SCAFFOLDED** header added)
- ✅ Documentation: `docs/performance_tuning.md`
- ✅ Classes defined: `BenchmarkRunner`, `BenchmarkResult`, `BenchmarkComparison`
- ❌ Not wired into test suite
- ❌ No benchmark scenarios defined
- ❌ Returns `NotImplementedError` if called

**Current Compiler (Implemented)**
- ✅ Lexer: `src/ape/tokenizer/tokenizer.py`
- ✅ Parser: `src/ape/parser/parser.py`
- ✅ AST nodes: `src/ape/parser/ast_nodes.py`
- ✅ Semantic validator: `src/ape/compiler/validator.py`
- ✅ Linker: `src/ape/linker.py`
- ✅ Code generator: `src/ape/codegen/python_codegen.py` (Python target)
- ✅ AST-based executor: `src/ape/runtime/executor.py`
- ❌ No compiler optimizations
- ❌ No bytecode VM
- ❌ No performance profiling tools
- ❌ No module caching

**Current Backend (Implemented)**
- Pure AST interpretation for runtime execution
- Python code generation for compilation workflow
- No bytecode or intermediate representation (beyond AST)
- Deterministic execution prioritized over speed
- Sandbox safety maintained

### Integration Work Required

1. Wire optimizer into compilation pipeline (parse → optimize → codegen)
2. Implement optimization passes (constant folding, DCE, CSE)
3. Build bytecode compiler (AST → bytecode)
4. Implement VM instruction dispatch loop
5. Connect VM to execution flow (alternative to AST executor)
6. Create benchmark scenarios and wire into CI
7. Add performance regression tests
8. Maintain determinism guarantees across optimizations

### Planned Features (After Integration)

**Compiler Optimizations**
- Constant folding
- Dead code elimination
- Common subexpression elimination
- Loop optimizations
- Tail call optimization

**Bytecode VM (Exploration)**
- Custom bytecode format for APE
- Stack-based VM implementation
- Faster execution than AST interpretation
- Maintain determinism guarantees
- No change to language semantics

**Performance Improvements**
- Faster parsing with optimized lexer
- Incremental compilation support
- Module caching
- Parallel module compilation
- Benchmark suite for tracking performance

### Documentation Status

- ✅ `docs/compiler_optimization.md` - Complete specification
- ✅ `docs/bytecode_vm.md` - Complete specification
- ✅ `docs/performance_tuning.md` - Complete guide
- ❌ Integration guide needed
- ❌ Performance benchmarking methodology needed
- Bytecode format specification (if VM pursued)
- VM implementation with instruction set
- Performance benchmarking infrastructure
- Maintain backward compatibility with AST executor
- Document performance characteristics

### Documentation Needed

- Compiler architecture guide
- Optimization strategies document
- Bytecode specification (if applicable)
- VM implementation guide (if applicable)
- Performance tuning guide

---

## Beyond 1.x — Future Directions

These features are **explicitly out of scope** for APE 1.x and may be considered for APE 2.0 or later:

### Language Extensions (2.0+)

- **Classes & Objects** - Object-oriented programming support
- **First-class Functions** - Functions as values, lambdas
- **Async/Await** - Asynchronous programming constructs
- **Metaprogramming** - Macros, reflection, code generation at compile time
- **Pattern Matching** - Advanced control flow with pattern-based dispatch
- **Module Packages** - Hierarchical module organization (e.g., `company.project.module`)

### Runtime Extensions (2.0+)

- **Concurrency** - Parallel execution, threading, message passing
- **Foreign Function Interface** - Call external libraries safely
- **Dynamic Loading** - Load modules at runtime
- **Garbage Collection** - Memory management beyond reference counting

### Ecosystem (Future)

- **Package Manager** - Central registry, dependency resolution, versioning
- **VS Code Extension** - Syntax highlighting, IntelliSense, debugging
- **Language Server Protocol** - IDE integration for any editor
- **Debugger** - Step-through debugging, breakpoints, inspection
- **Profiler** - Performance analysis, bottleneck identification
- **Test Framework** - Unit testing, assertion library, test runner
- **Documentation Generator** - Generate docs from code/comments

### Tooling (Future)

- **APE Playground** - Web-based REPL and tutorial environment
- **CI/CD Integration** - GitHub Actions, GitLab CI, Jenkins plugins
- **Static Analysis** - Linting, code quality checks, security scanning
- **Code Formatter** - Consistent style enforcement (like Black for Python)
- **Dependency Scanner** - Security vulnerability detection

---

## Contributing to the Roadmap

This roadmap reflects the actual state of implementation. To contribute:

1. **For DONE features:** Improve documentation, add tests, fix bugs
2. **For PLANNED features:** Review designs in GitHub issues, provide feedback
3. **For future directions:** Open GitHub discussions for new ideas

**Important:** APE 1.x is in specification freeze. New language features require 2.0.

---

## Version Naming Explanation

APE uses semantic versioning (SemVer):

- **Major (1.x.x)** - Breaking changes, specification changes
- **Minor (x.1.x)** - New features, backward compatible
- **Patch (x.x.1)** - Bug fixes, documentation updates

**Current sequence:**
- v0.2.0 → Modules + stdlib
- v0.2.2 → Packaging fix
- v0.3.0 → Control flow + runtime + observability
- v1.0.0 → Specification freeze + API stability
- v1.0.1 → Multi-language + tutorials + tests
- v0.4.0-v0.6.0 → Planned enhancements (still 1.x compatible)

Note: v0.4.0-v0.6.0 are planned as minor releases within the 1.x family. The version numbering is somewhat unconventional but reflects historical development phases.

---

**For detailed feature specifications, see:**
- [APE 1.0 Specification](APE_1.0_SPECIFICATION.md) - Language definition
- [Public API Contract](PUBLIC_API_CONTRACT.md) - API stability guarantees
- [Release Governance](RELEASE_GOVERNANCE.md) - Version management policy

**Last Updated:** December 6, 2025  
**Maintainer:** David Van Aelst
