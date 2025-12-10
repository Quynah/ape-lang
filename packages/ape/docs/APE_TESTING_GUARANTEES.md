# APE Testing & Guarantees

## Scope of This Document

This document describes what APE explicitly tests and guarantees through its test suites. It complements the test count statistics found in README files by explaining **what behaviour** each test suite enforces, which **regressions** they prevent, and which areas are **intentionally excluded**.

This is an evidence-based contract: every guarantee listed here maps to real test suites in the repository.

---

## What APE Explicitly Tests and Guarantees

### Language & Runtime Guarantees

**Deterministic Execution**
- APE runtime executes the same source code identically across multiple runs (no randomness, no nondeterminism)
- Control flow evaluation produces identical results when executed 10 times with identical inputs
- **Enforced by:** `tests/runtime/test_control_flow.py::TestExecutionStability`
- **Enforced by:** `tests/runtime/test_control_flow.py::TestRuntimeSafety::test_deterministic_execution`

**No Eval/Exec Injection**
- APE runtime does NOT use Python's `eval()` or `exec()` for execution
- All code execution uses AST-based interpretation only
- **Enforced by:** `tests/runtime/test_control_flow.py::TestRuntimeSafety::test_no_exec_used`

**Context Isolation**
- Execution contexts are isolated (changes in one context do not affect others)
- Child scopes do not pollute parent scopes
- **Enforced by:** `tests/runtime/test_control_flow.py::TestRuntimeSafety::test_context_isolation`
- **Enforced by:** `tests/runtime/test_control_flow.py::TestNestedControlFlow::test_nested_scope_isolation`

---

### Control Flow Guarantees

**If/Else Correctness**
- `if` statements evaluate conditions correctly and execute the correct branch
- `elif` chains are evaluated in order and stop at first true condition
- `else` branches execute only when all prior conditions are false
- **Enforced by:** `tests/runtime/test_control_flow.py::TestRuntimeExecution` (7 tests)
- **Enforced by:** `tests/runtime/test_control_flow.py::TestControlFlowParsing` (5 tests)

**Nested Control Flow**
- Nested `if` statements (up to 3 levels deep) execute correctly
- Inner branches do not interfere with outer branch evaluation
- **Enforced by:** `tests/runtime/test_control_flow.py::TestNestedControlFlow` (4 tests)

**Return Statement Propagation**
- `return` inside `if` or `else` branches correctly exits execution
- Return values propagate through control flow via `ReturnValue` exception
- **Enforced by:** `tests/runtime/test_control_flow.py::TestReturnInsideControlFlow` (3 tests)

**Loop Execution**
- `while` loops execute body in same context (variable updates persist across iterations)
- `for` loops iterate over collections with correct variable scoping
- Both loop types enforce iteration limits (`MaxIterationsExceeded` safety)
- **Enforced by:** `tests/runtime/test_control_flow.py::TestRuntimeExecution` (4 tests)
- **Enforced by:** `tests/runtime/test_control_flow.py::TestExecutionStability::test_while_loop_10x_identical`

**Boolean Expression Evaluation**
- All comparison operators work correctly: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Boolean literals (`true`, `false`) evaluate correctly
- String and numeric comparisons both supported
- **Enforced by:** `tests/runtime/test_control_flow.py::TestBooleanExpressions` (3 tests)

**Malformed Syntax Detection**
- Parser detects missing colons in `if` statements
- Parser detects missing conditions
- Dangling `else` binds to nearest `if` (Python semantics)
- **Enforced by:** `tests/runtime/test_control_flow.py::TestNegativeControlFlow` (3 tests)

---

### Execution & Error Semantics

**Parameter Validation**
- Missing required parameters raise `TypeError` with clear message
- Extra unknown parameters are rejected with error
- Zero-parameter functions accept empty input and reject extra parameters
- **Enforced by:** `tests/runtime/test_invariants_executor.py::TestExecutorDictBasedInvocation` (7 tests)

**Exception Propagation**
- Exceptions raised inside APE functions propagate to caller
- Exception types and messages are preserved
- **Enforced by:** `tests/runtime/test_invariants_executor.py::TestExecutorDictBasedInvocation::test_function_exception_propagates`

