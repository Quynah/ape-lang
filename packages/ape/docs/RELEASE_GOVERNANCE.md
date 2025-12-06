# APE Release Governance & SemVer Policy

**Version:** 1.0.0  
**Status:** Active  
**Scope:** Defines release process and semantic versioning for APE v1.0+

This document establishes the governance process for APE releases, semantic versioning interpretation, and compatibility guarantees.

---

## 1. Semantic Versioning (SemVer)

APE follows **Semantic Versioning 2.0.0** (semver.org) with APE-specific interpretations.

### 1.1 Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

**Examples:**
- `1.0.0` - Initial stable release
- `1.1.0` - New features, backward compatible
- `1.0.1` - Bug fix, backward compatible
- `2.0.0-alpha.1` - Pre-release for major version
- `1.5.3+20250106` - Build metadata

### 1.2 Version Increment Rules

**MAJOR (X.0.0)** - Incompatible API changes
- Breaking syntax changes
- Breaking semantic changes
- Public API removals or signature changes
- Type system overhaul

**MINOR (1.X.0)** - New features, backward compatible
- New syntax (with new keywords)
- New stdlib modules
- New capabilities
- New APIs (additive only)
- Performance improvements

**PATCH (1.0.X)** - Bug fixes, backward compatible
- Bug fixes in runtime
- Documentation corrections
- Error message improvements
- Security patches (non-breaking)

---

## 2. What Constitutes a Breaking Change

### 2.1 BREAKING (Requires Major Version)

**❌ Syntax Changes**
```ape
# Removing or changing keywords
# v1.x: task → v2.x: function  (BREAKING)
```

**❌ Semantic Changes**
```ape
# Changing execution behavior
# v1.x: while evaluates condition before loop
# v2.x: while evaluates condition after loop  (BREAKING)
```

**❌ Public API Changes**
```python
# Removing or changing public API
# v1.x: executor.execute(ast, context)
# v2.x: executor.run(ast)  (BREAKING)
```

**❌ Type System Changes**
```ape
# Changing type inference or validation
# v1.x: Integer accepted
# v2.x: Integer rejected  (BREAKING)
```

**❌ Error Behavior Changes**
```python
# Changing when errors are raised
# v1.x: Missing capability → CapabilityError
# v2.x: Missing capability → silent ignore  (BREAKING)
```

### 2.2 NON-BREAKING (Minor/Patch OK)

**✅ Adding New Syntax (with new keywords)**
```ape
# v1.0: No match statement
# v1.5: match statement added (with new "match" keyword)
# Non-breaking: old code still works
```

**✅ Adding New APIs**
```python
# v1.0: No explanation API
# v1.2: ExplanationEngine added
# Non-breaking: additive only
```

**✅ Performance Improvements**
```python
# v1.0: Slow executor
# v1.1: 10x faster executor
# Non-breaking: same output, faster
```

**✅ Bug Fixes**
```python
# v1.0: loop variable leaks into parent scope (bug)
# v1.0.1: loop variable scoped correctly (fix)
# Non-breaking: bug fixes don't count as breaking
```

**✅ Documentation**
```markdown
# Clarifications, examples, typo fixes
# Always non-breaking
```

### 2.3 Edge Cases

**Security Fixes**
- If fix changes behavior: Patch version + migration guide
- If fix requires breaking change: Fast-tracked major version

**Accidental Breaking Changes**
- Revert in patch release
- Document in CHANGELOG as regression
- Add test to prevent recurrence

---

## 3. Deprecation Process

### 3.1 Deprecation Timeline

**Minor Version N: Deprecate**
- Mark feature as deprecated
- Add runtime warning (optional)
- Document alternative in CHANGELOG

**Minor Version N+1: Still Works**
- Feature still functional
- Warning remains
- Migration guide updated

**Major Version N+1: Remove**
- Feature removed
- Breaking change documented
- Migration guide final

**Example:**
```
v1.5.0 - Deprecate old_api()
v1.6.0 - old_api() still works with warning
v1.7.0 - old_api() still works with warning
v2.0.0 - old_api() removed
```

### 3.2 Deprecation Notice Format

**In Code:**
```python
@deprecated(since="1.5.0", remove_in="2.0.0", alternative="new_api")
def old_api():
    warnings.warn(
        "old_api() is deprecated since 1.5.0 and will be removed in 2.0.0. "
        "Use new_api() instead.",
        DeprecationWarning
    )
```

**In Docs:**
```markdown
## old_api()

⚠️ **DEPRECATED** - Since v1.5.0, removed in v2.0.0  
Use `new_api()` instead.
```

