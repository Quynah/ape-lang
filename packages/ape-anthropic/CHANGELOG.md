# Changelog

All notable changes to `ape-anthropic` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-12-10

### Changed
- Updated dependency to `ape-lang>=1.0.4` for runtime task execution support
- Fully compatible with APE v1.0.4 runtime execution features:
  - Task execution via RuntimeExecutor
  - Tuple returns from tasks
  - If-elif-else chain detection
  - Early return support
  - Nested control flow

### Fixed
- Benefits from upstream task execution and control flow fixes

---

## [1.0.3] - 2025-12-10

### Changed
- Updated dependency to `ape-lang>=1.0.3` for control flow bug fixes
- Fully compatible with APE v1.0.3 control flow stability improvements

### Fixed
- Benefits from upstream while loop variable persistence fix

---

## [1.0.0] - 2025-12-06

### Changed
- **BREAKING:** Updated dependency to `ape-lang>=1.0.0` for compatibility with APE v1.0.0 release
- Aligned version with APE core release (semantic versioning sync)

### Compatibility
- Fully compatible with APE v1.0.0 multi-language features
- Tested with APE v1.0.0 runtime and executor
- No functional changes to ape-anthropic code

## [0.1.1] - Previous Release

### Changed
- Completed executor and generator test suites for full coverage
- Added end-to-end integration tests validating schema execution flow
- Improved test coverage for Claude dict-based tool use semantics
- Enhanced error handling tests for missing parameters and unknown functions

### Tests
- Added 12 executor tests with dict payload validation
- Added 11 generator tests with Anthropic API mocking
- Added 5 end-to-end integration tests
- All 51 tests now passing (100% coverage for core functionality)

## [0.1.0] - 2024-01-15

### Added
- Initial release of ape-anthropic
- Schema conversion: APE tasks  Claude tool schemas
- Execution layer with APE validation
- ApeAnthropicFunction wrapper class
- Natural language  APE code generation via Claude
- Type mapping for all APE types
- Error handling for Claude tool use
- Comprehensive test suite (44 tests)
- Full documentation and examples

### Features
- `ape_task_to_claude_schema()` - Convert APE to Claude format
- `execute_claude_call()` - Execute with validation
- `ApeAnthropicFunction` - High-level integration class
- `generate_ape_from_nl()` - Experimental code generation
- Support for Claude 3 Opus, Sonnet, and Haiku models

### Type Support
- String  string
- Integer  integer
- Float  number
- Boolean  boolean
- List  array
- Dict  object

[0.1.0]: https://github.com/yourusername/ape-anthropic/releases/tag/v0.1.0