**Function Discovery**
- APE modules enumerate available functions via `list_functions()`
- Function signatures are retrievable via `get_function_signature()`
- Nonexistent functions raise appropriate errors
- **Enforced by:** `tests/runtime/test_invariants_executor.py::TestExecutorFunctionDiscovery` (4 tests)

**Nested Data Handling**
- APE functions correctly process nested dictionaries and lists
- Nested structures are passed without flattening or corruption
- **Enforced by:** `tests/runtime/test_invariants_executor.py::TestExecutorDictBasedInvocation::test_nested_dict_inputs`

---

### Type & Schema Guarantees

**Function Signature Structure**
- Signatures always contain `name`, `inputs`, `outputs`, `description` keys
- `inputs` and `outputs` are dictionaries mapping parameter names to types
- Empty inputs/outputs are represented as empty dicts
- **Enforced by:** `tests/runtime/test_invariants_schema.py::TestFunctionSignatureInvariants` (4 tests)

**Primitive Type Representation**
- Primitive types are represented as strings: `"Integer"`, `"String"`, `"Boolean"`, `"Float"`
- Type annotations are preserved exactly as declared
- **Enforced by:** `tests/runtime/test_invariants_schema.py::TestTypeSystemInvariants` (3 tests)

**Complex Type Annotations**
- List types: `"List[Integer]"` (collections with element types)
- Map types: `"Map[String, Integer]"` (key-value pairs with types)
- Tuple types: `"Tuple[Integer, String]"` (fixed-size heterogeneous)
- Nested types: `"List[Map[String, Integer]]"` (arbitrary nesting)
- **Enforced by:** `tests/runtime/test_invariants_schema.py::TestTypeSystemInvariants::test_complex_type_annotations_preserved`

**Parameter Order Preservation**
- Multiple input parameters maintain declaration order in signature
- Order is preserved through serialization/deserialization
- **Enforced by:** `tests/runtime/test_invariants_schema.py::TestSignatureValidation::test_multiple_parameters_order_preserved`

**Structured Type Operations**
- Lists: creation, indexing, iteration, membership, equality, concatenation, bounds checking
- Maps: creation, get/set, key-not-found errors, type validation
- Tuples: creation, indexing, iteration, equality, hashability, immutability
- Records: field access, type validation, nested structures
- **Enforced by:** `tests/types/test_structured_types.py` (28 tests)

---

### Output Guarantees

**Result Formatting**
- Primitives (int, float, string, bool, None) serialize correctly
- Lists and dictionaries serialize recursively
- Empty collections serialize as `[]` and `{}`
- Nested structures serialize without data loss
- **Enforced by:** `tests/runtime/test_invariants_utils.py::TestResultFormattingInvariants` (9 tests)

**Non-Serializable Fallback**
- Objects that cannot be JSON-serialized fall back to string representation
- Fallback preserves type information via `str(obj)`
- **Enforced by:** `tests/runtime/test_invariants_utils.py::TestResultFormattingInvariants::test_format_non_serializable_object_fallback`

**Error Formatting**
- Exceptions are formatted as dicts with `error` key
- Error dicts contain `type` (exception class name) and `message` keys
- Error format is JSON-serializable
- Empty exception messages are handled gracefully
- **Enforced by:** `tests/runtime/test_invariants_utils.py::TestErrorFormattingInvariants` (5 tests)

**Result/Error Mutual Exclusivity**
- Successful results have `result` key (no `error` key)
- Failed executions have `error` key (no `result` key)
- Result and error never appear together in output
- **Enforced by:** `tests/runtime/test_invariants_utils.py::TestOutputStructureInvariants` (3 tests)

---

### Observability & Introspection Guarantees

**Execution Tracing**
- Runtime records enter/exit events for all major AST nodes
- Trace events capture context snapshots (variable state at each step)
- Trace collectors are queryable and iterable
- **Enforced by:** `tests/runtime/test_observability.py::TestExecutionTracing` (multiple tests)

**Dry-Run Mode**
- Dry-run mode executes without side effects
- Control flow is evaluated but side-effecting operations are skipped
- Results are marked as dry-run in output
- **Enforced by:** `tests/runtime/test_observability.py::TestDryRun` (multiple tests)