**In CHANGELOG:**
```markdown
## [1.5.0] - 2025-03-15

### Deprecated
- `old_api()` - Use `new_api()` instead. Removal planned for 2.0.0.
```

### 3.3 What Can Be Deprecated

**✅ Allowed:**
- Semi-internal APIs (with notice)
- Experimental features
- Suboptimal APIs with better alternatives

**❌ Not Allowed (1.x):**
- Core syntax
- Public API (compile, validate, run)
- Built-in capabilities
- Error types

---

## 4. Experimental Features

### 4.1 Marking Experimental

Features may be marked experimental:

**In Code:**
```python
@experimental(since="1.3.0", stable_in="1.5.0 or 2.0.0")
class NewFeature:
    pass
```

**In Docs:**
```markdown
## NewFeature

🧪 **EXPERIMENTAL** - Since v1.3.0  
API may change in minor releases. Stabilizes in 1.5.0 or 2.0.0.
```

**In CHANGELOG:**
```markdown
## [1.3.0] - 2025-06-01

### Experimental
- NewFeature API - Subject to change in minor releases
```

### 4.2 Experimental Stability

**Experimental features:**
- ✅ Can change in minor versions (within reason)
- ✅ Can be removed in major versions
- ❌ Cannot break stable features
- ❌ Cannot be used in critical path

**Stability Timeline:**
```
v1.3.0 - Experimental feature added
v1.4.0 - Experimental (may change)
v1.5.0 - Stable (no changes without deprecation)
```

### 4.3 Graduation to Stable

**Requirements:**
- At least 1 minor version cycle as experimental
- Positive community feedback
- No outstanding design issues
- Test coverage >90%

---

## 5. Release Process

### 5.1 Release Branches

**Main Branches:**
- `main` - Latest stable release (v1.0.0, v1.1.0, etc.)
- `develop` - Next minor release (v1.1.0-dev)

**Release Branches:**
- `release/1.0.x` - Patch releases for v1.0
- `release/1.1.x` - Patch releases for v1.1
- `release/2.0.x` - Next major release

### 5.2 Release Checklist

**Pre-Release:**
1. ✅ All tests passing (265+)
2. ✅ CHANGELOG updated
3. ✅ Version bumped in `pyproject.toml`
4. ✅ Documentation updated
5. ✅ Migration guide (if breaking changes)
6. ✅ Deprecation notices reviewed

**Release:**
1. Create release branch (`release/1.x.y`)
2. Tag release (`git tag v1.x.y`)
3. Build package (`python -m build`)
4. Upload to PyPI (`twine upload`)
5. Create GitHub release with CHANGELOG excerpt

**Post-Release:**
1. Merge release branch to `main`
2. Merge `main` to `develop`
3. Announce on Discord/Slack/Twitter
4. Update website (if applicable)

### 5.3 Hotfix Process

**For Critical Bugs:**
1. Create hotfix branch from `main`
2. Fix bug + add regression test
3. Bump patch version
4. Tag and release
5. Merge to `main` and `develop`

**Timeline:** <24 hours for security issues, <1 week for critical bugs.

---

## 6. Long-Term Support (LTS)

### 6.1 LTS Policy

**No LTS in v1.x**
- All users should stay on latest 1.x release
- Security patches backported to 1.x (not 0.x)

**Potential LTS in 2.x+**
- TBD based on adoption and community needs

---

## 7. Version Support

### 7.1 Supported Versions

**Currently Supported:**
- `v1.x` - Active development
- `v0.x` - Unsupported (upgrade to 1.0)

**When v2.0 Releases:**
- `v2.x` - Active development
- `v1.x` - Security patches only (6 months)
- `v0.x` - Unsupported

### 7.2 Python Version Support

**Minimum Python Version:**
- APE 1.0: Python 3.11+
- APE 2.0: Python 3.12+ (TBD)

**Support Policy:**
- Support last 3 Python minor versions
- Drop support in major APE releases only

---

## 8. Specification Updates

### 8.1 Specification Versioning

Specification version matches APE version:
- APE 1.0.0 → APE_1.0_SPECIFICATION.md
- APE 2.0.0 → APE_2.0_SPECIFICATION.md

### 8.2 Specification Changes

**1.x Releases:**
- Clarifications allowed (non-normative)
- No semantic changes
- Errata fixed in patch releases

**2.0 Release:**
- New specification document
- Breaking changes documented
- Migration guide required

---

## 9. Community Involvement

### 9.1 RFC Process (Future)

**For Major Changes:**
1. Propose RFC (Request for Comments)
2. Community discussion (2-4 weeks)
3. Decision by maintainers
4. Implementation in next major version

**RFC Required For:**
- Breaking changes
- New major features
- Architectural changes

