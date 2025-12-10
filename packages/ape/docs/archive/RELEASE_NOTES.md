# Release Notes: Ape v0.2.0

## Overview

Ape v0.2.0 is a **major release** introducing a complete, deterministic module system with standard library support. This release enables multi-file Ape programs with clear import semantics, circular dependency detection, and a foundation for building reusable libraries.

**Release Date:** December 4, 2025  
**Version:** 0.2.0  
**Test Status:** ✅ 192/192 tests passing  
**Breaking Changes:** None (fully backward compatible with v0.1.x)

---

## 🎯 What's New

### Module System
- **Module declarations:** `module <name>` to define importable modules
- **Import statements:** `import <module>` to import dependencies
- **Qualified calls:** `module.task(...)` for calling imported tasks
- **Deterministic resolution:** First-match-wins search order (lib/ → . → ape_std/)
- **Name mangling:** `<module>.<symbol>` → `<module>__<symbol>` at code generation

### Linker Component
- Resolves module dependencies across multiple files
- Builds complete dependency graph
- Detects circular dependencies with full cycle reporting
- Topologically sorts modules for correct compilation order
- Clear error messages for all import-related issues

### Standard Library v0.1
Three built-in modules with 13 tasks:

- **sys:** print, exit
- **io:** read_line, write_file, read_file  
- **math:** add, subtract, multiply, divide, power, abs, sqrt, factorial

All standard library tasks are marked as deterministic.

### Documentation
- Complete design philosophy document
- 1334-line module system specification
- Updated README with "What is Ape?" section
- Standard library API reference
- Migration guide from v0.1.x

---

## 📦 Installation

### From PyPI

Once published, install with:

```bash
pip install ape-lang==0.2.0
```

### From Source

```bash
git clone https://github.com/Quynah/Ape.git
cd Ape
git checkout v0.2.0
pip install .
```

---

## 🚀 Quick Start with Modules

**Create a local library** (`lib/utils.ape`):

```ape
module utils

import sys

task greet:
    inputs:
        name: String
    outputs:
        message: String
    
    constraints:
        - deterministic
    
    steps:
        - call sys.print with name
        - return message
```

**Use it in your main file** (`main.ape`):

```ape
module main

import utils

flow demo:
    steps:
        - call utils.greet with "Alice"
    
    constraints:
        - deterministic
```

**Build and run:**

```bash
ape build main.ape --target=python
python generated/main_gen.py
```

---

## 🔧 Release Checklist

### Pre-Release Verification

✅ **Version updated:** pyproject.toml → 0.2.0  
✅ **Tests passing:** 192/192  
✅ **Build successful:** wheel and sdist created  
✅ **Changelog updated:** CHANGELOG.md with complete v0.2.0 section  
✅ **Documentation complete:** README, philosophy.md, modules_and_imports.md

### Manual Release Steps

#### 1. Create Git Tag

```bash
git tag v0.2.0
git push origin v0.2.0
```

#### 2. Create GitHub Release

1. Go to: https://github.com/Quynah/Ape/releases/new
2. Tag: `v0.2.0`
3. Title: `v0.2.0 — Module System & Standard Library`
4. Copy the content from the **GitHub Release Text** section below
5. Attach files (optional):
   - `dist/ape_lang-0.2.0-py3-none-any.whl`
   - `dist/ape_lang-0.2.0.tar.gz`

#### 3. Publish to PyPI

**IMPORTANT:** Only run this when you're ready to publish publicly!

```bash
# Verify build artifacts exist
ls dist/ape_lang-0.2.0*

# Upload to PyPI (requires PyPI account and credentials)
twine upload dist/ape_lang-0.2.0*
```

**Note:** You can test on TestPyPI first:

```bash
twine upload --repository testpypi dist/ape_lang-0.2.0*
```

---

## 📝 GitHub Release Text

Copy this text into the GitHub release body:

```markdown
# Ape v0.2.0 — Module System & Standard Library

A major release introducing a complete, deterministic module system with standard library support. Build multi-file Ape programs with clear import semantics and reusable libraries.

## 🎯 Key Features

### Module System
- ✅ `module` declarations and `import` statements
- ✅ Qualified identifier calls: `module.task(...)`
- ✅ Deterministic module resolution (lib/ → . → ape_std/)
- ✅ Circular dependency detection with clear error messages
- ✅ Name-mangled code generation for namespace isolation

### Standard Library v0.1
- ✅ **sys** module: print, exit
- ✅ **io** module: read_line, write_file, read_file
- ✅ **math** module: add, subtract, multiply, divide, power, abs, sqrt, factorial
- ✅ All tasks marked as deterministic

### Linker
- ✅ Multi-file dependency resolution
- ✅ Dependency graph building and topological sorting
- ✅ Circular dependency detection
- ✅ Clear, actionable error messages

## 📊 Testing
- **192 tests passing** (up from ~80 in v0.1.x)
- 25 parser tests for modules/imports
- 22 linker tests
- 15 codegen tests for name mangling
- 35 standard library tests
- 15 example integration tests

## 🔄 Backward Compatibility
✅ All v0.1.x programs work unchanged  
✅ No breaking changes to existing syntax  
✅ Opt-in module system (add `module` declaration to make files importable)

## 📚 Documentation
- New design philosophy document explaining Ape's dual role
- Complete 1334-line module system specification
- Updated README with "What is Ape?" section
- Standard library API reference
- Migration guide from v0.1.x

## 📦 Installation

```bash
pip install ape-lang==0.2.0
```

## 🚀 Quick Example

**lib/math_utils.ape:**
```ape
module math_utils

import math

task square:
    inputs:
        x: Integer
    outputs:
        result: Integer
    constraints:
        - deterministic
    steps:
        - call math.multiply with x and x to get result
        - return result
```

**main.ape:**
```ape
module main

import math_utils
import sys

flow demo:
    steps:
        - call math_utils.square with 5 to get result
        - call sys.print with result
    constraints:
        - deterministic
```

**Build:**
```bash
ape build main.ape --target=python
python generated/main_gen.py
```

## 📖 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🙏 Acknowledgments

Thanks to everyone testing and providing feedback on the module system design!

---

**What's Next?** v0.3.0 will bring specific symbol imports (`import math.add`), export control, and expanded standard library modules.
```

---

## 🔍 Post-Release Verification

After publishing:

1. **Verify PyPI listing:** https://pypi.org/project/ape-lang/
2. **Test installation:** `pip install ape-lang==0.2.0` in fresh virtualenv
3. **Verify CLI:** `ape --version` should show `0.2.0`
4. **Run example:** Test one of the module examples from docs

---

## 📋 Additional Notes

### Build Warnings

The build process shows deprecation warnings about license configuration. These are non-critical but can be addressed in a future release by updating `pyproject.toml` to use the newer SPDX license format:

```toml
# Current (deprecated):
license = { text = "MIT" }

# Future (recommended):
license = "MIT"
```

### Files in dist/

- `ape_lang-0.2.0-py3-none-any.whl` - Wheel package (preferred)
- `ape_lang-0.2.0.tar.gz` - Source distribution

Both are ready for PyPI upload.

---

## 🎉 Release Complete!

Once the above steps are completed:
- ✅ Git tag created and pushed
- ✅ GitHub release published with release notes
- ✅ Package uploaded to PyPI
- ✅ Documentation is up to date

Ape v0.2.0 is ready for the world! 🦍
