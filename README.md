# APE Language — Monorepo

**A deterministic AI-first programming language designed for unambiguous human-AI collaboration.**

[![PyPI version](https://badge.fury.io/py/ape-lang.svg)](https://pypi.org/project/ape-lang/)
[![Tests](https://img.shields.io/badge/tests-654%20passing%20%7C%2075%20skipped-brightgreen)](#-test-suite-overview)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📦 Packages

### Core Language
**[packages/ape/](packages/ape/)** - APE compiler, runtime, and standard library

```bash
pip install ape-lang
```

- ✅ **523 passing, 72 skipped** (full compiler pipeline + control flow + tuples)
- ✅ **Multi-language support** (7 languages: EN, NL, FR, DE, ES, IT, PT)
- ✅ **Runtime observability** (tracing, explanation, replay)
- ✅ **Standard library** (logic, strings, collections, math)
- ✅ **Control flow** (if/while/for with AST-based execution)
- 📖 [**Full documentation →**](packages/ape/README.md)

### AI Integration Packages

**[packages/ape-anthropic/](packages/ape-anthropic/)** - Anthropic Claude integration
```bash
pip install ape-anthropic
```
- Executor and schema for Claude API
- **49 tests passing**

**[packages/ape-openai/](packages/ape-openai/)** - OpenAI GPT integration
```bash
pip install ape-openai
```
- Executor and schema for OpenAI API
- **49 tests passing**

**[packages/ape-langchain/](packages/ape-langchain/)** - LangChain integration
```bash
pip install ape-langchain
```
- APE-to-LangChain bridge utilities
- **20 tests** (17 passing + 3 documented skips)

---

## 🚀 Quick Start

### Installation

```bash
pip install ape-lang
```

### Your First APE Program

Create `hello.ape`:
```ape
module hello

task greet:
    inputs:
        name: String
    outputs:
        message: String
    
    constraints:
        - deterministic
    
    steps:
        - set message to "Hello, " + name + "!"
        - return message
```

### Run It

```bash
# Validate syntax and semantics
ape validate hello.ape

# Compile to Python
ape compile hello.ape

# Run with Python backend
ape run hello.ape
```

### Use Programmatically

```python
from ape import compile

# Compile APE source
module = compile("hello.ape")

# Call tasks
result = module.call("greet", name="World")
print(result)  # "Hello, World!"
```

---

## 🧪 Test Suite Overview

✅ **All core tests passing**

| Component          | Tests | Status |
|--------------------|-------|--------|
| APE Core           | 611   | ✅ 539 passing, 72 skipped |
| Anthropic Adapter  | 49    | ✅ 49 passing |
| OpenAI Adapter     | 49    | ✅ 49 passing |
| LangChain Adapter  | 20    | ✅ 17 passing, 3 skipped |
| **Total**          | **729** | **✅ 654 passing, 75 skipped** |

See [packages/ape/docs/APE_TESTING_GUARANTEES.md](packages/ape/docs/APE_TESTING_GUARANTEES.md) for details on what these tests guarantee.

**Test coverage includes:**
- Parser, lexer, and AST generation
- Linker and module resolution system
- Code generator and Python transpilation
- Standard library functions (86 functions)
- Runtime execution with control flow
- Observability and introspection
- Multi-language support (7 languages)
- Tuple returns and list operations
- Provider-specific adapters (Anthropic, OpenAI, LangChain)

**Evidence-based counting:**
All numbers derived from `pytest --collect-only` discovery. No manual counting.

To regenerate counts:
```bash
python scripts/count_tests.py
```

---

## 🎯 Core Philosophy

> **"What is allowed, is fully allowed.**  
> **What is forbidden, is strictly forbidden.**  
> **What is not declared, does not exist."**

APE is designed for **deterministic execution** and **unambiguous communication** between humans and AI:

- ✅ **Explicit over implicit** - No magic behavior
- ✅ **Fail loud, fail fast** - Clear errors, no guessing
- ✅ **Deterministic by default** - Same input → same output, always
- ✅ **AI-friendly syntax** - Consistent structure for reliable code generation
- ✅ **Dual-purpose design** - Bridge language (translator) + standalone language

---

## 📊 Repository Structure

```
ape-lang/
├── packages/
│   ├── ape/                    # Core language compiler & runtime
│   │   ├── src/ape/           # Source code
│   │   ├── tests/             # 439 tests
│   │   ├── docs/              # Documentation (300+ pages)
│   │   ├── ape_std/           # Standard library
│   │   └── examples/          # Example programs
│   ├── ape-anthropic/         # Anthropic integration
│   ├── ape-openai/            # OpenAI integration
│   └── ape-langchain/         # LangChain integration
├── demo_*.ape                 # Demo programs
└── generated/                 # Generated code output
```

---

## 🧪 Testing

APE includes a comprehensive runtime test suite covering:
- **Core type system** (Record, Map, List, Value)
- **DateTime & Duration semantics** (ISO-8601, UTC, arithmetic)
- **Collection and aggregation primitives** (group_by, unique, max/min, any/all)
- **JSON / nested data access** (dotted path navigation)

### Run All Tests

```bash
# Run core language tests (523+ tests)
cd packages/ape
pytest

# Run Decision Engine validation
pytest tests/test_datetime.py tests/test_collections.py tests/test_json_path.py

# Run integration tests
cd packages/ape-anthropic
pytest
```

**Test Results:** See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed validation evidence.

---

## 📖 Documentation

- **[Main README](packages/ape/README.md)** - Complete language documentation
- **[Philosophy](packages/ape/docs/philosophy.md)** - Design principles
- **[Module System](packages/ape/docs/modules_and_imports.md)** - Import resolution (1334 lines!)
- **[Runtime Observability](packages/ape/docs/runtime_observability.md)** - Tracing & replay
- **[Multi-Language](packages/ape/docs/multilanguage.md)** - Surface syntax variants
- **[Roadmap](packages/ape/docs/ROADMAP.md)** - Implementation status

---

## 🌍 Multi-Language Support

Write APE using keywords from your native language:

```ape
# English (canonical)
task calculate:
    inputs: x: Integer
    steps:
        if x > 0:
            - return x * 2

# Dutch
taak berekenen:
    invoer: x: Integer
    stappen:
        als x > 0:
            - return x * 2

# French
tâche calculer:
    entrées: x: Integer
    étapes:
        si x > 0:
            - return x * 2
```

All produce identical AST and runtime behavior.

---

## 🔗 Links

- **PyPI Core:** https://pypi.org/project/ape-lang/
- **PyPI Anthropic:** https://pypi.org/project/ape-anthropic/
- **PyPI OpenAI:** https://pypi.org/project/ape-openai/
- **PyPI LangChain:** https://pypi.org/project/ape-langchain/
- **GitHub:** https://github.com/Quynah/ape-lang
- **Issues:** https://github.com/Quynah/ape-lang/issues

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**David Van Aelst**

---

## 🦍 Status: v1.0.3

**Current Release:** v1.0.3 (December 2024)  
**Maturity:** Production-ready core, scaffolded advanced features  
**Tests:** 611/611 passing ✅

See [CHANGELOG](packages/ape/CHANGELOG.md) for version history
    - guest

task CreateUser:
    inputs:
        username: String
        email: String
        role: UserRole
    outputs:
        user: User
    steps:
        - validate username is not empty
        - validate email format
        - create User instance
        - assign role to user
        - return user
    constraints:
        - username must be unique

flow UserRegistrationFlow:
    steps:
        - receive registration request
        - call CreateUser task
        - send welcome email
        - return success

policy SecurityPolicy:
    rules:
        - all passwords must be hashed
        - user data must be encrypted
```

## Usage

### Complete Pipeline

```python
from apeparser import parse_ape_source, IRBuilder
from apecompiler.semantic_validator import SemanticValidator
from apecompiler.strictness_engine import StrictnessEngine
from apecodegen.python_codegen import PythonCodeGenerator
from apecompiler.ir_nodes import ProjectNode

# 1. Parse Ape source
ast = parse_ape_source(source, "example.ape")

# 2. Build IR
builder = IRBuilder()
ir_module = builder.build_module(ast, "example.ape")
project = ProjectNode(name="MyProject", modules=[ir_module])

# 3. Validate
validator = SemanticValidator()
errors = validator.validate_project(project)

# 4. Check strictness
engine = StrictnessEngine()
warnings = engine.enforce(project)

# 5. Generate Python
codegen = PythonCodeGenerator(project)
files = codegen.generate()

# 6. Save
for file in files:
    with open(file.path, 'w') as f:
        f.write(file.content)
```

### Running Demos

```bash
# Complete pipeline demo
python demo_pipeline.py

# Generate code
python example_generate.py

# Run tests
python -m pytest tests/ -v

# Test calculator example
python -m pytest tests/examples/test_calculator_basic.py -v
```

## Examples

### Calculator Examples

#### 1. Calculator Basic (`calculator_basic.ape`)
A fully deterministic calculator example that demonstrates:
- Strict type checking without ambiguity
- Deterministic constraints
- No controlled deviation
- Complete pipeline from Ape → Python

#### 2. Calculator Smart (`calculator_smart.ape`)
Demonstrates the **Controlled Deviation System (CDS)**:
- Deterministic for calculations
- Creative freedom for human summary
- Explicit bounds define what can vary
- Rationale explains why deviation is needed

See [`examples/calculator_basic.ape`](examples/calculator_basic.ape), [`examples/calculator_smart.ape`](examples/calculator_smart.ape) and [`examples/README.md`](examples/README.md) for details.

## Test Results

```
✅ Parser tests:           11 passed
✅ Semantic tests:         19 passed
✅ Codegen tests:          12 passed
✅ Example tests:          14 passed (7 basic + 7 smart)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL:                  56 passed
```

## What Makes Ape Unique

1. **Strict Determinism** - No implicit ambiguity allowed
2. **Controlled Deviation** (RFC-0001) - Explicit flexibility with bounds
3. **AI-Native** - Designed for AI agents to work with
4. **Type Safety** - Strict type checking at all levels
5. **Policy Enforcement** - Policy rules integrated in the language

## Next Steps

Potential extensions:
- [ ] Fully implement deviation system
- [ ] Runtime with logging and tracing
- [ ] Web-based playground
- [ ] VS Code extension
- [ ] More target languages (TypeScript, Rust, etc.)
- [ ] Standard library with common patterns
- [ ] Package manager for Ape modules

## Technical Details

- **Language:** Python 3.11+
- **Dependencies:** None (stdlib only)
- **Test Framework:** pytest
- **Code Style:** Typed Python with dataclasses

---

**Status:** 🟢 Prototype v0.1 - Parser, Validator & Python Codegen working

**Date:** December 3, 2025

**Author:** Author: David Van Aelst (APE Creator)