**Capability Gating**
- Runtime enforces capability requirements (e.g., `network`, `filesystem`)
- Operations requiring unavailable capabilities raise `CapabilityError`
- Capability checks happen before execution
- **Enforced by:** `tests/runtime/test_observability.py::TestCapabilities` (multiple tests)

**Execution Explanation**
- `ExplanationEngine` converts traces into human-readable steps
- Explanations describe what happened (condition evaluations, variable changes)
- **Enforced by:** `tests/runtime/test_introspection.py::TestExplanationEngine` (multiple tests)

**Execution Replay**
- `ReplayEngine` can re-execute from recorded traces
- Replay validates that re-execution produces identical results
- **Enforced by:** `tests/runtime/test_introspection.py::TestReplayEngine` (multiple tests)

**Runtime Profiles**
- Predefined profiles (e.g., `strict`, `permissive`) configure execution behaviour
- Profiles control capabilities, iteration limits, dry-run defaults
- Custom profiles can be registered and validated
- **Enforced by:** `tests/runtime/test_introspection.py::TestRuntimeProfiles` (multiple tests)

---

### Standard Library Guarantees

**Logic Operations**
- `assert`, `all_true`, `any_true`, `none_true`, `equals`, `not_equals`
- Type validation for all logic operations
- **Enforced by:** `tests/std/test_stdlib_core.py::TestLogicModule` (17 tests)

**Collection Operations**
- `count`, `is_empty`, `contains`, `filter_items`, `map_items`, `reduce_items`
- Works on lists and other iterables
- Type validation for collection operations
- **Enforced by:** `tests/std/test_stdlib_core.py::TestCollectionsModule` (multiple tests)

**Math Operations**
- Basic arithmetic: `add`, `subtract`, `multiply`, `divide`
- Comparisons: `greater_than`, `less_than`
- Rounding, absolute value, min/max
- **Enforced by:** `tests/std/test_math.py` (10 tests)

**String Operations**
- Concatenation, substring extraction, case conversion
- String length, trimming, splitting
- **Enforced by:** `tests/std/test_stdlib_core.py::TestStringModule` (multiple tests)

**I/O Operations**
- `read_file`, `write_file`, `print_output`
- Path validation and capability gating
- **Enforced by:** `tests/std/test_io.py` (14 tests)

---

### Module & Import Guarantees

**Module Resolution**
- Modules are resolved from standard library (`ape_std/`) and local directories
- Import paths support relative (`./module`) and absolute references
- Circular imports are detected and prevented
- **Enforced by:** `tests/linker/test_linker_basic.py` (13 tests)
- **Enforced by:** `tests/linker/test_linker_cycles.py` (9 tests)

**Import Syntax**
- `import module` and `from module import function` both supported
- Imported symbols are accessible in execution context
- Unknown imports raise clear errors
- **Enforced by:** `tests/parser/test_modules_and_imports.py` (25 tests)

**Code Generation for Imports**
- Python codegen correctly translates APE imports to Python imports
- Namespacing prevents symbol collisions
- **Enforced by:** `tests/codegen/python/test_namespaced_calls.py` (15 tests)

---

### Multi-Language Guarantees

**Language Normalization**
- Source code in non-English languages is normalized to canonical English form
- Semantic keywords (`task`, `if`, `return`) have translations
- Execution behaviour is identical across languages
- **Enforced by:** `tests/lang/test_multilanguage.py` (29 tests)

**Supported Languages**
- English (`en`) is the canonical language
- Dutch (`nl`), German (`de`), French (`fr`) translations exist
- **Enforced by:** `tests/lang/test_multilanguage.py`

---

### Integration & End-to-End Guarantees

**Evidence Scenarios**
- Real-world APE programs (control flow + stdlib + runtime) execute correctly
- Examples: risk classification, calculator, email policy
- **Enforced by:** `tests/evidence/test_evidence_scenarios.py` (13 tests)

**Example Execution**
- All examples in `examples/` directory parse and execute without errors
- Examples demonstrate canonical usage patterns
- **Enforced by:** `tests/examples/` (21 tests across multiple scenarios)

**Tutorial Execution**
- All tutorial code in `tutorials/` directory executes successfully
- Tutorials are kept in sync with runtime behaviour
- **Enforced by:** `tests/tutorials/test_tutorials_execute.py` (46 tests)

---

## Provider Adapter Guarantees

