# Version Update Plan: v1.0.2 → v1.0.3

## Changes in v1.0.3

**Date:** December 10, 2025

### Bug Fixes
- **Critical:** Fixed while loop variable persistence bug (execute_while now uses same context instead of child_scope)

### Tests
- Added 16 comprehensive control flow stability tests
- Total core tests: 595 → 611 (539 passing, 72 skipped)
- New test classes:
  - TestReturnInsideControlFlow (3 tests)
  - TestNestedControlFlow (4 tests) 
  - TestBooleanExpressions (3 tests)
  - TestNegativeControlFlow (3 tests)
  - TestExecutionStability (3 tests)

### Documentation
- Created `docs/APE_TESTING_GUARANTEES.md` - comprehensive test guarantees documentation
- Updated all README test counts
- Added test execution instructions to guarantees doc

### Tooling
- Fixed `scripts/count_tests.py` type annotation (cwd: Optional[str])

---

## Files to Update

### pyproject.toml (version field)
- [x] packages/ape/pyproject.toml: 1.0.2 → 1.0.3
- [ ] packages/ape-anthropic/pyproject.toml: 1.0.1 → 1.0.3
- [ ] packages/ape-openai/pyproject.toml: 1.0.1 → 1.0.3
- [ ] packages/ape-langchain/pyproject.toml: 1.0.1 → 1.0.3

### __init__.py (__version__ field)
- [ ] packages/ape/src/ape/__init__.py: 1.0.1 → 1.0.3
- [ ] packages/ape-anthropic/src/ape_anthropic/__init__.py: 0.1.1 → 1.0.3
- [ ] packages/ape-openai/src/ape_openai/__init__.py: 0.1.0 → 1.0.3
- [ ] packages/ape-langchain/src/ape_langchain/__init__.py: 0.1.0 → 1.0.3

### pyproject.toml (dependency versions)
- [ ] packages/ape-anthropic/pyproject.toml: ape-lang>=1.0.1 → ape-lang>=1.0.3
- [ ] packages/ape-openai/pyproject.toml: ape-lang>=1.0.1 → ape-lang>=1.0.3
- [ ] packages/ape-langchain/pyproject.toml: ape-lang>=1.0.1 → ape-lang>=1.0.3

### CHANGELOG.md (new v1.0.3 entry at top)
- [ ] packages/ape/CHANGELOG.md
- [ ] packages/ape-anthropic/CHANGELOG.md
- [ ] packages/ape-openai/CHANGELOG.md
- [ ] packages/ape-langchain/CHANGELOG.md

### README.md (status sections)
- [ ] README.md (root): v1.0.0 → v1.0.3
- [ ] packages/ape/README.md: v1.0.0 → v1.0.3

### Documentation
- [x] packages/ape/docs/APE_TESTING_GUARANTEES.md: v1.0.3 already set

### Outdated Files to Delete or Update
- [ ] packages/ape/CONTROL_FLOW_IMPLEMENTATION.md: references v0.3.0 (OUTDATED - delete or archive)
- [ ] packages/ape/RELEASE_NOTES.md: references v0.2.0 (OUTDATED - delete or archive)
- [ ] packages/ape/RELEASE_CHECKLIST.md: references v0.2.0 (OUTDATED - delete or archive)
- [ ] packages/ape/RELEASE_SUMMARY.md: references v0.2.0 (OUTDATED - delete or archive)
- [ ] packages/ape/PYPI_RELEASE_SUMMARY.md: references v0.2.0 (OUTDATED - delete or archive)
- [ ] packages/ape/RELEASE_BODY_v1.0.0.md: still relevant but refers to v1.0.0
- [ ] packages/ape/pyproject.toml.bak: DELETE (backup file)
- [ ] packages/ape-anthropic/pyproject.toml.bak: DELETE (backup file)

### Tutorial READMEs (APE version field)
- [ ] All tutorial READMEs: v1.0.0 → v1.0.3

### Legacy Documentation (v0.x references)
- Multiple files reference old v0.2.0, v0.3.0, v0.4.0 roadmap versions
- Decision: Keep as historical context OR update to reflect v1.0.3 reality

---

## Execution Order

1. Add v1.0.3 CHANGELOG entries (all 4 packages)
2. Update pyproject.toml versions (all 4 packages)
3. Update __init__.py __version__ (all 4 packages)
4. Update dependency versions in adapter pyproject.toml files
5. Update README.md status sections
6. Delete .bak files
7. Archive or delete outdated release documentation
8. Update tutorial READMEs
9. Build and publish packages

