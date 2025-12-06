# APE Multi-Language Surface Syntax

**Version:** 1.0.0  
**Status:** Active  
**Scope:** Latin script languages only

This document explains APE's multi-language surface syntax feature, what it means, what it explicitly does NOT mean, and how it maintains determinism and safety.

---

## 1. What "Multi-Language" Means in APE

**APE is ONE language with multiple surface syntaxes.**

Multi-language support in APE means:
- ✅ Developers can write APE code using keywords from their native language
- ✅ All languages normalize to the same canonical APE syntax (English)
- ✅ The AST, parser, runtime, and semantics remain completely unchanged
- ✅ Deterministic keyword-only mapping (no NLP, no heuristics, no guessing)
- ✅ Identical execution behavior regardless of input language

**Example:**

```python
# English
if x > 5:
    - set y to 10

# Dutch
als x > 5:
    - set y to 10

# French
si x > 5:
    - set y to 10
```

All three produce **identical AST** and **identical runtime behavior**.

---

## 2. What Multi-Language Does NOT Mean

APE multi-language is **NOT**:

❌ **Multiple programming languages** - There is only one APE language  
❌ **Natural language processing** - No LLM, no AI, no "understanding"  
❌ **Fuzzy matching** - Keywords must match exactly (whole-word)  
❌ **Automatic translation** - Only explicitly mapped keywords are translated  
❌ **Localized identifiers** - Variable/function names remain unchanged  
❌ **Localized error messages** - Errors remain in English  
❌ **Culture-specific behavior** - Runtime behavior is identical across all languages  

**Example of what is NOT supported:**

```python
# ❌ This does NOT work - identifiers are not translated
als gebruiker_naam == "admin":
    # Variable name stays in Dutch, only keywords translate
```

---

## 3. Architecture

### 3.1 Language Adapters (Pre-Tokenization Layer)

Language adapters operate **before tokenization**:

```
Source Code (any language)
         ↓
LanguageAdapter.normalize_source()
         ↓
Canonical APE (English keywords)
         ↓
Tokenizer (unchanged)
         ↓
Parser (unchanged)
         ↓
AST (canonical, language-independent)
         ↓
Runtime (unchanged)
```

### 3.2 Design Principles

**Determinism First:**
- Keyword mapping is exact, whole-word, lookup-based
- Same input → same normalized output, always
- No heuristics, no probabilistic matching

**Safety:**
- Unknown keywords → fail at parse time (not runtime)
- Ambiguous input → fail immediately
- No silent failures or assumptions

**Separation of Concerns:**
- Language adapters = surface syntax normalization only
- Parser/runtime = unchanged, language-agnostic
- One canonical AST for all languages

---

## 4. Supported Languages (v1.0.0)

All supported languages use **Latin script only**.

### 4.1 English (en) - Canonical

English is the canonical APE syntax. The English adapter is an **identity transformation** (no changes).

**Keywords:** `if`, `else`, `while`, `for`, `in`, `and`, `or`, `not`

### 4.2 Dutch (nl)

| Dutch | English |
|-------|---------|
| `als` | `if` |
| `anders` | `else` |
| `zolang` | `while` |
| `voor` | `for` |
| `in` | `in` |
| `en` | `and` |
| `of` | `or` |
| `niet` | `not` |

### 4.3 French (fr)

| French | English |
|--------|---------|
| `si` | `if` |
| `sinon` | `else` |
| `tant que` | `while` |
| `pour` | `for` |
| `dans` | `in` |
| `et` | `and` |
| `ou` | `or` |
| `pas` | `not` |

**Note:** `tant que` is a multi-word keyword (matches "tant que" as a phrase).

### 4.4 German (de)

| German | English |
|--------|---------|
| `wenn` | `if` |
| `sonst` | `else` |
| `solange` | `while` |
| `für` | `for` |
| `in` | `in` |
| `und` | `and` |
| `oder` | `or` |
| `nicht` | `not` |

### 4.5 Spanish (es)

| Spanish | English |
|---------|---------|
| `si` | `if` |
| `sino` | `else` |
| `mientras` | `while` |
| `para` | `for` |
| `en` | `in` |
| `y` | `and` |
| `o` | `or` |
| `no` | `not` |

### 4.6 Italian (it)

| Italian | English |
|---------|---------|
| `se` | `if` |
| `altrimenti` | `else` |
| `mentre` | `while` |
| `per` | `for` |
| `in` | `in` |
| `e` | `and` |
| `o` | `or` |
| `non` | `not` |

