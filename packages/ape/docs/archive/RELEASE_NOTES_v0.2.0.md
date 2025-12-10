# Ape v0.2.0 Release Notes

**Release Date:** December 4, 2025  
**Package:** ape-lang  
**Version:** 0.2.0

---

## Overview

Ape v0.2.0 introduces modules, imports, deterministic linking, and the first standard library. It is the foundation for the upcoming v1.0.0 release.

This release transforms Ape from a single-file language into a complete module system with predictable, deterministic behavior that both humans and AI can rely on.

---

## What's New

### 🎯 Module System

**Module Declarations**
```ape
module main

import sys
import math
```

Every importable file now declares its module name. This enables clear dependency management and namespace isolation.

**Deterministic Resolution**

When you `import math`, Ape searches in this exact order:
1. `./lib/math.ape` - Project-local library (highest priority)
2. `./math.ape` - Same directory as importing file
3. `<APE_INSTALL>/ape_std/math.ape` - Standard library (lowest priority)

**First match wins.** No ambiguity, no guessing. If not found → clear compile error.

### 📦 Linker

The linker resolves all module dependencies:
- Builds complete dependency graph
- Detects circular dependencies
- Reports full cycle path (e.g., `a → b → c → a`)
- Topologically sorts modules for correct compilation order

### 🔧 Code Generation

**Name Mangling**

Module-qualified calls are mangled at code generation time:
- `math.add` → `math__add` in Python
- Prevents naming collisions
- Preserves module namespaces

**Backward Compatible**

Files without `module` declarations work as before (no mangling).

### 📚 Standard Library v0.1

Three core modules included:

**`sys` - System Operations**
- `print(message: String) → success: Boolean`
- `exit(code: Integer) → success: Boolean`

**`io` - Input/Output**
- `read_line(prompt: String) → line: String`
- `write_file(path: String, content: String) → success: Boolean`
- `read_file(path: String) → content: String`

**`math` - Mathematics**
- `add`, `subtract`, `multiply`, `divide`
- `power`, `abs`, `sqrt`, `factorial`

All tasks are marked as `deterministic`.

### 📖 Documentation

- Complete design philosophy document
- 1334-line module system specification
- Standard library API reference
- Migration guide from v0.1.x
- Updated README with roadmap to v1.0.0

### ✅ Testing

**192 tests passing** (up from ~80 in v0.1.x):
- 25 parser tests for modules/imports
- 22 linker tests (resolution + cycles)
- 15 codegen tests (name mangling)
- 35 standard library tests
- 15 example integration tests

---

## Installation

### From PyPI

```bash
pip install ape-lang
```

### Verify Installation

```bash
ape --version
# Output: 0.2.0
```

---

## Quick Start

### Example: Hello World with Standard Library

**File: `hello.ape`**
```ape
module main

import sys

task main:
    inputs:
        none
    outputs:
        success: Boolean
    constraints:
        - deterministic
    steps:
        - call sys.print with "Hello from Ape v0.2.0!"
        - return success
```

**Compile:**
```bash
ape validate hello.ape
ape build hello.ape --target=python
```

### Example: Using Math Library

**File: `calculator.ape`**
```ape
module calculator

import math
import sys

task calculate:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: Integer
    constraints:
        - deterministic
    steps:
        - call math.add with a and b to get sum
        - call math.multiply with sum and 2 to get result
        - call sys.print with result
        - return result
```

### Example: Custom Libraries

**Project structure:**
```
my_project/
├── main.ape
└── lib/
    └── utils.ape
```

**File: `lib/utils.ape`**
```ape
module utils

import sys

task log:
    inputs:
        message: String
    outputs:
        success: Boolean
    constraints:
        - deterministic
    steps:
        - call sys.print with message
        - return success
```

**File: `main.ape`**
```ape
module main

import utils

task main:
    inputs:
        none
    outputs:
        success: Boolean
    constraints:
        - deterministic
    steps:
        - call utils.log with "Hello from local library!"
        - return success
```

The linker automatically finds `utils` in `./lib/utils.ape`.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete v0.2.0 changelog including:
- Module system features
- Linker implementation
- Standard library v0.1
- Code generation updates
- Documentation improvements
- Testing statistics

---

## Migration from v0.1.x

All v0.1.x programs work unchanged in v0.2.0:
- Files without `module` declarations are valid
- No breaking changes to existing syntax
- Opt-in module system: add `module` declaration to enable imports

---

## What's Next

### v0.3.0 (Planned Q1 2026)
- Control flow (if, while, for)
- Basic type system (int, float, string, bool, list, map)
- Expanded error messages

### v1.0.0 (Targeted Q2 2026)
- Complete minimal language specification
- Stable compiler backend
- Standard library v1.0 (string, json, http, etc.)
- CLI improvements (fmt, test, etc.)

See [README.md](README.md) for the complete roadmap.

---

## Package Contents

The PyPI package includes:
- ✅ Core compiler (parser, linker, codegen)
- ✅ Standard library v0.1 (sys, io, math)
- ✅ CLI tool (`ape` command)
- ✅ Complete documentation
- ✅ Working examples

---

## Known Issues

**Build Warnings**

The build process shows deprecation warnings about license configuration. These are non-critical and can be ignored. They will be addressed in a future release.

**Not Yet Implemented**
- Control flow statements (if, while, for)
- Advanced type system
- Package manager
- Ape bytecode VM

These are planned for future releases.

---

## Links

- **GitHub:** https://github.com/Quynah/Ape
- **PyPI:** https://pypi.org/project/ape-lang/
- **Documentation:** https://github.com/Quynah/Ape/tree/main/docs
- **Issues:** https://github.com/Quynah/Ape/issues

---

## Contributing

Ape is under active development. Contributions welcome!

Areas needing help:
- Control flow implementation
- Type system expansion
- Standard library additions
- VS Code extension
- Documentation improvements

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Credits

**Author:** David Van Aelst  
**Contributors:** Community contributors welcome!

---

**APE v0.2.0** — Built for deterministic AI collaboration 🦍

*Ape is a programming language designed for AI and humans to communicate unambiguously.*
