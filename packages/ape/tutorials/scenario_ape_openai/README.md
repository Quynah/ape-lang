# APE + OpenAI Integration — Governance Over AI

## What This Proves

This scenario demonstrates **correct APE + OpenAI integration**:

- **APE validates intent**: Deterministic governance BEFORE AI execution
- **No AI in APE**: OpenAI calls happen in your application, not APE runtime
- **Traceable decisions**: Why AI was allowed/blocked is fully auditable
- **Capability separation**: APE decides, your app executes

**Real-world use case**: AI chatbots, content generation, code assistants.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same intent always gets same decision
- ✅ **Side-effect free execution** - No AI calls in APE
- ✅ **Explainable control flow** - Trace shows governance logic
- ✅ **Replay-safe behavior** - Audit governance without AI re-execution
- ✅ **Capability-aware design** - AI execution requires explicit permission

## How It Works

### APE Task (Governance Layer)

```ape
task validate_openai_intent:
    inputs:
        intent: String
    steps:
        if intent == "classify":
            - set decision to "allowed"
        else if intent == "summarize":
            - set decision to "allowed"
        else if intent == "execute_code":
            - set decision to "blocked"
        else:
            - set decision to "review_required"
        - return decision
```

**APE's role:**
- Receive intended AI operation as input
- Apply deterministic validation rules
- Return governance decision
- Provide audit trail

**APE does NOT:**
- Call OpenAI API
- Execute AI models
- Handle API keys
- Process AI responses

### Integration Pattern

```python
from ape import run
import openai

def execute_with_governance(user_request: str) -> str:
    # Step 1: Determine intent (your logic)
    intent = classify_intent(user_request)  # e.g., "summarize"
    
    # Step 2: APE validates intent
    decision = run("validate_openai_intent.ape", input={"intent": intent})
    
    # Step 3: Act based on governance decision
    if decision == "allowed":
        # Your app executes OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_request}]
        )
        return response.choices[0].message.content
    
    elif decision == "blocked":
        return "Request blocked by governance policy"
    
    elif decision == "review_required":
        # Queue for human review
        queue_for_review(user_request, intent)
        return "Request queued for review"
```

**Separation of concerns:**
- **APE**: Deterministic, traceable governance
- **Your app**: Non-deterministic AI execution
- **OpenAI**: Language model inference

## Context

### Where This Fits

In **AI-powered applications**:

```
User request → Intent classification → APE governance → OpenAI execution → Response
                     ↓                       ↓                    ↓
                Your code              APE task            Your code
```

**Why this architecture?**

1. **Governance is deterministic** - APE guarantees same input → same decision
2. **AI execution is non-deterministic** - OpenAI may produce different responses
3. **Audit trail is separate** - APE trace shows governance, not AI outputs
4. **Replay is possible** - Can verify governance without re-calling AI

### Why APE Here?

Traditional AI integration suffers from:
- Non-deterministic governance (timestamps, random)
- No audit trail for why AI was allowed/blocked
- Difficult to test all scenarios
- Can't replay decisions without re-executing AI

APE provides:
- **Deterministic governance** - Always same decision for same intent
- **Complete audit trail** - Trace shows exactly why allowed/blocked
- **Testable guarantees** - Provably correct validation
- **Replay capability** - Audit without AI re-execution

## Running This Tutorial

```bash
# Validate allowed intent
python -m ape run tutorials/scenario_ape_openai/tutorial.ape \
    --input intent='"classify"'

# Validate blocked intent
python -m ape run tutorials/scenario_ape_openai/tutorial.ape \
    --input intent='"execute_code"'

# With trace for audit
python -m ape run --trace tutorials/scenario_ape_openai/tutorial.ape \
    --input intent='"classify"'
```

## Complete Integration Example

### Full Application Code

