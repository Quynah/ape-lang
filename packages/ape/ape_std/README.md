# Ape Standard Library (ape_std)

**Status**: Placeholder for v0.2.0  
**Version**: 0.2.0-dev

---

## Overview

This directory contains the **Ape Standard Library**, a collection of built-in modules that provide common functionality for Ape programs.

The standard library is part of the core Ape distribution and follows the same deterministic principles as user code.

---

## Standard Library Modules (Planned)

The following modules are planned for implementation in future releases:

### Core Modules

- **`math`**: Basic arithmetic, trigonometry, mathematical constants
  - Functions: `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt`, `sin`, `cos`, `tan`, etc.
  - Constants: `PI`, `E`

- **`strings`**: String manipulation and formatting
  - Functions: `upper`, `lower`, `trim`, `split`, `join`, `substring`, `format`, etc.

- **`io`**: File and console I/O operations
  - Functions: `read_file`, `write_file`, `read_line`, `print`, `println`, etc.

- **`collections`**: Data structure utilities
  - Types: `List`, `Set`, `Map`
  - Functions: `map`, `filter`, `reduce`, `sort`, etc.

- **`datetime`**: Date and time utilities
  - Types: `DateTime`, `Date`, `Time`, `Duration`
  - Functions: `now`, `parse`, `format`, `add_days`, etc.

- **`json`**: JSON parsing and serialization
  - Functions: `parse`, `stringify`, `validate`

### Future Modules

- **`http`**: HTTP client operations (v0.3.0+)
- **`crypto`**: Cryptographic functions (v0.3.0+)
- **`regex`**: Regular expression support (v0.3.0+)
- **`testing`**: Unit testing framework (v0.3.0+)

---

## Module Resolution

The standard library is searched as the **last location** in the module resolution order:

1. `./lib/<module>.ape` (project-local library)
2. `./<module>.ape` (same directory)
3. **`<APE_INSTALL>/ape_std/<module>.ape`** (standard library)

See `docs/modules_and_imports.md` for complete details on module resolution.

---

## Usage

To use a standard library module in your Ape program:

```ape
import math

task calculate_area:
    inputs:
        - radius: decimal
    outputs:
        - area: decimal
    
    steps:
        - area = math.multiply(math.PI, math.power(radius, 2))
        - return area
```

---

## Implementation Status

**v0.2.0**: Folder structure and specification only (this file)

**v0.3.0+**: Actual module implementations will be added in subsequent releases

---

## Design Principles

All standard library modules must:

1. **Be deterministic**: Same inputs always produce same outputs
2. **Have clear contracts**: Explicit inputs, outputs, and constraints
3. **Follow Ape philosophy**: What is allowed is fully allowed; what is forbidden is strictly forbidden
4. **Be well-documented**: Every function and type must have clear documentation
5. **Have test coverage**: Comprehensive tests for all functionality
6. **Be AI-friendly**: Predictable behavior for AI code generation

---

## Contributing

Standard library modules are maintained by the Ape core team. Proposals for new modules or functions should be submitted as RFCs to the main repository.

---

**End of README**
