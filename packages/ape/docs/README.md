# Ape v0.2.0 Documentation

Welcome to the Ape programming language documentation. This directory contains comprehensive guides for understanding and using Ape.

## Documentation Index

### Core Concepts

1. **[Philosophy and Design](philosophy.md)**
   - What is Ape? (Bridge Language vs Standalone Language)
   - Core design principles
   - Why Ape is optimized for AI collaboration
   - The role of determinism in Ape
   - Future vision and roadmap

2. **[Modules and Imports](modules_and_imports.md)** ⭐ **v0.2.0**
   - Complete module system specification
   - Import syntax and resolution order
   - Name mangling and namespacing
   - Standard library v0.1 (sys, io, math)
   - Error handling and troubleshooting
   - Implementation status: 192/192 tests passing

### Implementation Details

3. **[Code Generation and Namespacing](codegen_namespacing.md)**
   - How name mangling works (`module.symbol` → `module__symbol`)
   - Backward compatibility with v0.1.x
   - Target language code generation

4. **[Linker Implementation](linker_implementation.md)**
   - Module resolution algorithm
   - Dependency graph building
   - Circular dependency detection
   - Search order: `./lib/` → `./` → `<APE_INSTALL>/ape_std/`

5. **[Standard Library v0.1](stdlib_v0.1.md)**
   - `sys`: print, exit
   - `io`: read_line, write_file, read_file
   - `math`: add, subtract, multiply, divide, power, abs, sqrt, factorial
   - All tasks marked as deterministic

## Quick Start

### New to Ape?

1. Read **[Philosophy and Design](philosophy.md)** to understand Ape's unique value proposition
2. Check the main **[README](../README.md)** for installation and basic usage
3. Explore **[Modules and Imports](modules_and_imports.md)** to learn the v0.2.0 module system

### Working with Modules?

1. **[Modules and Imports](modules_and_imports.md)** - Complete reference
2. **[Standard Library v0.1](stdlib_v0.1.md)** - API documentation for sys, io, math
3. **[Examples](../examples/)** - Working code samples

### Implementing Ape?

1. **[Linker Implementation](linker_implementation.md)** - Module resolution algorithm
2. **[Code Generation](codegen_namespacing.md)** - Name mangling and codegen
3. **[Modules and Imports](modules_and_imports.md)** - Complete specification with error messages

## What's New in v0.2.0

Ape v0.2.0 introduces a complete, deterministic module system:

### ✅ Module System
- **Module declarations**: `module <name>`
- **Import statements**: `import <module>`
- **Qualified calls**: `module.task(...)`
- **Deterministic resolution**: `./lib/` → `./` → `<APE_INSTALL>/ape_std/`
- **Name mangling**: `<module>.<symbol>` → `<module>__<symbol>`

### ✅ Standard Library v0.1
Three fully implemented modules:

**sys** - System operations
```ape
task print:
    inputs: message: String
    outputs: success: Boolean

task exit:
    inputs: code: Integer
    outputs: success: Boolean
```

**io** - File and input operations
```ape
task read_line:
    inputs: prompt: String
    outputs: line: String

task write_file:
    inputs: path: String, content: String
    outputs: success: Boolean

task read_file:
    inputs: path: String
    outputs: content: String
```

**math** - Mathematical operations
```ape
task add:
    inputs: a: Integer, b: Integer
    outputs: result: Integer

task subtract:
    inputs: a: Integer, b: Integer
    outputs: result: Integer

task multiply:
    inputs: a: Integer, b: Integer
    outputs: result: Integer

task divide:
    inputs: a: Integer, b: Integer
    outputs: result: Float

task power:
    inputs: base: Integer, exponent: Integer
    outputs: result: Integer

task abs:
    inputs: x: Integer
    outputs: result: Integer

task sqrt:
    inputs: x: Float
    outputs: result: Float

task factorial:
    inputs: n: Integer
    outputs: result: Integer
```

### ✅ Testing
- **192/192 tests passing**
- Parser tests (module/import syntax)
- Linker tests (resolution, cycles)
- Codegen tests (name mangling)
- Standard library tests
- End-to-end integration tests

## Design Philosophy Summary

Ape is **both** a translator language and a standalone language:

### As a Translator (Bridge Language)
- Converts human/AI intent → target language code (Python, TypeScript, etc.)
- Deterministic by default (no guessing)
- Explicit over implicit
- Optimized for AI code generation

### As a Standalone Language
- Complete module and library system
- Standard library (sys, io, math)
- Entity/task/flow/policy primitives
- Controlled deviation system for non-deterministic code

This dual nature makes Ape ideal for:
- AI-assisted development
- Prototyping with guaranteed translation
- Building structured, maintainable systems
- Clear communication of intent

## Examples

Check the **[examples/](../examples/)** directory for working code:

1. **hello_imports.ape** - Basic module imports
2. **stdlib_complete.ape** - Using all three stdlib modules
3. **custom_lib_project/** - Project with local library

## Contributing

When adding documentation:
- Update this index with new files
- Follow existing structure (philosophy → specification → implementation)
- Include concrete code examples (use actual Ape syntax)
- Add error scenarios with real error messages
- Update "What's New" section in main README

## Version History

- **v0.2.0** (Current) - Module system, stdlib v0.1, 192 tests
- **v0.1.x** - Core language (entity, task, flow, policy, deviation)
- **v0.3.0** (Planned) - Specific symbol imports, export control

---

**Need help?** Start with [Philosophy and Design](philosophy.md) to understand Ape's unique approach, then dive into [Modules and Imports](modules_and_imports.md) for the complete technical reference.