```python
from ape import run
from ape.runtime import TraceCollector
import openai
import logging

class GovernedOpenAI:
    def __init__(self, governance_policy: str):
        self.policy = governance_policy
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def execute(self, user_request: str) -> dict:
        # Classify intent
        intent = self._classify_intent(user_request)
        
        # APE governance
        trace = TraceCollector()
        decision = run(
            self.policy,
            input={"intent": intent},
            trace=trace
        )
        
        # Log governance decision
        logging.info(f"Governance: intent={intent}, decision={decision}")
        
        # Act based on decision
        if decision == "allowed":
            response = self._call_openai(user_request)
            return {
                "status": "success",
                "response": response,
                "governance_trace": trace
            }
        
        elif decision == "blocked":
            logging.warning(f"Blocked request: intent={intent}")
            return {
                "status": "blocked",
                "reason": "Governance policy violation",
                "governance_trace": trace
            }
        
        else:  # review_required
            review_id = self._queue_for_review(user_request, intent)
            return {
                "status": "pending_review",
                "review_id": review_id,
                "governance_trace": trace
            }
    
    def _classify_intent(self, request: str) -> str:
        # Your intent classification logic
        if "summarize" in request.lower():
            return "summarize"
        elif "classify" in request.lower():
            return "classify"
        elif "execute" in request.lower() or "run code" in request.lower():
            return "execute_code"
        else:
            return "unknown"
    
    def _call_openai(self, request: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": request}]
        )
        return response.choices[0].message.content

# Usage
ai = GovernedOpenAI("validate_openai_intent.ape")

# Safe request
result = ai.execute("Classify this document")
print(result["response"])  # OpenAI response

# Blocked request
result = ai.execute("Execute this Python code")
print(result["status"])  # "blocked"
```

## Advanced: Dynamic Rules

Extend governance with runtime configuration:

```ape
import std.collections

task validate_with_config:
    inputs:
        intent: String
        allowed_intents: List
    steps:
        if std.collections.contains(allowed_intents, intent):
            - set decision to "allowed"
        else:
            - set decision to "blocked"
        - return decision
```

**Configuration provided at runtime:**

```python
config = load_config()  # ["classify", "summarize"]
decision = run("validate_with_config.ape", input={
    "intent": "classify",
    "allowed_intents": config
})
```

## What APE Deliberately Doesn't Do

❌ **No OpenAI API calls** - APE validates, doesn't execute AI  
❌ **No API key management** - Your app handles credentials  
❌ **No response processing** - APE governs input, not output  
❌ **No rate limiting** - Your app implements infrastructure concerns

APE is **governance layer**, not AI execution layer.

## Testing Governance

Test APE governance without OpenAI:

```python
import pytest
from ape import run

def test_allowed_intents():
    for intent in ["classify", "summarize"]:
        decision = run("validate_openai_intent.ape", input={"intent": intent})
        assert decision == "allowed"

def test_blocked_intents():
    decision = run("validate_openai_intent.ape", input={"intent": "execute_code"})
    assert decision == "blocked"

def test_unknown_intents():
    decision = run("validate_openai_intent.ape", input={"intent": "hack_system"})
    assert decision == "review_required"
```

**Test governance independently from AI execution.**

## Compliance & Audit

For regulatory compliance:

```python
from ape.runtime import ExplanationEngine

def audit_ai_decision(request_id: str):
    # Load historical trace
    trace = load_trace(request_id)
    
    # Generate explanation
    engine = ExplanationEngine()
    explanation = engine.from_trace(trace)
    
    # Compliance report
    return {
        "request_id": request_id,
        "governance_decision": trace.result,
        "reasoning": explanation,
        "timestamp": trace.timestamp,
        "policy_version": trace.policy_version
    }
```

**Complete audit trail. No AI re-execution needed.**

## Related Resources

- [ape-openai package](../../packages/ape-openai/) - Official OpenAI integration
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Capability-Aware Design](../../docs/capabilities.md)

---

**Guarantees:** Deterministic governance, traceable decisions, replay-safe  
**Real-world use:** AI chatbots, content generation, code assistants  
**APE version:** v1.0.3  
**OpenAI SDK:** Compatible with openai>=1.0.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Governance** — Intent validation, allow/deny decisions  
✅ **Policy logic** — What operations are permitted  
✅ **Determinism** — Same intent always gets same validation result  
✅ **Audit trail** — Complete trace of every governance decision

**Your application handles:**
✅ **AI execution** — Calling openai.ChatCompletion.create()  
✅ **Intent extraction** — Parsing user requests to determine intent  
✅ **Response handling** — Processing OpenAI's output  
✅ **Integration** — Wrapping OpenAI SDK with APE governance

**APE never executes:**
❌ OpenAI API calls  
❌ Prompt construction  
❌ Token usage  
❌ Response parsing

**Why this matters:** APE validates intent deterministically *before* AI execution. Your app extracts intent, APE validates it, your app executes if allowed. This separation enables testing governance without API costs.
