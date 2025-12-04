# Changelog

## v0.2.0 — Module System & Standard Library (2025-12-04)

**Major Features**

🎯 **Module System**
- Added `module` declaration syntax for defining importable modules
- Added `import` statement for importing other modules
- Qualified identifier support: `module.task(...)` for calling imported tasks
- Deterministic module resolution order:
  1. `./lib/` (local library directory)
  2. `./` (same directory as source file)
  3. `<APE_INSTALL>/ape_std/` (standard library)
- First match wins (no ambiguity, no fallback magic)

📦 **Linker**
- New linker component for resolving module dependencies
- Builds complete dependency graph for multi-file programs
- Detects and reports circular dependencies with full cycle path
- Topologically sorts modules for correct compilation order
- Clear error messages for missing modules, import violations, and invalid module names

🔧 **Code Generation**
- Name mangling: `<module>.<symbol>` → `<module>__<symbol>` at codegen time
- Backward compatible: files without `module` declaration work as before (no mangling)
- Module-aware code generation for Python target
- Generates one file per module in `generated/` directory

📚 **Standard Library v0.1**
- **sys module**: system operations
  - `print`: output messages to console
  - `exit`: exit program with status code
- **io module**: file and input operations
  - `read_line`: read user input with prompt
  - `write_file`: write content to file
  - `read_file`: read content from file
- **math module**: mathematical operations
  - `add`, `subtract`, `multiply`, `divide`: basic arithmetic
  - `power`: exponentiation
  - `abs`: absolute value
  - `sqrt`: square root
  - `factorial`: factorial calculation
- All stdlib tasks marked as deterministic
- Full task signatures with proper input/output types

📝 **Examples**
- `examples/hello_imports.ape`: basic module import demonstration
- `examples/stdlib_complete.ape`: showcases all three stdlib modules
- `examples/custom_lib_project/`: complete project with local library structure
  - `main.ape`: entry point importing local module
  - `lib/utils.ape`: local library module

**Parser Enhancements**
- `MODULE` and `IMPORT` tokens recognized by tokenizer
- Module declaration parsing: `module <name>`
- Import statement parsing: `import <module>`
- Qualified identifier parsing: `math.add`, `io.read_file`, etc.
- Import placement validation (must appear after `module`, before definitions)
- 25 new parser tests for modules and imports

**Semantic & IR**
- IR builder tracks module name and dependencies
- Module information preserved through compilation pipeline
- Qualified identifiers resolved correctly in semantic validation

**CLI Updates**
- All existing commands work with modular programs
- `ape build` now links dependencies and generates multiple files
- `ape validate` checks for module resolution errors

**Documentation**
- 📖 New `docs/philosophy.md`: Explains Ape's dual role as translator AND standalone language
- 📖 Comprehensive `docs/modules_and_imports.md`: Complete module system specification (1334 lines)
  - Name mangling implementation details
  - Standard library API reference
  - Error handling with real error messages (5 scenarios)
  - Complete working examples
  - Migration guide from v0.1.x
- 📖 Updated `README.md`: "What is Ape?" section and expanded v0.2.0 features
- 📖 New `docs/README.md`: Documentation index for easy navigation
- 📖 Updated `docs/codegen_namespacing.md`, `docs/linker_implementation.md`, `docs/stdlib_v0.1.md`

**Testing**
- ✅ **192 tests passing** (up from ~80 in v0.1.x)
- 25 parser tests for module/import syntax
- 22 linker tests (basic resolution + circular dependency detection)
- 15 codegen tests for name mangling
- 35 standard library tests (parsing, linking, codegen)
- 15 example integration tests (hello_imports, stdlib_complete, custom_lib_project)
- All existing v0.1.x tests continue to pass (backward compatibility confirmed)

**Backward Compatibility**
- ✅ All v0.1.x programs without `module`/`import` work unchanged
- ✅ No breaking changes to existing syntax
- ✅ Opt-in module system: add `module` declaration to make file importable

**Error Messages**
Enhanced error reporting for:
- Module not found (shows search paths attempted)
- Circular dependencies (shows complete cycle: a → b → c → a)
- Import after definition (shows correct placement)
- Missing module declaration in imported files
- Invalid module names (must be valid identifiers)

---

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
