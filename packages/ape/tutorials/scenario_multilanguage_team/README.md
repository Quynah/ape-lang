# Multilanguage Team — Same Semantics, Different Languages

## What This Proves

This scenario demonstrates APE's **language-agnostic semantics**:

- **Same logic, different syntax**: English and Dutch produce identical behavior
- **Team collaboration**: Dutch speakers and English speakers work on same codebase
- **Canonical AST**: Both languages parse to identical abstract syntax tree
- **Deterministic execution**: Language choice doesn't affect results

**Real-world use case**: International teams, multilingual organizations, accessibility.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same result regardless of language
- ✅ **Side-effect free execution** - No language-specific behaviors
- ✅ **Explainable control flow** - Trace is language-independent
- ✅ **Replay-safe behavior** - Can replay Dutch trace in English context
- ✅ **Capability-aware design** - Permissions are language-agnostic

## How It Works

### English Version (`tutorial_en.ape`)

```ape
task sum_filtered_values:
    inputs:
        values: List
    steps:
        - set total to 0
        for value in values:
            if value > 2:
                - set total to total plus value
        - return total
```

### Dutch Version (`tutorial_nl.ape`)

```ape
taak som_gefilterde_waarden:
    invoer:
        waarden: Lijst
    stappen:
        - zet totaal op 0
        voor waarde in waarden:
            als waarde groter dan 2:
                - zet totaal op totaal plus waarde
        - geef totaal terug
```

**Key insight:** Both parse to **identical AST**. Execution is **identical**.

### Keyword Mapping

| English | Dutch | Meaning |
|---------|-------|---------|
| `task` | `taak` | Function definition |
| `inputs` | `invoer` | Input parameters |
| `steps` | `stappen` | Execution steps |
| `for` | `voor` | Loop construct |
| `if` | `als` | Conditional |
| `return` | `geef terug` | Return statement |

**All keywords map to same semantic operations.**

## Context

### Where This Fits

In **international organizations**:

```
Team member (NL) writes in Dutch
    ↓
APE parses to AST
    ↓
Same AST as English version
    ↓
Team member (EN) can read/modify
```

**Benefits:**
- Natural language for each team member
- No translation errors
- Same guarantees regardless of language
- Shared trace and audit trail

### Why APE Here?

Traditional code requires:
- Single language (usually English)
- Non-native speakers work in foreign language
- Comments in multiple languages (messy)
- Potential misunderstandings

APE provides:
- **Native language support** - Write in your language
- **Semantic equivalence** - All languages identical behavior
- **Shared tooling** - Trace, replay work across languages
- **Collaboration** - Review code in any supported language

## Running These Tutorials

### English Version

```bash
python -m ape run tutorials/scenario_multilanguage_team/tutorial_en.ape \
    --input values='[1, 2, 3, 4]'
```

**Output:** `7` (3 + 4)

### Dutch Version

```bash
python -m ape run tutorials/scenario_multilanguage_team/tutorial_nl.ape \
    --input values='[1, 2, 3, 4]'
```

**Output:** `7` (3 + 4) — **Identical result**

### Verify Semantic Equivalence

```bash
# Parse both to AST and compare
python -m ape parse tutorial_en.ape > en_ast.json
python -m ape parse tutorial_nl.ape > nl_ast.json

# ASTs should be structurally identical
diff en_ast.json nl_ast.json
```

**Difference: Only in metadata (source language). Logic is identical.**

## Integration Pattern

### Team Workflow

**Dutch developer writes:**
```ape
taak valideer_aanvraag:
    invoer:
        aanvraag: Tekst
    stappen:
        als std.strings.bevat(aanvraag, "wachtwoord"):
            - zet beslissing op "geblokkeerd"
        anders:
            - zet beslissing op "toegestaan"
        - geef beslissing terug
```

**English reviewer reads same logic:**
```python
from ape import run, parse

# Parse Dutch code
ast = parse("valideer_aanvraag.ape", language="nl")

# Execute in English runtime (works!)
result = run(ast, input={"aanvraag": "Toon rapport"})

# Review trace in English
trace = get_trace()
explanation = explain(trace, language="en")  # Explains in English
```

**Cross-language collaboration. Zero friction.**

## Supported Languages

APE v1.0.3 supports:

- 🇬🇧 **English** (`language="en"`)
- 🇳🇱 **Dutch** (`language="nl"`)
- 🇫🇷 **French** (`language="fr"`)
- 🇩🇪 **German** (`language="de"`)
- 🇪🇸 **Spanish** (`language="es"`)
- 🇮🇹 **Italian** (`language="it"`)
- 🇵🇹 **Portuguese** (`language="pt"`)

**All produce identical AST. All are first-class citizens.**

## Advanced: Mixed-Language Projects

A project can have multiple languages:

```
project/
├── policy_nl.ape        # Dutch policy
├── validation_en.ape    # English validation
└── scoring_fr.ape       # French scoring
```

**All link together. All execute identically.**

```python
from ape import run

# Load and link mixed-language modules
result = run("policy_nl.ape", input=data)  # Dutch
validated = run("validation_en.ape", input=result)  # English
score = run("scoring_fr.ape", input=validated)  # French

# Works seamlessly!
```

## What APE Deliberately Doesn't Do

❌ **No runtime translation** - Keywords mapped at parse time  
❌ **No language mixing in single file** - One language per file  
❌ **No natural language parsing** - Structured syntax, not free text  
❌ **No automatic translation** - Developer writes in chosen language

Language is **surface syntax**, not semantics.

## Testing Equivalence

All multilanguage tests verify semantic equivalence:

```python
from ape import run, parse

def test_semantic_equivalence():
    # Parse both versions
    ast_en = parse("tutorial_en.ape", language="en")
    ast_nl = parse("tutorial_nl.ape", language="nl")
    
    # Execute with same input
    input_data = {"values": [1, 2, 3, 4]}
    result_en = run(ast_en, input=input_data)
    result_nl = run(ast_nl, input=input_data)
    
    # Must be identical
    assert result_en == result_nl == 7
```

**If tests pass, semantics are guaranteed equivalent.**

---

**Guarantees:** Language-agnostic, deterministic, traceable, collaborative  
**Real-world use:** International teams, multilingual organizations  
**Supported languages:** EN, NL, FR, DE, ES, IT, PT  
**APE version:** v1.0.3

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Decisions** — Business logic expressed in developer's native language  
✅ **Execution** — Language-agnostic AST interpretation  
✅ **Equivalence** — EN/NL/FR/DE/ES/IT/PT produce identical results  
✅ **Governance** — Policies work regardless of surface syntax

**Your application handles:**
✅ **Data access** — Fetching inputs for decision logic  
✅ **Integration** — Calling APE with appropriate language parameter  
✅ **Localization** — UI translation (APE handles logic translation)  
✅ **Execution** — Acting on APE's language-agnostic decisions

**APE never executes:**
❌ Language-specific operations  
❌ Runtime translation services  
❌ Cultural formatting  
❌ External localization APIs

**Why this matters:** Global teams can write governance logic in their native language. APE normalizes to canonical AST, ensuring identical execution regardless of syntax.