### 9.2 Issue Tracking

**Labels:**
- `bug` - Bug reports
- `enhancement` - Feature requests
- `breaking-change` - Requires major version
- `experimental` - Unstable API
- `good-first-issue` - For new contributors

---

## 10. Security Policy

### 10.1 Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

**Instead:**
1. Email: security@ape-lang.org (TBD)
2. Include: APE version, description, reproduction steps
3. Allow 48 hours for initial response

### 10.2 Security Patch Timeline

**Critical:** <24 hours  
**High:** <1 week  
**Medium:** <1 month  
**Low:** Next patch release

### 10.3 Security Advisories

Published on:
- GitHub Security Advisories
- CHANGELOG.md
- Official website/blog

---

## 11. Compatibility Guarantees

### 11.1 What's Guaranteed in 1.x

**✅ Source Code Compatibility**
- All valid v1.0 APE code runs on v1.x

**✅ Public API Compatibility**
- All public APIs work identically

**✅ Semantic Compatibility**
- Execution behavior unchanged

**✅ Error Compatibility**
- Error types remain

### 11.2 What's NOT Guaranteed

**❌ Binary Compatibility**
- Bytecode/AST format may change

**❌ Internal API Compatibility**
- Lexer, parser internals may change

**❌ Performance Characteristics**
- Speed/memory may improve or regress

**❌ Error Messages**
- Wording may change (not error types)

---

## 12. Example Release Timeline

### 12.1 Hypothetical v1.x Releases

```
v1.0.0 (2025-01-15) - Initial stable release
v1.0.1 (2025-01-22) - Bug fix: loop variable scoping
v1.1.0 (2025-02-15) - New feature: match expressions
v1.1.1 (2025-02-20) - Bug fix: match exhaustiveness
v1.2.0 (2025-04-01) - New stdlib: async module (experimental)
v1.3.0 (2025-06-01) - Deprecate old_api()
v1.4.0 (2025-08-01) - async module stable
v1.5.0 (2025-10-01) - Performance improvements
v2.0.0 (2026-01-01) - Remove old_api(), breaking changes
```

### 12.2 Cadence

**Target:**
- Patch: As needed (bug fixes)
- Minor: Every 2-3 months
- Major: Every 12-18 months

**Actual cadence depends on community needs and contribution velocity.**

---

## 13. Tooling & Automation

### 13.1 Version Bumping

**Automated:**
- `bumpversion patch` - Bump patch version
- `bumpversion minor` - Bump minor version
- `bumpversion major` - Bump major version

**Manual Steps:**
- Update CHANGELOG.md
- Update APE_1.0_SPECIFICATION.md (if needed)
- Update migration guides

### 13.2 CI/CD

**On Every Commit:**
- Run test suite (265+ tests)
- Check code formatting (Black, isort)
- Run linters (Pylint, mypy)

**On Release:**
- Build wheel + sdist
- Upload to PyPI
- Create GitHub release
- Update documentation

---

## 14. Migration Guides

### 14.1 When Required

**Migration guide required for:**
- Major version releases (1.0 → 2.0)
- Deprecations (when feature removed)
- Breaking changes (even if justified)

### 14.2 Migration Guide Template

```markdown
# Migration Guide: v1.x to v2.0

## Breaking Changes

### 1. old_api() Removed
**What Changed:** old_api() no longer exists  
**Why:** Replaced by new_api() with better semantics  
**Migration:**
```python
# v1.x
result = old_api(x, y)

# v2.0
result = new_api(x, y)
```

### 2. Syntax Change: task → function
**What Changed:** keyword changed  
**Why:** Better aligns with other languages  
**Migration:** Use find-replace to update `.ape` files
```

---

## 15. Governance Roles

### 15.1 Maintainers

**Responsibilities:**
- Review pull requests
- Merge approved changes
- Cut releases
- Triage issues

**Current Maintainers:**
- TBD (Open to community)

### 15.2 Core Contributors

**Responsibilities:**
- Contribute features
- Fix bugs
- Write tests
- Improve documentation

**How to Become Core Contributor:**
- 5+ merged PRs
- Consistent engagement
- Positive community interaction

---

## 16. References

- **SemVer 2.0.0:** https://semver.org
- **Keep a Changelog:** https://keepachangelog.com
- **APE_1.0_SPECIFICATION.md** - Language specification
- **PUBLIC_API_CONTRACT.md** - API stability guarantees

---

**Status:** ✅ Active  
**Version:** 1.0.0  
**Authority:** Governs all APE v1.x releases  
**Updates:** Require minor version bump (non-breaking updates only)

This governance policy ensures APE releases are predictable, stable, and community-friendly.
