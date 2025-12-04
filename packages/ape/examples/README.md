# Ape Examples

This directory contains example Ape programs that demonstrate the language.

## 1. Calculator Basic (`calculator_basic.ape`)

A fully deterministic calculator example.

### Purpose

This example serves as:
- **Demo** of Ape syntax and semantics
- **Regression test** for the complete pipeline
- **Reference** for entities, enums, tasks and flows
- **Proof** that the strict Ape philosophy works

### Philosophy

This example demonstrates the core principles of Ape:

> "What is allowed, is fully allowed.  
> What is forbidden, is strictly forbidden.  
> What is not declared, does not exist."

The calculator is:
- ✅ **Fully deterministic** - no randomness, no ambiguity
- ✅ **No controlled deviation** - purely strict semantics
- ✅ **Explicitly declared** - all types, inputs, outputs known
- ✅ **Type-safe** - all fields have concrete types

## 2. Calculator Smart (`calculator_smart.ape`)

Demonstrates the **Controlled Deviation System (CDS)** from RFC-0001.

### Purpose

This example demonstrates:
- **Controlled Deviation** - explicit flexibility within bounds
- **Mixed determinism** - strict for calculations, creative for presentation
- **Bounds and rationale** - documentation why deviation is needed
- **Practical application** of the CDS framework

### Unique Features

The `calculate_smart` task:
- ✅ **Deterministic result** - calculation is exact
- ✅ **Creative summary** - human summary can vary
- ✅ **Explicit bounds** - what can vary is strictly defined
- ✅ **Rationale** - explains why flexibility is needed

This shows how Ape combines both worlds:
- Strict determinism where needed (calculation)
- Controlled flexibility where desired (presentation)

### CDS Example

```ape
constraints:
    - deterministic
    - allow deviation:
        scope: steps
        mode: creative
        bounds:
            - result.result must always equal the mathematically correct outcome
            - summary must describe the operation and result
            - no additional side effects are allowed
        rationale: "Formatting of the human-readable summary can vary"
```

## Shared Structure (both calculators)

### Enum: Operation
Defines the allowed operations:
- `add`
- `subtract`
- `multiply`
- `divide`

### Entity: CalculationRequest
Input for a calculation:
- `left: Float` - left operand
- `right: Float` - right operand
- `op: Operation` - operation

### Entity: CalculationResult
Output of a calculation:
- `left: Float` - left operand (copied)
- `right: Float` - right operand (copied)
- `op: Operation` - operation (copied)
- `result: Float` - calculation result

### Task: calculate
Performs one calculation:
- **Input:** `request: CalculationRequest`
- **Output:** `result: CalculationResult`
- **Constraint:** deterministic
- **Steps:** 8 explicit steps (no ambiguity)

### Flow: calculator_demo
Demo orchestration flow:
- **Steps:** 3 steps
- **Constraint:** deterministic
- Shows how tasks are called

## Test Results

```
✅ test_parse_and_ir - Parser and IR builder work correctly
✅ test_semantic_and_strictness_valid - No validation errors
✅ test_codegen_calculator - Generates valid Python code
✅ test_calculator_deterministic_constraints - Determinism guaranteed
✅ test_no_deviation_used - No controlled deviation used
✅ test_calculator_as_regression_test - Regression test passes
✅ test_complete_pipeline - Complete pipeline works
```

**7/7 tests passing**

## Generated Python

The generated Python file (`calculator_basic_gen.py`) contains:

```python
class Operation:
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

@dataclass
class CalculationRequest:
    left: float
    right: float
    op: "Operation"

@dataclass
class CalculationResult:
    left: float
    right: float
    op: "Operation"
    result: float

def calculate(request: "CalculationRequest") -> "CalculationResult":
    # ... deterministic implementation
    raise NotImplementedError
```

The code is:
- ✅ Syntactically correct Python
- ✅ Type-safe with type hints
- ✅ Compilable
- ✅ Executable (with NotImplementedError placeholder)

## Use as Regression Test

Both calculators are used as regression tests for:

1. **Parser** - Correctly parsing entities, enums, tasks, flows
2. **IR Builder** - Correctly building intermediate representation
3. **Semantic Validator** - Type checking, symbol resolution
4. **Strictness Engine** - Determinism checking, ambiguity detection
5. **Python Codegen** - Correct Python code generation

With every change to these components, all calculator tests must pass.

## Pipeline Verification

```bash
# Run all calculator tests
python -m pytest tests/examples/ -v

# Run basic calculator tests
python -m pytest tests/examples/test_calculator_basic.py -v

# Run smart calculator tests (with CDS)
python -m pytest tests/examples/test_calculator_smart.py -v

# Run complete test suite
python -m pytest tests/ -v

# Generate Python code
python -c "from examples import generate; generate('calculator_basic.ape')"
python -c "from examples import generate; generate('calculator_smart.ape')"
```

## Test Overview

```
Calculator Basic:   7 tests - Pure determinism
Calculator Smart:   7 tests - Controlled deviation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Examples:    14 tests - Both philosophies
```

## Why Two Calculators?

### Calculator Basic
- **No deviation** - fully deterministic
- Shows the **strict core** of Ape
- Ideal for beginners
- Pure type safety demonstration

### Calculator Smart
- **With deviation** - controlled flexibility
- Shows **RFC-0001 Controlled Deviation System**
- Practical application of bounds and rationale
- Mix of strict + creative

Together they demonstrate the full range of Ape's capabilities.