### 4.7 Portuguese (pt)

| Portuguese | English |
|------------|---------|
| `se` | `if` |
| `senão` | `else` |
| `enquanto` | `while` |
| `para` | `for` |
| `em` | `in` |
| `e` | `and` |
| `ou` | `or` |
| `não` | `not` |

---

## 5. Usage

### 5.1 Using run() with Language Parameter

```python
from ape import run

# English (default)
result = run("""
if x > 5:
    - set y to 10
""", context={'x': 10})

# Dutch
result = run("""
als x > 5:
    - set y to 10
""", context={'x': 10}, language='nl')

# French
result = run("""
si x > 5:
    - set y to 10
""", context={'x': 10}, language='fr')
```

### 5.2 Using Language Adapters Directly

```python
from ape.lang import get_adapter

# Get Dutch adapter
adapter = get_adapter('nl')

# Normalize Dutch source to canonical APE
dutch_source = "als x > 5:\n    - set y to 10"
canonical_source = adapter.normalize_source(dutch_source)

# Now canonical_source is: "if x > 5:\n    - set y to 10"
# Can be parsed normally
```

### 5.3 Listing Supported Languages

```python
from ape.lang import list_supported_languages

languages = list_supported_languages()
# Returns: ['de', 'en', 'es', 'fr', 'it', 'nl', 'pt']
```

---

## 6. Why No Non-Latin Scripts?

APE v1.0.0 deliberately supports **Latin script languages only**.

**Reasons:**
1. **Keyboard accessibility** - Latin keyboards are widely available
2. **ASCII compatibility** - Easier integration with existing tools
3. **Clear scope** - Latin script provides consistent word boundaries
4. **Testing burden** - Non-Latin scripts require extensive Unicode testing
5. **Incremental rollout** - Validate approach before expanding

**Future consideration (v2.0+):**
- Cyrillic script (Russian, Bulgarian)
- Arabic script (Arabic, Persian)
- Devanagari script (Hindi)
- Han characters (Chinese, Japanese)

**Not a statement about language importance** - purely a pragmatic phased rollout.

---

## 7. Adding New Language Adapters

### 7.1 Requirements

To add a new language adapter:

1. Language uses **Latin script**
2. Clear keyword mappings exist
3. No keyword conflicts with identifiers
4. Whole-word matching is sufficient

### 7.2 Implementation Steps

1. **Create adapter file** in `src/ape/lang/<code>.py`

```python
from typing import Dict
from ape.lang.base import LanguageAdapter

class YourLanguageAdapter(LanguageAdapter):
    def __init__(self):
        super().__init__(
            language_code="xx",
            language_name="YourLanguage",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        return {
            'your_if': 'if',
            'your_else': 'else',
            # ... other keywords
        }
```

2. **Register adapter** in `src/ape/lang/registry.py`

```python
from ape.lang.xx import YourLanguageAdapter

# In _register_builtin_adapters():
register_adapter(YourLanguageAdapter())
```

3. **Add tests** in `tests/lang/test_multilanguage.py`

```python
def test_your_language_if_keyword():
    adapter = get_adapter('xx')
    source = "your_if x > 5:\n    - set y to 10"
    normalized = adapter.normalize_source(source)
    assert 'if x > 5:' in normalized
```

4. **Update documentation** (this file)

---

## 8. Determinism Guarantees

### 8.1 Same Input → Same Output

Language adapters are **deterministic**:

```python
adapter = get_adapter('nl')
source = "als x > 5:\n    - set y to 10"

result1 = adapter.normalize_source(source)
result2 = adapter.normalize_source(source)
result3 = adapter.normalize_source(source)

# Always identical
assert result1 == result2 == result3
```

### 8.2 Identical AST Across Languages

```python
# English
en_source = "if x > 5:\n    - set y to 10"
en_ast = parse_ape_source(en_source)

# Dutch
nl_source = "als x > 5:\n    - set y to 10"
nl_adapter = get_adapter('nl')
nl_normalized = nl_adapter.normalize_source(nl_source)
nl_ast = parse_ape_source(nl_normalized)

# ASTs are structurally identical
assert type(en_ast) == type(nl_ast)
```

### 8.3 Identical Runtime Behavior

```python
# English version
result_en = run("if x > 5:\n    - set y to 10", context={'x': 10})

# Dutch version
result_nl = run("als x > 5:\n    - set y to 10", context={'x': 10}, language='nl')

# Results are identical
assert result_en == result_nl
```

---

## 9. Error Handling

### 9.1 Unsupported Language Code

