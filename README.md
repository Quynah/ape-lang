# APE Language — Monorepo

**A deterministic decision language for auditable, traceable, and explainable systems.**

[![PyPI version](https://badge.fury.io/py/ape-lang.svg)](https://pypi.org/project/ape-lang/)
[![Tests](https://img.shields.io/badge/tests-439%20passing-brightgreen)](packages/ape/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⚠️ Intended Audience (v1.x)

**APE v1.x is designed for:**

- Engineers and researchers building **deterministic decision systems**
- Environments with **governance, audit, or safety requirements**
- Use cases requiring **explainability and traceability** of decisions
- **Controlled AI integrations** where AI provides input but does not directly execute decisions
- Systems where **human oversight** is required or mandated

**APE is focused on:**
- Structured decision logic that can be inspected and explained
- Workflows where determinism, reproducibility, and auditability matter
- Integration scenarios where AI assists but humans remain accountable

---

## 🚫 Explicit Exclusions (Non-Goals)

**APE v1.x is NOT:**

- ❌ A general-purpose programming language (use Python, JavaScript, Rust, etc.)
- ❌ An AI agent framework (not designed for autonomous agents)
- ❌ An autonomous decision maker (requires human control and oversight)
- ❌ Suitable for unsupervised or self-executing systems
- ❌ Intended for direct consumer-facing applications without oversight
- ❌ A replacement for production languages in general software development

**If you need:**
- General computation → use Python, Go, Rust
- Autonomous AI agents → use LangChain, AutoGPT, or agent frameworks
- Web applications → use React, Django, Rails
- System programming → use C, Rust, Zig

APE serves a **narrow, specific niche**: deterministic decision logic with full observability.

---

## 🛡️ Governance & Safety Design

**APE is built with governance and responsibility as core principles:**

- **Dry-run by default** - No mutations without explicit opt-in (`allow_execution=True`)
- **Mandatory traceability** - Every execution has a unique `trace_id`
- **Explainability first** - Decision paths can be explained and replayed
- **Human accountability** - Designed for human-in-the-loop workflows, not autonomous systems

**APE is not suitable for:**
- Applications where autonomous decisions directly impact vulnerable populations (including minors) without human review
- Systems requiring real-time autonomous responses without oversight
- Scenarios where traceability and auditability are not feasible or required

**These are design constraints, not certifications or guarantees.** Users remain responsible for appropriate use, compliance with regulations, and ethical deployment.

---

## 🎯 Why APE Exists (Practical)

**Existing AI tools let AI decide. APE splits this explicitly:**

- **AI = input** (suggestions, analysis, generated candidates)
- **APE = decision** (deterministic logic, traceable execution)

**APE exists to:**

1. **Enforce deterministic decisions** - No "best effort" or ambiguous outcomes
2. **Make explainability standard** - Every decision path can be explained and replayed
3. **Enable audit & governance** - Full traceability with mandatory `trace_id`
4. **Eliminate ambiguity** - What is allowed is explicit, what is forbidden is enforced

**Use case:** AI generates multiple policy candidates → APE validates and enforces exactly one → Decision is traceable and auditable.

**Not a vision statement. This is what the system does.**

---

## 📦 Packages

### Core Language
**[packages/ape/](packages/ape/)** - APE compiler, runtime, and standard library

```bash
pip install ape-lang
```

- ✅ **439 tests passing** (full compiler pipeline)
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
- 49 tests passing

**[packages/ape-openai/](packages/ape-openai/)** - OpenAI GPT integration
```bash
pip install ape-openai
```
- Executor and schema for OpenAI API

**[packages/ape-langchain/](packages/ape-langchain/)** - LangChain integration
```bash
pip install ape-langchain
```
- APE-to-LangChain bridge utilities

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

## 🎯 Core Philosophy

> **"What is allowed, is fully allowed.**  
> **What is forbidden, is strictly forbidden.**  
> **What is not declared, does not exist."**

APE is a **decision language**, not a general-purpose programming language:

- ✅ **Explicit over implicit** - No magic behavior, no hidden side effects
- ✅ **Fail loud, fail fast** - Clear errors, no silent failures
- ✅ **Deterministic by default** - Same input → same output, always
- ✅ **Traceable by design** - Every execution produces inspectable traces
- ✅ **Human-supervised** - Built for controlled execution, not autonomous operation

**APE is a bridge language:**
- Translates human intent into deterministic logic
- Enables AI to assist with structured decision workflows
- Maintains full auditability and explainability
- Keeps humans accountable for outcomes

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

All packages have comprehensive test suites:

```bash
# Run core language tests (439 tests)
cd packages/ape
pytest

# Run integration tests
cd packages/ape-anthropic
pytest
```

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

## 🦍 Status: v1.0.2

**Current Release:** v1.0.2 (December 7, 2025)  
**Tag:** ape-v1.0.2-analyzer-ready  
**Maturity:** Production-ready core, scaffolded advanced features  
**Tests:** 439/439 passing ✅

See [CHANGELOG](packages/ape/CHANGELOG.md) for version history

---

## 👤 Author

**David Van Aelst**

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
