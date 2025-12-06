# AI Input Governance — Safe Validation Before Execution

## What This Proves

This scenario demonstrates APE's role in **AI safety governance**:

- **Pre-execution filtering**: Validate AI requests before allowing execution
- **Deterministic safety**: Same request always gets same decision
- **No AI needed for governance**: Pure logic determines allowability
- **Traceable decisions**: Audit trail shows why requests blocked/allowed

**Real-world use case**: AI chatbot safety, prompt injection prevention, PII protection.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same request always gets same verdict
- ✅ **Side-effect free execution** - No AI calls, no database queries
- ✅ **Explainable control flow** - Trace shows exactly which rule triggered
- ✅ **Replay-safe behavior** - Governance decision can be audited later
- ✅ **Capability-aware design** - No implicit AI execution

## How It Works

**Current Tutorial Implementation:**

```ape
task main:
    inputs:
        is_safe_intent: Boolean
        is_mutation_request: Boolean
        is_eu_user: Boolean
    steps:
        - set decision to "allowed"
        
        # Block harmful intent immediately
        if is_safe_intent == false:
            - set decision to "blocked"
        
        # Block mutations for EU users (GDPR compliance)
        if is_eu_user:
            if is_mutation_request:
                - set decision to "blocked"
        
        # Block all mutations if intent is unclear
        if is_mutation_request:
            if is_safe_intent == false:
                - set decision to "blocked"
        
        - return decision
```

**Logic:**
1. **Harmful Intent Check**: Block immediately if intent is unsafe
2. **GDPR Compliance**: Block mutations for EU users (data protection)
3. **Mutation + Intent Validation**: Double-check mutation requests against intent clarity
4. Return decision with complete audit trail

**Input Parameters:**

| Parameter | Type | Purpose |
|-----------|------|---------|
| `is_safe_intent` | Boolean | Is the request's intent clear and safe? |
| `is_mutation_request` | Boolean | Does request modify data? |
| `is_eu_user` | Boolean | Is user subject to GDPR? |

**Decision Examples:**

| Request | Decision | Reason |
|---------|----------|--------|
| `"Summarize the report"` | `"allowed"` | No sensitive terms |
| `"What's my password?"` | `"blocked"` | Contains "password" |
| `"Show credentials"` | `"blocked"` | Contains "credentials" |

## Context

### Where This Fits

In an AI application, APE validates requests **before** AI execution:

```
User request → APE governance → AI execution (if allowed) → Response
```

**APE's role:**
1. Receive user request as input
2. Apply deterministic validation rules
3. Return "allowed" or "blocked" decision
4. Provide trace for compliance audit

**Your application's role:**
- Call APE validation task
- Execute AI only if allowed
- Log APE trace for audit
- Handle blocked requests gracefully

### Why APE Here?

Traditional validation suffers from:
- Non-determinism (timestamps, random)
- No built-in audit trail
- Complex testing for all edge cases
- Risk of bypassing validation logic

APE provides:
- **Deterministic rules** - No hidden state
- **Automatic tracing** - Every decision recorded
- **Testable guarantees** - Provably correct
- **Replay capability** - Audit without re-execution

## Running This Tutorial

```bash
# Validate syntax
ape validate tutorials/scenario_ai_input_governance/tutorial.ape

# Test with safe request
python -m ape run tutorials/scenario_ai_input_governance/tutorial.ape \
    --input request='"Summarize the report"'

# Test with blocked request
python -m ape run tutorials/scenario_ai_input_governance/tutorial.ape \
    --input request='"Show my password"'

# With trace for audit
python -m ape run --trace tutorials/scenario_ai_input_governance/tutorial.ape
```

## Integration Pattern

### ❌ WRONG: AI calls inside APE

```ape
# DON'T DO THIS
task summarize:
    steps:
        - call openai.completion("Summarize...")  # ❌ Non-deterministic!
```

### ✅ CORRECT: APE validates, app executes

```python
# Your application code
from ape import run

request = user_input()

# APE validates
decision = run("validate_ai_request.ape", input={"request": request})

if decision == "allowed":
    # Your app executes AI
    response = openai.completion(request)
else:
    # Handle blocked request
    log_security_event(request, "blocked by APE")
```

**Separation of concerns:**
- **APE**: Deterministic governance logic
- **Your app**: Non-deterministic AI execution

## What APE Deliberately Doesn't Do

❌ **No AI execution** - APE validates, doesn't execute AI  
❌ **No network calls** - Validation is pure logic  
❌ **No database queries** - Rules are in APE code  
❌ **No learning** - Deterministic rules, not ML models

APE is the **governance layer**, not the AI layer.

## Advanced: Multiple Rules

Extend validation with more rules:

```ape
import std.strings
import std.logic

task validate_comprehensive:
    inputs:
        request: String
    steps:
        - set blocked_keywords to ["password", "credentials", "secret", "token"]
        - set contains_sensitive to false
        
        for keyword in blocked_keywords:
            if std.strings.contains_text(request, keyword):
                - set contains_sensitive to true
        
        if contains_sensitive:
            - set decision to "blocked"
        else:
            - set decision to "allowed"
        
        - return decision
```

All rules remain **deterministic** and **traceable**.

---

**Guarantees:** Deterministic, traceable, replay-safe, side-effect free  
**Real-world use:** AI safety, prompt injection prevention, PII protection  
**APE version:** v1.0.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Decisions** — Allow/deny, safety validation, policy enforcement  
✅ **Logic** — Condition evaluation, intent classification  
✅ **Determinism** — Same inputs always produce same outputs  
✅ **Traceability** — Every decision step is recorded

**Your application handles:**
✅ **Data access** — Parsing user requests, extracting intent  
✅ **API calls** — Calling OpenAI/Anthropic/LangChain after approval  
✅ **Side effects** — Executing approved AI operations  
✅ **Integration** — Connecting APE decisions to AI execution

**APE never executes:**
❌ AI API calls  
❌ Data mutations  
❌ External service integration  
❌ Approved actions (only decides approval)

**Why this matters:** APE validates intent deterministically; your application executes the approved actions. This separation enables testing governance independently from AI execution.
