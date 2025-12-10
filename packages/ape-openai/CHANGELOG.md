# Changelog

All notable changes to `ape-openai` will be documented in this file.

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
- No functional changes to ape-openai code

## [0.1.0] - Initial Release

### Added
- OpenAI integration for APE
- Tool schema generation from APE tasks
- Executor for OpenAI tool calls
- Type conversion utilities
- Comprehensive test suite
