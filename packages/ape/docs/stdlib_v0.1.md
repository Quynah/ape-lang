# Ape Standard Library v0.1

## Overview

The Ape standard library provides a minimal set of common functionality for Ape programs. These modules are automatically available via the linker's search path at `<APE_INSTALL>/ape_std/`.

## Modules

### sys - System Operations

Location: `ape_std/sys.ape`

System-level operations for I/O and program control.

**Functions:**
- `sys.print(message: String) → success: Boolean`
  - Print a message to standard output
  - Returns: Boolean indicating success
  
- `sys.exit(code: Integer) → success: Boolean`
  - Exit the program with the given exit code
  - Returns: Boolean indicating success

**Example:**
```ape
import sys

task greet:
    inputs:
        name: String
    outputs:
        success: Boolean
    constraints:
        - deterministic
    steps:
        - call sys.print with name
        - return success
```

### io - Input/Output Operations

Location: `ape_std/io.ape`

File and console I/O operations.

**Functions:**
- `io.read_line(prompt: String) → line: String`
  - Read a line from standard input with a prompt
  - Returns: The line read as a String
  
- `io.write_file(path: String, content: String) → success: Boolean`
  - Write content to a file
  - Returns: Boolean indicating success
  
- `io.read_file(path: String) → content: String`
  - Read entire file contents as a string
  - Returns: The file content as a String

**Example:**
```ape
import io

task save_config:
    inputs:
        path: String
        config: String
    outputs:
        success: Boolean
    constraints:
        - deterministic
    steps:
        - call io.write_file with path and config
        - return success
```

### math - Mathematical Operations

Location: `ape_std/math.ape`

Basic arithmetic operations on integers.

**Functions:**
- `math.add(a: Integer, b: Integer) → result: Integer`
  - Add two integers
  
- `math.subtract(a: Integer, b: Integer) → result: Integer`
  - Subtract b from a
  
- `math.multiply(a: Integer, b: Integer) → result: Integer`
  - Multiply two integers
  
- `math.divide(a: Integer, b: Integer) → result: Integer`
  - Divide a by b (integer division)
  
- `math.power(base: Integer, exponent: Integer) → result: Integer`
  - Raise base to the power of exponent
  
- `math.abs(x: Integer) → result: Integer`
  - Return absolute value of x

**Example:**
```ape
import math

task calculate:
    inputs:
        x: Integer
        y: Integer
    outputs:
        sum: Integer
        product: Integer
    constraints:
        - deterministic
    steps:
        - call math.add with x and y to get sum
        - call math.multiply with x and y to get product
        - return sum and product
```

## Implementation Notes

All standard library functions are:
1. Marked as `deterministic` - they produce consistent outputs for the same inputs
2. Defined as task stubs that compile to Python function definitions with `raise NotImplementedError`
3. Intended to be implemented by the runtime or replaced with actual implementations

The stdlib modules are resolvable via the linker from the `ape_std/` directory, which is searched as the third fallback after `./lib/` and `.` directories.

## Usage

To use standard library modules in your Ape program:

1. Add import statements at the top of your module (after `module` declaration)
2. Call stdlib functions using qualified names (e.g., `math.add`, `sys.print`)
3. The linker will automatically resolve these imports

**Complete Example:**
```ape
module my_program

import sys
import math

task main:
    inputs:
        x: Integer
        y: Integer
    outputs:
        result: Integer
    constraints:
        - deterministic
    steps:
        - call math.add with x and y to get result
        - call sys.print with result
        - return result
```

## Testing

Comprehensive tests are provided in `tests/std/`:
- `test_math.py` - Tests for math module
- `test_sys.py` - Tests for sys module
- `test_io.py` - Tests for io module

Tests verify:
- Module parsing
- Linking and resolution
- Code generation with proper name mangling
- Function signatures
- Deterministic constraints
- Multi-module imports

All 35 stdlib tests pass, and the full test suite maintains 177/177 passing tests.
