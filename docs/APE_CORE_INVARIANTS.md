# APE Core Invariants Test Suite

**Created**: December 10, 2025  
**Purpose**: Provider-agnostic tests encoding APE's fundamental guarantees  
**Location**: `packages/ape/tests/runtime/test_invariants_*.py`

---

## Overview

This test suite encodes the **core APE invariants** that ALL provider adapters (Anthropic, OpenAI, LangChain, etc.) must rely on. These tests are:

- ✅ **Provider-agnostic**: No SDK dependencies (no anthropic, openai, langchain imports)
- ✅ **Self-contained**: No network access, no real API calls, no environment variables
- ✅ **Fast & deterministic**: Suitable for CI/CD pipelines
- ✅ **Specification-like**: Each test documents a guarantee in natural language

---

## Test Files

### 1. `test_invariants_executor.py` (11 tests)
**Module**: `ape.runtime.core.ApeModule`

Tests the fundamental execution model that all provider adapters use:

#### A. Dict-Based Invocation (7 tests)
- `test_simple_function_execution`: Primitive params → primitive result
- `test_nested_dict_inputs`: Nested dict/list structures preserved
- `test_missing_required_parameter_raises_error`: Missing params fail deterministically
- `test_extra_unknown_parameters`: Extra params rejected
- `test_zero_parameter_function_with_empty_dict`: Zero-param functions work with `{}`
- `test_zero_parameter_function_rejects_extra_params`: Zero-param functions reject any params
- `test_function_exception_propagates`: Exceptions propagate with original info

#### B. Function Discovery (4 tests)
- `test_list_functions`: `ApeModule.list_functions()` returns all callables
- `test_get_function_signature`: Returns complete `FunctionSignature` metadata
- `test_get_nonexistent_function_raises_keyerror`: Non-existent signature → KeyError
- `test_call_nonexistent_function_raises_attributeerror`: Non-existent call → AttributeError

**Key Guarantee**: All providers can invoke APE functions via `module.call(name, **kwargs)` with predictable error handling.

---

### 2. `test_invariants_schema.py` (10 tests)
**Module**: `ape.runtime.core.FunctionSignature`

Tests the schema/type system that providers use for introspection:

#### A. FunctionSignature Structure (4 tests)
- `test_function_signature_structure`: Required fields (name, inputs, output, description)
- `test_function_signature_no_parameters`: Zero-parameter functions have empty `inputs`
- `test_function_signature_no_output`: Void functions have `output=None`
- `test_function_signature_no_description`: Description is optional

#### B. Type System (3 tests)
- `test_primitive_types_are_strings`: All type names are strings
- `test_common_ape_types_recognized`: Core types (str, int, float, bool, list, dict)
- `test_complex_type_annotations_preserved`: Complex types as string representations

#### C. Signature Validation (3 tests)
- `test_signature_with_all_fields`: Complete signature structure
- `test_signature_inputs_must_be_dict`: `inputs` is always `Dict[str, str]`
- `test_multiple_parameters_order_preserved`: Parameter order consistency (Python 3.7+)

**Key Guarantee**: Providers can introspect function signatures via `module.get_function_signature(name)` and map APE types to their format (JSON Schema, TypeScript, etc.).

---

### 3. `test_invariants_utils.py` (19 tests)
**Module**: Provider-agnostic formatters (helpers defined in test file)

Tests the output formatting patterns that providers use:

#### A. Result Formatting (11 tests)
- `test_format_primitive_*`: Int, float, string, bool serialization
- `test_format_null_none`: None/null handling
- `test_format_list_result`: List preservation as JSON arrays
- `test_format_dict_result`: Dict preservation as JSON objects
- `test_format_nested_structure`: Deep nesting preserved
- `test_format_empty_list/dict`: Empty containers valid
- `test_format_non_serializable_object_fallback`: `str()` fallback for non-JSON types

#### B. Error Formatting (5 tests)
- `test_format_exception_basic`: Exception → `{"error": "Type: message"}`
- `test_format_exception_preserves_type`: Exception type included
- `test_format_exception_includes_message`: Message preserved
- `test_format_exception_json_serializable`: Always valid JSON (special chars handled)
- `test_format_exception_empty_message`: Empty messages handled

#### C. Output Structure (3 tests)
- `test_result_has_result_key`: Success → `{"result": ...}`
- `test_error_has_error_key`: Error → `{"error": ...}`
- `test_result_and_error_are_mutually_exclusive`: Never both keys present