```python
from ape import run
from ape.errors import ValidationError

try:
    run("if x > 5: ...", language='xx')
except ValidationError as e:
    print(e)  # "Unsupported language code 'xx'. Supported: de, en, es, fr, it, nl, pt"
```

### 9.2 Unknown Keywords

If source contains keywords not in the mapping, they pass through unchanged. The **parser will fail** (not the adapter).

```python
# Dutch with typo
source = "alss x > 5:\n    - set y to 10"  # 'alss' instead of 'als'

adapter = get_adapter('nl')
normalized = adapter.normalize_source(source)
# normalized still contains 'alss' (unknown keyword)

# Parser will fail with ParseError
parse_ape_source(normalized)  # ParseError: unexpected token 'alss'
```

**Design: Fail hard and early.**

---

## 10. Limitations

### 10.1 Keywords Only

Only **keywords** are translated. Identifiers, literals, and comments remain unchanged.

```python
# ✅ Works - keywords translated
als gebruiker_actief:
    - set status to "active"

# Becomes:
if gebruiker_actief:
    - set status to "active"
```

### 10.2 No Mixed Language Detection

Adapters do not detect mixed languages. If you use multiple languages in one file, behavior is undefined (keywords from all mappings will be applied).

**Best practice:** Use one language per file.

### 10.3 No Localized Error Messages

Error messages remain in English regardless of input language.

```python
# Dutch input
run("als x >:\n    - set y to 10", language='nl')
# Error message: "ParseError: unexpected token ':' at line 1"
# (not in Dutch)
```

---

## 11. Testing

All language adapters have comprehensive tests in `tests/lang/test_multilanguage.py`:

- ✅ Keyword normalization
- ✅ Identical AST across languages
- ✅ Identical runtime behavior
- ✅ Whole-word matching
- ✅ Determinism
- ✅ Error handling

**Run tests:**

```bash
pytest tests/lang/ -v
```

---

## 12. Governance

### 12.1 Language Addition Policy

New languages may be added in **minor releases** (e.g., 1.1.0, 1.2.0) if:
- Language uses Latin script (v1.x restriction)
- Clear keyword mappings exist
- Community contribution with tests
- No conflicts with existing languages

### 12.2 Keyword Changes

Keyword mappings are **stable within major versions**:
- Adding new keywords: **Minor release** (non-breaking)
- Changing existing mappings: **Major release** (breaking)
- Removing languages: **Major release** (breaking)

---

## 13. Future Extensions

**Planned for v2.0+:**
- Non-Latin scripts (Cyrillic, Arabic, Devanagari, Han)
- Module-level language declaration (`module calculator lang=nl`)
- Localized error messages (opt-in)
- Language auto-detection (based on keyword frequency)

**Not planned:**
- Automatic identifier translation (too ambiguous)
- Runtime language switching (violates determinism)
- Mixed-language files (increases complexity)

---

## 14. FAQ

### Q: Can I mix English and Dutch in the same file?

**A:** Technically yes, but **not recommended**. Both adapters will be applied, which may cause unexpected behavior. Best practice: one language per file.

### Q: Why are error messages in English only?

**A:** Localized error messages require significant infrastructure (translation files, message catalogs). This may come in v2.0+ but is out of scope for v1.0.1.

### Q: Can I use French variable names?

**A:** Yes! Identifiers are **not translated**. Only keywords are normalized.

```python
# ✅ Works perfectly
si nombre_utilisateurs > 10:
    - set statut to "actif"
```

### Q: What about Chinese/Japanese/Arabic?

**A:** v1.0.1 supports **Latin script only**. Non-Latin scripts are planned for v2.0+ after validating the approach with Latin languages.

### Q: Is this slower than English?

**A:** Negligible. Language normalization is a single-pass string operation before tokenization. Performance impact is <1% in practice.

### Q: Can I contribute a new language?

**A:** Yes! See [Section 7: Adding New Language Adapters](#7-adding-new-language-adapters). Must use Latin script for v1.x.

---

## 15. References

- **APE_1.0_SPECIFICATION.md** - Core language specification
- **src/ape/lang/** - Language adapter implementations
- **tests/lang/test_multilanguage.py** - Test suite

---

**Status:** ✅ Active  
**Version:** 1.0.0  
**Supported Languages:** EN, NL, FR, DE, ES, IT, PT (Latin script only)  
**Next:** Non-Latin scripts in v2.0+

This feature maintains APE's core principles: determinism, explicitness, and safety while making the language more accessible to non-English speakers.
