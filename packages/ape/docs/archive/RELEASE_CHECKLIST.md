# 🚀 Ape v0.2.0 Release Checklist

**Status:** ✅ READY FOR PUBLICATION  
**Version:** 0.2.0  
**Date Prepared:** December 4, 2025

---

## ✅ Pre-Release Tasks (COMPLETED)

- [x] **Version bump** to 0.2.0 in `pyproject.toml`
- [x] **CHANGELOG.md** updated with complete v0.2.0 section
- [x] **Test suite** passing: 192/192 tests (0.53s)
- [x] **Build packages** created:
  - `dist/ape_lang-0.2.0-py3-none-any.whl` (39.7 KB)
  - `dist/ape_lang-0.2.0.tar.gz` (38.9 KB)
- [x] **Documentation** complete:
  - README.md updated
  - docs/philosophy.md created
  - docs/modules_and_imports.md updated
  - docs/README.md created
- [x] **Release notes** prepared:
  - RELEASE_NOTES.md (complete guide)
  - RELEASE_SUMMARY.md (executive summary)
  - GitHub release text ready to copy-paste

---

## 📋 Manual Release Tasks (TODO)

### 1. Git Tag (Required)

```bash
cd c:\Users\quyna\Documents\Ape_v0.1.2
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

**Verification:**
```bash
git tag -l | Select-String "0.2.0"
```

### 2. GitHub Release (Required)

1. **Go to:** https://github.com/Quynah/Ape/releases/new
2. **Tag version:** Select `v0.2.0` (after pushing tag)
3. **Release title:** `v0.2.0 — Module System & Standard Library`
4. **Description:** Copy from `RELEASE_NOTES.md` (GitHub Release Text section)
5. **Attach files (optional):**
   - Upload `dist/ape_lang-0.2.0-py3-none-any.whl`
   - Upload `dist/ape_lang-0.2.0.tar.gz`
6. **Click:** "Publish release"

**Verification:**
- Visit https://github.com/Quynah/Ape/releases
- Confirm v0.2.0 is listed
- Check that release notes display correctly

### 3. PyPI Upload (Required)

**⚠️ IMPORTANT:** This makes the release public and permanent!

**Option A: Test on TestPyPI first (recommended)**

```bash
cd c:\Users\quyna\Documents\Ape_v0.1.2
twine upload --repository testpypi dist/ape_lang-0.2.0*
```

Verify:
```bash
pip install -i https://test.pypi.org/simple/ ape-lang==0.2.0
ape --version
```

**Option B: Upload to production PyPI**

```bash
cd c:\Users\quyna\Documents\Ape_v0.1.2
twine upload dist/ape_lang-0.2.0*
```

**Verification:**
- Visit https://pypi.org/project/ape-lang/
- Confirm version 0.2.0 is listed
- Check that description and links are correct

### 4. Installation Test (Required)

```bash
# Create fresh virtual environment
python -m venv test_env
test_env\Scripts\activate

# Install from PyPI
pip install ape-lang==0.2.0

# Verify installation
ape --version
# Should output: 0.2.0

# Test with example
cd examples
ape validate hello_imports.ape
ape build hello_imports.ape --target=python

# Deactivate
deactivate
```

---

## 📊 Verification Matrix

| Task | Status | Notes |
|------|--------|-------|
| Version in pyproject.toml | ✅ | 0.2.0 |
| CHANGELOG.md | ✅ | Complete v0.2.0 section |
| Tests passing | ✅ | 192/192 (0.53s) |
| Wheel built | ✅ | 39.7 KB |
| Source dist built | ✅ | 38.9 KB |
| README updated | ✅ | v0.2.0 features |
| Docs updated | ✅ | 5 doc files |
| Git tag created | ⏳ | Manual step |
| GitHub release | ⏳ | Manual step |
| PyPI upload | ⏳ | Manual step |
| Installation verified | ⏳ | After PyPI upload |

---

## 📦 Build Artifacts

**Location:** `c:\Users\quyna\Documents\Ape_v0.1.2\dist\`

**Files:**
```
ape_lang-0.2.0-py3-none-any.whl  (39,706 bytes)
ape_lang-0.2.0.tar.gz            (38,929 bytes)
```

**SHA256 Checksums:**
```bash
# Generate checksums (optional)
cd c:\Users\quyna\Documents\Ape_v0.1.2\dist
Get-FileHash ape_lang-0.2.0-py3-none-any.whl -Algorithm SHA256
Get-FileHash ape_lang-0.2.0.tar.gz -Algorithm SHA256
```

---

## 📖 Documentation Files

All ready for reference:

- **README.md** - Main project documentation
- **CHANGELOG.md** - Version history (v0.2.0 section complete)
- **RELEASE_NOTES.md** - Comprehensive release guide
- **RELEASE_SUMMARY.md** - Executive summary
- **docs/philosophy.md** - Design philosophy
- **docs/modules_and_imports.md** - Module system spec (1334 lines)
- **docs/README.md** - Documentation index

---

## 🎯 Quick Commands Reference

**For copy-paste convenience:**

```bash
# Tag and push
git tag v0.2.0
git push origin v0.2.0

# Test on TestPyPI
twine upload --repository testpypi dist/ape_lang-0.2.0*

# Upload to PyPI (production)
twine upload dist/ape_lang-0.2.0*

# Verify installation
pip install ape-lang==0.2.0
ape --version
```

---

## 🚦 Release Decision

**Ready to proceed?** 

If yes, execute the manual steps in order:
1. Git tag → 2. GitHub release → 3. PyPI upload → 4. Verification

**Need more time?**

All preparation is complete. You can:
- Review the release notes
- Test the build artifacts locally
- Update any documentation
- Return to complete manual steps when ready

---

## 📞 Support

If issues arise during release:

1. **Build problems:** Re-run `python -m build`
2. **Test failures:** Check with `pytest tests/ -v`
3. **Upload issues:** Verify PyPI credentials with `twine check dist/ape_lang-0.2.0*`
4. **Documentation errors:** Edit and regenerate as needed

---

## ✨ Post-Release

After successful publication:

- [ ] Announce on GitHub Discussions
- [ ] Update project website (if applicable)
- [ ] Share on social media
- [ ] Notify early adopters
- [ ] Begin planning v0.3.0 features

---

**🎉 Ready to release Ape v0.2.0 to the world!**

See `RELEASE_NOTES.md` for detailed instructions on each manual step.
