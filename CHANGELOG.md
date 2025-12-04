# Changelog

## v0.1.0 — Initial prototype

**Core language**

- Basic Ape syntax implemented:
  - `entity`
  - `task`
  - `flow`
  - `enum`
  - `policy`
- Indent-based structure (like Python/YAML) with fixed indentation rules.
- Natural-language `steps` blocks for tasks and flows.

**Compiler pipeline**

- Tokenizer + parser + AST
- IR builder (Module/Entity/Task/Flow/Enum/Policy/Deviation IR-nodes)
- SemanticValidator:
  - check for duplicate definitions
  - type verification for entities, tasks, enums
  - validation of policies
- StrictnessEngine:
  - detection of ambiguity in steps
  - prohibition of implicit choices without declaration
  - integration with CDS (Controlled Deviation System)

**Controlled Deviation System (CDS)**

- Introduction of `allow deviation:` blocks in `constraints`:
  - `scope`
  - `mode`
  - `bounds`
  - optional `rationale`
- Parser → `DeviationNode` in AST/IR.
- Semantic validation on:
  - valid `scope` and `mode` values
  - non-empty `bounds`
- Strictness-engine:
  - treats deviations within CDS as legal
  - keeps all ambiguity outside CDS forbidden

**Code generation & runtime**

- PythonCodeGenerator:
  - entities → dataclasses
  - enums → simple Python classes/constants
  - tasks → functions with type hints + docstrings (incl. constraints/deviation info)
  - flows → orchestration functions + metadata
  - policies → Python structures
- Minimalistic runtime (`aperuntime`):
  - `RunContext` as basis for flows and future runtime hooks

**CLI**

- `python -m ape` entrypoint with subcommands:
  - `ape parse <file>` – inspect AST
  - `ape ir <file>` – display IR as JSON-like structure
  - `ape validate <file>` – Semantic + strictness validation
  - `ape build <file> --target=python --out-dir=...` – generate Python code
- Exit codes:
  - `0` on success
  - `1` on validation/build errors

**Examples**

- `examples/calculator_basic.ape`  
  - deterministic calculator (no deviation)
- `examples/calculator_smart.ape`  
  - calculator with Controlled Deviation for human-readable summary
- `examples/email_policy_basic.ape`  
  - simple email threat level scenario with enum, entities, task and policy

**Tests**

- Complete test suite (~80 tests) for:
  - tokenizer & parser
  - IR-builder
  - semantic validation (valid + invalid cases)
  - strictness-engine (ambiguous vs allowed deviation)
  - code generator (valid Python syntax, type mapping)
  - CLI (parse/ir/validate/build)
  - examples (calculators + email policy) end-to-end