**Key Guarantee**: Providers can format results/errors consistently using `{"result": value}` / `{"error": message}` patterns.

---

## Running the Tests

### Run only invariant tests:
```bash
cd packages/ape
pytest tests/runtime/test_invariants_executor.py \
       tests/runtime/test_invariants_schema.py \
       tests/runtime/test_invariants_utils.py -v
```

### Run with coverage:
```bash
pytest tests/runtime/test_invariants_*.py --cov=ape.runtime.core --cov-report=term
```

### Quick validation:
```bash
pytest tests/runtime/test_invariants_*.py -q
# Expected: 40 passed in <1s
```

---

## What These Tests Guarantee

### For Provider Adapter Developers

If you're building a new provider adapter (e.g., `ape-vertex`, `ape-azure`), these tests document what you can rely on:

1. **Execution Model**:
   - Call APE functions via `ApeModule.call(function_name, **kwargs)`
   - Pass parameters as dict
   - Expect TypeError for missing/extra params
   - Exceptions propagate (may be wrapped, but cause preserved)

2. **Schema/Type System**:
   - Introspect via `ApeModule.get_function_signature(name)`
   - Returns `FunctionSignature(name, inputs, output, description)`
   - All types are strings (map to your format)
   - Core types: str, int, float, bool, list, dict

3. **Output Formatting**:
   - Success: `{"result": <value>}` (JSON-serializable)
   - Error: `{"error": "<Type>: <message>"}` (JSON-serializable)
   - Never both keys present
   - Non-serializable objects → `str()` fallback

### For APE Core Developers

These tests are **contracts** that must remain stable across v1.x releases:

- ⚠️ **Breaking changes to these behaviors require major version bump**
- ✅ You can add new optional features (e.g., type validation, async support)
- ✅ You can optimize internals (e.g., caching, lazy loading)
- ❌ You cannot change function call semantics, signature structure, or error types

---

## Coverage Summary

| Test File | Tests | Lines | Coverage |
|-----------|-------|-------|----------|
| test_invariants_executor.py | 11 | 250 | `ape.runtime.core.ApeModule` |
| test_invariants_schema.py | 10 | 180 | `ape.runtime.core.FunctionSignature` |
| test_invariants_utils.py | 19 | 290 | Formatting patterns (documented) |
| **TOTAL** | **40** | **720** | Core execution layer |

---

## Relationship to Provider-Specific Tests

### Anthropic (`packages/ape-anthropic/tests/`)
- **49 tests**: Anthropic SDK integration (mocked)
- **Depends on**: These 40 invariant tests
- **Adds**: Claude-specific JSON Schema conversion, API client mocking

### OpenAI (`packages/ape-openai/tests/`)
- **TODO**: Implement following same pattern
- **Should depend on**: These 40 invariant tests
- **Should add**: OpenAI function calling specifics, API client mocking

### LangChain (`packages/ape-langchain/tests/`)
- **TODO**: Implement following same pattern
- **Should depend on**: These 40 invariant tests
- **Should add**: LangChain tool/chain integration specifics

---

## Design Principles

These tests follow strict guidelines:

1. **Evidence-first**: Based on actual repository structure, not assumptions
2. **No external dependencies**: Only core APE modules
3. **Self-documenting**: Each test has explicit docstring explaining the invariant
4. **Arrange/Act/Assert**: Clear test structure with comments
5. **Fast execution**: All 40 tests run in <1 second
6. **Deterministic**: No randomness, no time-dependent behavior
7. **CI-friendly**: No network, no environment variables, no cleanup needed

---

## Maintenance

### When to Update These Tests

✅ **Add tests when**:
- New core execution features are added (e.g., async support)
- New type system features are added (e.g., generics, unions)
- New formatting requirements emerge

❌ **Do NOT modify tests when**:
- Implementing provider-specific features
- Adding optimizations (if behavior unchanged)
- Refactoring internals (if API unchanged)

### Version Compatibility

- **APE v1.0.0 - v1.x.x**: These invariants are stable
- **APE v2.0.0**: May introduce breaking changes (document explicitly)

---

## Contact

For questions about these invariants or how to implement a new provider adapter:
- See `ANTHROPIC_TEST_ANALYSIS.md` for reference implementation
- Check provider adapter examples: `packages/ape-anthropic/`, `packages/ape-openai/`
- File issues at: https://github.com/Quynah/ape-lang/issues

---

**Last Updated**: December 10, 2025  
**Test Status**: ✅ 40/40 passing  
**Coverage**: Core execution layer (`ape.runtime.core`)
