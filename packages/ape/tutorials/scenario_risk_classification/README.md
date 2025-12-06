# Risk Classification — Complex Control Flow

## What This Proves

This scenario demonstrates APE's ability to handle **complex governance logic** with:

- **Data filtering**: Iterate over collections with control flow
- **Multi-condition logic**: Combine boolean operators (`not`, `and`)
- **Deterministic decisions**: Same input always produces same classification
- **Audit trail**: Every decision point is traceable

**Real-world use case**: Access control systems, compliance checks, risk scoring in financial services.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same users always classified identically
- ✅ **Side-effect free execution** - No database mutations, no I/O
- ✅ **Explainable control flow** - Trace shows exactly why each user was flagged
- ✅ **Replay-safe behavior** - Decision can be replayed for audit
- ✅ **Capability-aware design** - No implicit permissions needed

## How It Works

```ape
task classify_high_risk_users:
    inputs:
        users: List
    steps:
        - set high_risk to empty list
        for user in users:
            if not user active and user is admin:
                - add user name to high_risk list
        - return high_risk
```

**Logic:**
1. Start with empty high-risk list
2. For each user:
   - Check if user is NOT active
   - AND check if user IS admin
   - If both true → add to high-risk list
3. Return classified list

**Input example:**
```python
users = [
    {"name": "alice", "active": False, "admin": True},   # HIGH RISK
    {"name": "bob", "active": True, "admin": False},     # Safe
    {"name": "carol", "active": False, "admin": False}   # Safe
]
```

**Output:** `["alice"]`

## Context

### Where This Fits

In a real system, this APE task would:

1. Receive user data from your application
2. Execute classification logic deterministically
3. Return results for your system to act on
4. Provide complete audit trail via trace

**APE does not:**
- Query databases (your app provides data)
- Send notifications (your app handles actions)
- Make external API calls (capability separation)

### Why APE Here?

Traditional code would require:
- Manual audit logging
- Risk of non-determinism (timestamps, random)
- No built-in replay capability
- Complex testing for all conditions

APE provides:
- **Automatic tracing** - Every decision recorded
- **Guaranteed determinism** - No hidden state
- **Replay validation** - Audit without re-execution
- **Natural language steps** - Business logic readable

## Running This Tutorial

```bash
# Validate syntax
ape validate tutorials/scenario_risk_classification/tutorial.ape

# Execute (provide users as input)
python -m ape run tutorials/scenario_risk_classification/tutorial.ape \
    --input users='[{"name":"alice","active":false,"admin":true}]'

# With full trace
python -m ape run --trace tutorials/scenario_risk_classification/tutorial.ape
```

## What APE Deliberately Doesn't Do

❌ **No database access** - Your app provides data  
❌ **No notifications** - Your app handles actions  
❌ **No AI calls** - Classification is deterministic logic  
❌ **No randomness** - Guaranteed reproducibility

APE is the **decision engine**, not the full application.

---

**Guarantees:** Deterministic, traceable, replay-safe, side-effect free  
**Real-world use:** Access control, compliance, risk scoring  
**APE version:** v1.0.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Decisions** — Risk classification, policy evaluation, governance rules  
✅ **Logic** — Control flow, conditions, score calculations  
✅ **Determinism** — Same inputs always produce same outputs  
✅ **Traceability** — Every decision step is recorded

**Your application handles:**
✅ **Data access** — Fetching user records, database queries  
✅ **API calls** — External services, third-party integrations  
✅ **Side effects** — Writing to database, sending notifications  
✅ **AI execution** — Calling OpenAI/Anthropic/LangChain

**APE never executes:**
❌ Database mutations  
❌ API calls to external services  
❌ File system operations  
❌ Network requests

**Why this matters:** APE is a governance & decision layer. Your application orchestrates data and execution; APE provides deterministic, auditable decisions about what should happen.
