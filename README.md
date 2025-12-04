# Ape - AI Programming Language

**The very first AIP (AI Programming Language)** 🚀

Ape is an AI-native programming language with a strict core and Controlled Deviation System.

## Quickstart

### Installation
```bash
git clone https://github.com/yourusername/ape.git
cd ape
pip install -r requirements.txt  # if exists, or install pytest
```

### CLI Usage
```bash
# Parse Ape source to AST
python -m ape parse examples/calculator_basic.ape

# Build IR (Intermediate Representation)
python -m ape ir examples/calculator_basic.ape

# Validate semantics and strictness
python -m ape validate examples/calculator_basic.ape

# Build Python code
python -m ape build examples/calculator_basic.ape --target=python
```

### Your First Ape Program
Create `hello.ape`:
```ape
entity Greeting:
    message: String

task say_hello:
    inputs:
        - name: String
    outputs:
        - greeting: Greeting
    
    constraints:
        - deterministic
    
    steps:
        - create greeting with message
        - return greeting
```

Then compile it:
```bash
python -m ape validate hello.ape
python -m ape build hello.ape --target=python
```

## Core Philosophy

> "What is allowed, is fully allowed.  
> What is forbidden, is strictly forbidden.  
> What is not declared, does not exist."

## What is Implemented

### ✅ 1. Parser & Tokenizer
- **Tokenizer** with indentation-aware lexical analysis
- **AST nodes** for all Ape constructs
- **Recursive descent parser** for Ape grammar v0.3
- **IR Builder** transforms AST to Intermediate Representation

**Tests:** 11 passing

### ✅ 2. Semantic Validator
- **Symbol table** for tracking all declarations
- **Type checking** (entities, enums, builtin types)
- **Duplicate definition detection**
- **Unknown type detection**
- **Contract validation**
- **Policy validation**
- **Deviation validation** (RFC-0001)

### ✅ 3. Strictness Engine
- **Ambiguity detection** (maybe, possibly, ?, etc.)
- **Undeclared behavior detection**
- **Implicit choice detection** (or, choose, etc.)
- **Non-determinism detection** (random, etc.)
- **Deviation bounds validation**
- **Policy conflict detection**

**Tests:** 19 passing

### ✅ 4. Python Code Generator
- **Entity → Python @dataclass** with type hints
- **Enum → Python constants class**
- **Task → Python function** with documentation
- **Flow → Orchestration function** + metadata
- **Policy → Python dict** structures
- **Syntactically valid Python** output

**Tests:** 12 passing

### ✅ 5. Runtime Support
- **RunContext** for flow orchestration
- Placeholder for logging, determinism, etc.

---

## Project Structure

```
Ape/
├── src/
│   ├── apeparser/          # Parser & Tokenizer
│   │   ├── tokenizer.py
│   │   ├── parser.py
│   │   ├── ast_nodes.py
│   │   └── ir_builder.py
│   ├── apecompiler/        # Compiler & Validation
│   │   ├── ir_nodes.py
│   │   ├── errors.py
│   │   ├── semantic_validator.py
│   │   └── strictness_engine.py
│   ├── apecodegen/         # Code Generation
│   │   └── python_codegen.py
│   └── aperuntime/         # Runtime Support
│       └── core.py
├── tests/                  # Test Suite (49 tests)
│   ├── parser/
│   ├── compiler/semantic/
│   ├── codegen/python/
│   └── examples/           # Example program tests
├── examples/               # Example Ape programs
│   ├── calculator_basic.ape
│   └── README.md
├── generated/              # Generated Python code
├── demo_pipeline.py        # Complete pipeline demo
└── example_generate.py     # Code generation example
```

## Ape Syntax Voorbeeld

```ape
entity User:
    id: Integer
    username: String
    email: String

enum UserRole:
    - admin
    - user
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

## Technische Details

- **Taal:** Python 3.11+
- **Dependencies:** Geen (stdlib only)
- **Test Framework:** pytest
- **Code Style:** Typed Python met dataclasses

---

**Status:** 🟢 Prototype v0.1 - Parser, Validator & Python Codegen working

**Date:** December 3, 2025

**Author:** Author: David Van Aelst (APE Creator)

