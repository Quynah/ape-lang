# Ape v0.2.0 Module System Examples

This directory contains examples demonstrating Ape's module system, imports, and standard library (introduced in v0.2.0).

## Examples Overview

### 1. `hello_imports.ape` - Basic Imports

**Purpose:** Demonstrates basic usage of standard library modules (`sys` and `math`).

**What it shows:**
- Module declaration: `module main`
- Importing stdlib modules: `import sys`, `import math`
- Calling stdlib functions: `math.add()`, `math.multiply()`, `sys.print()`
- Combining imports in a single program

**Run:**
```bash
python -m ape validate examples/hello_imports.ape
python -m ape build examples/hello_imports.ape --target=python
```

**Key concepts:**
- Standard library is automatically available via linker
- Qualified calls like `math.add` compile to `math__add` in Python
- All stdlib functions are deterministic

---

### 2. `custom_lib_project/` - Local Library

**Purpose:** Demonstrates using a local `lib/` folder for project-specific modules.

**Structure:**
```
custom_lib_project/
├── main.ape           # Entry point
└── lib/
    └── tools.ape      # Local library module
```

**What it shows:**
- Module resolution from `./lib/` directory
- Creating reusable local libraries
- Importing local modules: `import tools`
- Local modules can also import stdlib: `tools` imports `sys` and `math`

**Run:**
```bash
cd examples/custom_lib_project
python -m ape validate main.ape
python -m ape build main.ape --target=python
```

**Key concepts:**
- Linker searches `./lib/` first for modules
- Local libraries can depend on stdlib
- Clean separation between application code and utilities

---

### 3. `stdlib_complete.ape` - All Standard Library Modules

**Purpose:** Comprehensive example using all three stdlib modules: `sys`, `io`, `math`.

**What it shows:**
- Using `sys.print()` for output
- Using `io.read_file()`, `io.write_file()`, `io.read_line()` for I/O
- Using `math.multiply()` for calculations
- Combining all three modules in one program

**Run:**
```bash
python -m ape validate examples/stdlib_complete.ape
python -m ape build examples/stdlib_complete.ape --target=python
```

**Key concepts:**
- Standard library provides common operations
- All stdlib functions are deterministic
- Multiple imports work together seamlessly

---

## Module Resolution Rules

When you write `import <module>`, Ape searches in this exact order:

1. **`./lib/<module>.ape`** - Project-local library (highest priority)
2. **`./<module>.ape`** - Same directory as importing file
3. **`<APE_INSTALL>/ape_std/<module>.ape`** - Standard library (lowest priority)

If the module is not found in any location → **hard compile error**.

---

## Standard Library v0.1 Reference

### `sys` - System Operations
- `sys.print(message: String) → success: Boolean` - Print to stdout
- `sys.exit(code: Integer) → success: Boolean` - Exit program

### `io` - Input/Output
- `io.read_line(prompt: String) → line: String` - Read from stdin
- `io.write_file(path: String, content: String) → success: Boolean` - Write file
- `io.read_file(path: String) → content: String` - Read file

### `math` - Mathematics
- `math.add(a: Integer, b: Integer) → result: Integer` - Addition
- `math.subtract(a: Integer, b: Integer) → result: Integer` - Subtraction
- `math.multiply(a: Integer, b: Integer) → result: Integer` - Multiplication
- `math.divide(a: Integer, b: Integer) → result: Integer` - Division
- `math.power(base: Integer, exponent: Integer) → result: Integer` - Exponentiation
- `math.abs(x: Integer) → result: Integer` - Absolute value

---

## Testing Your Examples

### Validate (Parse + Semantic Check)
```bash
python -m ape validate examples/hello_imports.ape
```

### Build (Generate Python)
```bash
python -m ape build examples/hello_imports.ape --target=python
```

### Parse Only
```bash
python -m ape parse examples/hello_imports.ape
```

### IR (Intermediate Representation)
```bash
python -m ape ir examples/hello_imports.ape
```

---

## Creating Your Own Examples

1. **Declare a module:**
   ```ape
   module my_program
   ```

2. **Import what you need:**
   ```ape
   import sys
   import math
   import my_local_module
   ```

3. **Call imported functions:**
   ```ape
   task example:
       inputs:
           x: Integer
       outputs:
           result: Integer
       constraints:
           - deterministic
       steps:
           - call math.add with x and 1 to get result
           - call sys.print with result
           - return result
   ```

4. **Validate and build:**
   ```bash
   python -m ape validate my_program.ape
   python -m ape build my_program.ape --target=python
   ```

---

## Notes

- All examples are **fully deterministic** - no randomness or ambiguity
- Standard library modules are located in `ape_std/` at the repository root
- The linker automatically resolves all imports before compilation
- Circular dependencies are detected and reported as errors
- Module names must match the declared `module <name>` statement in each file

For more details, see:
- `docs/modules_and_imports.md` - Complete module system specification
- `docs/stdlib_v0.1.md` - Standard library API reference