**Adapter Compliance**

Provider adapters (Anthropic, OpenAI, LangChain) do NOT define new execution semantics. They are tested for compliance with the core APE guarantees listed above.

**Anthropic** (`packages/ape-anthropic/`)
- Behavioural reference implementation
- Tests executor, schema, generator, utils, end-to-end scenarios
- **Test path:** `packages/ape-anthropic/tests/`
- **Test files:** `test_executor.py`, `test_schema.py`, `test_generator.py`, `test_utils.py`, `test_end_to_end.py`

**OpenAI** (`packages/ape-openai/`)
- Mirrors Anthropic guarantees for OpenAI API
- Tests same contract: executor, schema, generator, utils, end-to-end
- **Test path:** `packages/ape-openai/tests/`
- **Test files:** `test_executor.py`, `test_schema.py`, `test_generator.py`, `test_utils.py`, `test_end_to_end.py`

**LangChain** (`packages/ape-langchain/`)
- Mirrors Anthropic guarantees for LangChain integration
- Tests same contract: executor, schema, generator, utils, end-to-end
- **Test path:** `packages/ape-langchain/tests/`
- **Test files:** `test_executor.py`, `test_schema.py`, `test_generator.py`, `test_utils.py`, `test_end_to_end.py`

**Adapter Guarantees:**
- All adapters validate parameter presence (missing params → error)
- All adapters validate parameter types (wrong types → error)
- All adapters propagate execution errors with context
- All adapters produce identical result/error structure
- All adapters support zero-parameter functions

**Evidence:** Each adapter has ~5 identical test files verifying the same contract.

---

## What Is Intentionally NOT Tested

**Performance & Benchmarks**
- Execution speed, memory usage, throughput
- **Reason:** Performance is observable but not guaranteed; optimizations are ongoing

**Streaming Behaviour**
- Token-by-token streaming from LLM APIs
- **Reason:** Streaming is provider-specific and does not affect correctness

**Provider-Specific Model Behaviour**
- Claude vs GPT-4 output differences
- Model version updates
- **Reason:** APE guarantees execution semantics, not AI output quality

**Rate Limits & Network Resilience**
- API rate limiting, retries, backoff strategies
- **Reason:** Network failures are external to APE semantics

**AI Hallucination Correctness**
- Whether LLM outputs are factually correct
- **Reason:** APE ensures structured execution, not content accuracy

**Fuzzing & Adversarial Inputs**
- Random malformed inputs, exploit attempts
- **Reason:** Security hardening is ongoing; basic validation is tested

**Concurrency & Parallelism**
- Multi-threaded execution, async patterns
- **Reason:** Current runtime is single-threaded by design

**Backward Compatibility (breaking changes)**
- APE is pre-1.0; breaking changes are expected
- **Reason:** Stability guarantees begin at 1.0 release

---

## How to Use This Document

**For Contributors:**
- When adding a feature, add corresponding tests to enforce guarantees
- If you cannot write a test for a guarantee, mark it as "Implicit / currently unproven"
- Update this document when new guarantees are added

**For Users:**
- A failed test indicates a violated guarantee
- If a guarantee is not listed here, it is not explicitly tested
- Test counts (e.g., "539 tests") are in README files; this document explains what those tests guarantee

**For Maintainers:**
- This document is the canonical reference for APE's tested behaviour
- All documented guarantees must map to real test files
- Exclusions should be honest and intentional

---

## Running Tests

**Core APE Tests:**
```bash
cd packages/ape
pytest                              # Run all tests
pytest tests/runtime/               # Run specific category
pytest -v --tb=short                # Verbose with short tracebacks
```

**Provider Adapter Tests:**
```bash
cd packages/ape-anthropic
pytest

cd packages/ape-openai
pytest

cd packages/ape-langchain
pytest
```

**All Tests (from monorepo root):**
```bash
pytest packages/ape/tests/
pytest packages/ape-anthropic/tests/
pytest packages/ape-openai/tests/
pytest packages/ape-langchain/tests/
```

**Verify Test Counts:**
```bash
# From monorepo root
python scripts/count_tests.py
```

---

**Last Updated:** December 10, 2025  
**Test Suite Version:** v1.0.3  
**Total Core Tests:** 611 collected (539 passing, 72 skipped)
