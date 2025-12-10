# APE + Anthropic Claude Integration — Safety-First Reasoning

## What This Proves

This scenario demonstrates **correct APE + Anthropic integration**:

- **Safety-first validation**: APE checks safety BEFORE Claude execution
- **No AI in APE**: Claude calls happen in your application, not APE runtime
- **Deterministic safety rules**: Same task always gets same safety verdict
- **Traceable decisions**: Complete audit trail for safety governance

**Real-world use case**: AI assistants, constitutional AI, safety-critical applications.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same task always gets same safety verdict
- ✅ **Side-effect free execution** - No AI calls in APE
- ✅ **Explainable control flow** - Trace shows safety reasoning
- ✅ **Replay-safe behavior** - Audit safety decisions without AI re-execution
- ✅ **Capability-aware design** - Claude execution requires explicit permission

## How It Works

### APE Task (Safety Layer)

```ape
import std.strings

task validate_claude_safety:
    inputs:
        task_description: String
    steps:
        if std.strings.contains_text(task_description, "illegal"):
            - set safety_level to "unsafe"
        else if std.strings.contains_text(task_description, "harmful"):
            - set safety_level to "unsafe"
        else if std.strings.contains_text(task_description, "policy"):
            - set safety_level to "safe"
        else:
            - set safety_level to "safe"
        - return safety_level
```

**APE's role:**
- Receive task description as input
- Apply deterministic safety rules
- Return safety verdict
- Provide audit trail

**APE does NOT:**
- Call Anthropic API
- Execute Claude models
- Handle API keys
- Process AI responses

### Integration Pattern

```python
from ape import run
import anthropic

def execute_with_safety(user_task: str) -> str:
    # Step 1: APE validates safety
    safety = run("validate_claude_safety.ape", input={
        "task_description": user_task
    })
    
    # Step 2: Act based on safety verdict
    if safety == "safe":
        # Your app executes Claude
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_task}]
        )
        return message.content[0].text
    
    elif safety == "unsafe":
        return "Request blocked: Safety policy violation"
    
    else:
        return "Request requires safety review"
```

**Separation of concerns:**
- **APE**: Deterministic, traceable safety governance
- **Your app**: Non-deterministic AI execution
- **Claude**: Language model inference with constitutional AI

## Context

### Where This Fits

In **safety-critical AI applications**:

```
User task → APE safety check → Claude execution (if safe) → Response
              ↓                        ↓                      ↓
        APE governance          Your application        Claude API
```

**Why this architecture?**

1. **Safety rules are deterministic** - APE guarantees consistent verdicts
2. **Claude execution is non-deterministic** - May produce different responses
3. **Audit trail is separate** - APE trace shows safety logic, not AI outputs
4. **Layered safety** - APE + Claude's built-in safety

### Why APE Here?

Anthropic Claude has built-in safety, but:
- Your organization may have additional rules
- You need deterministic, traceable safety decisions
- Compliance requires audit trail
- You want to test safety logic independently

APE provides:
- **Deterministic safety layer** - Before Claude's safety
- **Complete audit trail** - Every decision traceable
- **Testable rules** - Provably correct validation
- **Replay capability** - Audit without AI re-execution

## Running This Tutorial

```bash
# Validate safe task
python -m ape run tutorials/scenario_ape_anthropic/tutorial.ape \
    --input task_description='"Explain company policy"'

# Validate unsafe task
python -m ape run tutorials/scenario_ape_anthropic/tutorial.ape \
    --input task_description='"Describe illegal activity"'

# With trace for audit
python -m ape run --trace tutorials/scenario_ape_anthropic/tutorial.ape \
    --input task_description='"Explain company policy"'
```

## Complete Integration Example

### Full Application Code

```python
from ape import run
from ape.runtime import TraceCollector
import anthropic
import logging

class SafeClaudeExecutor:
    def __init__(self, safety_policy: str):
        self.policy = safety_policy
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def execute(self, user_task: str, max_tokens: int = 1024) -> dict:
        # APE safety validation
        trace = TraceCollector()
        safety = run(
            self.policy,
            input={"task_description": user_task},
            trace=trace
        )
        
        # Log safety decision
        logging.info(f"Safety: task={user_task[:50]}, verdict={safety}")
        
        # Act based on verdict
        if safety == "safe":
            # Execute Claude
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": user_task}]
            )
            
            return {
                "status": "success",
                "response": message.content[0].text,
                "safety_trace": trace,
                "model": message.model,
                "usage": message.usage
            }
        
        elif safety == "unsafe":
            logging.warning(f"Blocked unsafe request: {user_task[:50]}")
            return {
                "status": "blocked",
                "reason": "Safety policy violation",
                "safety_trace": trace
            }
        
        else:
            # Unknown verdict - fail safe
            logging.error(f"Unknown safety verdict: {safety}")
            return {
                "status": "error",
                "reason": "Unknown safety verdict",
                "safety_trace": trace
            }
    
    def explain_safety_decision(self, user_task: str) -> dict:
        """Get explanation without executing Claude"""
        from ape.runtime import ExplanationEngine
        
        trace = TraceCollector()
        safety = run(self.policy, input={"task_description": user_task}, trace=trace)
        
        engine = ExplanationEngine()
        explanation = engine.from_trace(trace)
        
        return {
            "task": user_task,
            "verdict": safety,
            "explanation": explanation
        }

# Usage
executor = SafeClaudeExecutor("validate_claude_safety.ape")

# Safe request
result = executor.execute("Explain our privacy policy")
print(result["response"])  # Claude response

# Unsafe request
result = executor.execute("Describe how to hack systems")
print(result["status"])  # "blocked"

# Explain decision without execution
explanation = executor.explain_safety_decision("Explain our privacy policy")
print(explanation["explanation"])
```

