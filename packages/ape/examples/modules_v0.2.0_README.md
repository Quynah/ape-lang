# Ape v0.2.0 Module and Import Examples

This directory contains examples demonstrating the new module and import system introduced in Ape v0.2.0.

## Example 1: Simple Module (math.ape)

A basic math library module:

```ape
module math

entity Number:
    value: int

task add:
    inputs:
        a: int
        b: int
    outputs:
        result: int
    steps:
        - compute sum
        - return result

task multiply:
    inputs:
        a: int
        b: int
    outputs:
        result: int
    steps:
        - compute product
        - return result
```

## Example 2: Using Imports (calculator.ape)

A calculator that imports from the math module:

```ape
module calculator

import math

entity Calculation:
    left: int
    right: int
    result: int

task calculate_sum:
    inputs:
        a: int
        b: int
    outputs:
        calc: Calculation
    steps:
        - call math.add with a and b
        - create Calculation with result
        - return calc
```

## Example 3: Specific Symbol Import (formatter.ape)

Importing specific symbols from modules:

```ape
module formatter

import math.add
import strings.upper

task format_sum:
    inputs:
        a: int
        b: int
        label: String
    outputs:
        message: String
    steps:
        - compute result using add
        - format label using upper
        - combine into message
        - return message
```

## Example 4: Legacy Code (no module declaration)

Existing Ape code without module declarations continues to work:

```ape
entity User:
    id: int
    name: String

task create_user:
    inputs:
        name: String
    outputs:
        user: User
    steps:
        - create user object
        - return user
```

## Testing Examples

You can parse these examples using the Ape CLI:

```bash
# Parse a module
python -m ape parse examples/math.ape

# Validate a module with imports
python -m ape validate examples/calculator.ape

# Build to Python
python -m ape build examples/calculator.ape --target=python
```

## Module Resolution

When you write `import math`, Ape searches in this order:

1. `./lib/math.ape` - Project-local library
2. `./math.ape` - Same directory
3. `<APE_INSTALL>/ape_std/math.ape` - Standard library

See the full specification in `docs/modules_and_imports.md`.
