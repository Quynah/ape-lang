# APE Evidence Scenarios — Early Adopter Proof Suite

## 📋 Overview

This directory contains **evidence-based test scenarios** that demonstrate APE's core guarantees to early adopters. Unlike unit tests that verify individual components, these scenarios are **complete, runnable APE programs** that prove real-world capabilities.

**Design Philosophy:**
- ✅ **APE-first**: `.ape` files are primary artifacts, Python is subordinate
- ✅ **No new features**: Uses existing v1.0.0 capabilities only
- ✅ **Combined guarantees**: Each scenario tests multiple dimensions simultaneously
- ✅ **Observable**: All scenarios include tracing and explanation

## 🎯 Evidence Dimensions

### 1. Control Flow (`risk_classification.ape`)
**Proves:** Conditional logic, sequential execution, variable scoping

```ape
task main:
    inputs:
        x: Integer
        y: Integer
    steps:
        - set total to 0
        if x > 0:
            - set total to total + 10
        if y > 1:
            - set total to total + 20
```

**Tests:**
- `test_risk_classification_e2e`: End-to-end execution
- `test_risk_classification_trace_completeness`: Trace captures all decision points

### 2. Multi-Language Equivalence (`multilanguage_equivalence.ape`)
**Proves:** Language-agnostic semantics, same AST regardless of English/Dutch syntax

**Tests:**
- `test_multilanguage_semantic_equivalence`: Same results from EN/NL
- `test_multilanguage_trace_equivalence`: Identical traces across languages

### 3. Dry-Run Governance (`dry_run_governance.ape`)
**Proves:** Safe analysis without mutations, "deciding without executing"

**Tests:**
- `test_dry_run_prevents_mutation_but_executes_logic`: Logic runs, state doesn't change
- `test_dry_run_vs_normal_execution_comparison`: Dry-run vs normal mode

### 4. Observability Flow (`observability_flow.ape`)
**Proves:** Explainable control flow, human-readable trace generation

**Tests:**
- `test_explanation_describes_control_flow`: Trace → readable explanation
- `test_observability_trace_structure`: Enter/exit pairing correctness

### 5. Replay Integrity (`replay_integrity.ape`)
**Proves:** Deterministic execution, tamper detection, reproducibility

**Tests:**
- `test_replay_validates_determinism`: Replay engine validates traces
- `test_replay_detects_tampering`: Modified traces are detected
- `test_determinism_across_runs`: Same input → identical traces

## 📊 Test Results

```
13 passed in 0.14s
393 total tests passing (380 baseline + 13 evidence)
```

## 🔧 Running Evidence Tests

```powershell
# All evidence tests
pytest tests/evidence/test_evidence_scenarios.py -v

# Specific dimension
pytest tests/evidence/test_evidence_scenarios.py::TestReplayIntegrity -v

# Integration tests
pytest tests/evidence/test_evidence_scenarios.py::TestEvidenceIntegration -v
```

## 📂 File Structure

```
tests/evidence/
├── README.md                       # This file
├── test_evidence_scenarios.py      # Test runner (Python)
└── ape/                            # APE scenario files
    ├── risk_classification.ape
    ├── multilanguage_equivalence.ape
    ├── dry_run_governance.ape
    ├── observability_flow.ape
    └── replay_integrity.ape
```

## 🎓 For Early Adopters

These scenarios demonstrate that APE v1.0.0 can:

1. **Execute complex logic** with conditionals and sequential steps
2. **Work identically** in English or Dutch (or any future language)
3. **Analyze safely** without side effects (dry-run mode)
4. **Explain decisions** with human-readable traces
5. **Guarantee determinism** with replay validation

Each `.ape` file is a **standalone proof** that can be:
- Run independently (`python -m ape run tests/evidence/ape/risk_classification.ape`)
- Traced and explained
- Replayed for validation
- Used as documentation examples

## 🔬 Technical Notes

**Input Handling:**
All scenarios use `inputs:` declarations. The Python test runner provides input values via `ExecutionContext.set()`. This ensures variables exist before task execution begins.

**Step Semantics:**
Steps like `- set x to value` are **natural language descriptions**, not executable code. They parse as `StepNode` but don't mutate context. For actual variable assignment, use the `inputs:` mechanism.

**Trace Recording:**
All tests pass a `TraceCollector` to the executor. Traces capture:
- Enter/exit events for all control structures
- Node types (IfNode, TaskDefNode, etc.)
- Execution phases
- Context snapshots (future enhancement)

**Explanation Generation:**
`ExplanationEngine.from_trace()` converts low-level trace events into high-level `ExplanationStep` objects with human-readable summaries.

## 📚 Related Documentation

- [APE 1.0 Specification](../../spec/APE_Spec_v0.1.md)
- [Runtime Documentation](../../src/ape/runtime/README.md)
- [Tracing & Observability](../../docs/observability.md)
- [Standard Library](../../docs/stdlib.md)

---

**Version:** APE v1.0.0  
**Last Updated:** 2024 (Evidence Scenarios Release)  
**Status:** ✅ All tests passing (393 total)