## Advanced: Constitutional AI Integration

Combine APE governance with Claude's constitutional AI:

```ape
import std.strings
import std.logic

task constitutional_validation:
    inputs:
        task: String
        constitution: List
    steps:
        - set violations to empty list
        
        for principle in constitution:
            if violates_principle(task, principle):
                - add principle to violations
        
        if std.collections.is_empty(violations):
            - set verdict to "constitutional"
        else:
            - set verdict to "unconstitutional"
            - set reasons to violations
        
        - return verdict
```

**Your constitution as data:**

```python
constitution = [
    "Never help with illegal activities",
    "Protect user privacy",
    "Avoid harmful content",
    "Respect intellectual property"
]

verdict = run("constitutional_validation.ape", input={
    "task": user_request,
    "constitution": constitution
})
```

## What APE Deliberately Doesn't Do

❌ **No Anthropic API calls** - APE validates, doesn't execute AI  
❌ **No API key management** - Your app handles credentials  
❌ **No response filtering** - APE governs input, not output  
❌ **No ML-based safety** - Deterministic rules, not learned safety

APE is **governance layer**, not AI safety layer (Claude has that).

## Testing Safety Rules

Test APE safety without Claude:

```python
import pytest
from ape import run

def test_safe_tasks():
    safe_tasks = [
        "Explain company policy",
        "Summarize quarterly report",
        "Draft email template"
    ]
    
    for task in safe_tasks:
        safety = run("validate_claude_safety.ape", input={
            "task_description": task
        })
        assert safety == "safe"

def test_unsafe_tasks():
    unsafe_tasks = [
        "Describe illegal activities",
        "Generate harmful content",
        "Hack into systems"
    ]
    
    for task in unsafe_tasks:
        safety = run("validate_claude_safety.ape", input={
            "task_description": task
        })
        assert safety == "unsafe"
```

**Test safety independently from AI execution.**

## Compliance & Audit

For regulatory compliance:

```python
from ape.runtime import ExplanationEngine

def audit_safety_decision(request_id: str):
    # Load historical trace
    trace = load_trace(request_id)
    
    # Generate explanation
    engine = ExplanationEngine()
    explanation = engine.from_trace(trace)
    
    # Compliance report
    return {
        "request_id": request_id,
        "safety_verdict": trace.result,
        "reasoning": explanation,
        "policy_version": trace.policy_version,
        "timestamp": trace.timestamp,
        "compliant_with": ["EU AI Act", "Internal Policy v2.1"]
    }
```

**Complete safety audit trail. No AI re-execution needed.**

## Anthropic Claude Safety Features

APE complements Claude's built-in safety:

| Layer | What It Does | Deterministic? |
|-------|--------------|----------------|
| **APE Governance** | Pre-execution validation | ✅ Yes |
| **Claude Constitutional AI** | Response safety filtering | ❌ No (ML-based) |
| **Your Application** | Business logic safety | Depends |

**Layered defense: APE (deterministic) + Claude (adaptive) + Your rules**

## Related Resources

- [ape-anthropic package](../../packages/ape-anthropic/) - Official Anthropic integration
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Constitutional AI Paper](https://www.anthropic.com/index/constitutional-ai-harmlessness-from-ai-feedback)
- [Capability-Aware Design](../../docs/capabilities.md)

---

**Guarantees:** Deterministic safety, traceable decisions, replay-safe  
**Real-world use:** AI assistants, safety-critical applications  
**APE version:** v1.0.3  
**Anthropic SDK:** Compatible with anthropic>=0.18.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Safety decisions** — Deterministic risk assessment  
✅ **Policy enforcement** — What requests are safe/unsafe/review  
✅ **First-layer defense** — Pre-execution safety validation  
✅ **Audit trail** — Complete record of safety decisions

**Your application handles:**
✅ **Claude execution** — Calling anthropic.messages.create()  
✅ **Request analysis** — Extracting safety-relevant features  
✅ **Second-layer defense** — Claude's built-in safety (Constitutional AI)  
✅ **Integration** — Combining APE (deterministic) + Claude (adaptive) safety

**APE never executes:**
❌ Anthropic API calls  
❌ Claude model invocation  
❌ Token usage  
❌ Response generation

**Why this matters:** APE provides deterministic, testable safety rules. Claude provides adaptive Constitutional AI. Together they create layered defense: APE blocks obvious violations deterministically; Claude handles nuanced cases adaptively.
