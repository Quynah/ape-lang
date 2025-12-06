# Explainable Decisions — Traceable Control Flow

## What This Proves

This scenario demonstrates APE's **built-in explainability**:

- **Observable execution**: Every decision point captured in trace
- **Human-readable explanations**: Trace converts to natural language
- **No manual logging**: Tracing is automatic and complete
- **Audit compliance**: Full decision trail for regulatory requirements

**Real-world use case**: Credit scoring, loan approval, compliance decisions, medical recommendations.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same score always gets same rating
- ✅ **Side-effect free execution** - No mutations, no I/O
- ✅ **Explainable control flow** - Every decision path traceable
- ✅ **Replay-safe behavior** - Can explain decision months later
- ✅ **Capability-aware design** - No hidden dependencies

## How It Works

```ape
task rate_score:
    inputs:
        score: Integer
    steps:
        if score >= 80:
            - set rating to "high"
        else if score >= 50:
            - set rating to "medium"
        else:
            - set rating to "low"
        - return rating
```

**Logic:**
1. Evaluate score against thresholds
2. Assign rating based on range
3. Return rating with full trace

**Decision table:**

| Score | Rating | Explanation |
|-------|--------|-------------|
| 85 | `"high"` | Condition `score >= 80` evaluated to true |
| 72 | `"medium"` | First condition false, `score >= 50` true |
| 30 | `"low"` | Both conditions false, else branch taken |

## Context

### Where This Fits

In systems requiring **explainable AI/decisions**:

```
Input → APE task → Decision + Trace → Explanation
```

**APE provides:**
1. Deterministic decision logic
2. Complete execution trace
3. Human-readable explanation via `ExplanationEngine`
4. Replay capability for audits

**Your application uses:**
- Decision result for business logic
- Trace for compliance logging
- Explanation for user feedback
- Replay for dispute resolution

### Why APE Here?

Traditional decision logic suffers from:
- Manual logging (incomplete, inconsistent)
- No automatic trace capture
- Hard to explain after the fact
- Can't replay historical decisions

APE provides:
- **Automatic tracing** - Every execution fully captured
- **Explanation engine** - Trace → human-readable narrative
- **Replay validation** - Re-verify decisions without re-execution
- **Audit compliance** - Complete decision trail

## Running This Tutorial

```bash
# Basic execution
python -m ape run tutorials/scenario_explainable_decisions/tutorial.ape \
    --input score=72

# With trace capture
python -m ape run --trace tutorials/scenario_explainable_decisions/tutorial.ape \
    --input score=72

# Generate explanation
python -m ape explain tutorials/scenario_explainable_decisions/tutorial.ape \
    --input score=72
```

## Explanation Output

For `score=72`, the explanation engine produces:

```
Step 1: Evaluating condition: score >= 80
  - Result: false (72 is not >= 80)
  
Step 2: Evaluating condition: score >= 50
  - Result: true (72 >= 50)
  
Step 3: Executing then-branch
  - Setting rating to "medium"
  
Step 4: Returning rating
  - Value: "medium"
```

**All automatic. No manual logging.**

## Integration Pattern

### Using Trace for Compliance

```python
from ape import run
from ape.runtime import TraceCollector, ExplanationEngine

# Execute with tracing
trace = TraceCollector()
rating = run("rate_score.ape", input={"score": 72}, trace=trace)

# Generate explanation
engine = ExplanationEngine()
explanation = engine.from_trace(trace)

# Log for compliance
log_decision(
    result=rating,
    explanation=explanation,
    timestamp=now(),
    user=current_user()
)
```

### Replay for Audit

Months later, when auditor asks "Why was this rated medium?":

```python
from ape.runtime import ReplayEngine

# Load historical trace
trace = load_trace_from_database(decision_id)

# Validate trace integrity
replay = ReplayEngine()
validation = replay.replay(trace)

if validation.valid:
    # Generate explanation from historical trace
    explanation = ExplanationEngine().from_trace(trace)
    show_to_auditor(explanation)
```

**No re-execution needed. Trace is sufficient.**

## Advanced: Multi-Factor Decisions

Extend with multiple inputs:

```ape
task comprehensive_rating:
    inputs:
        score: Integer
        history: String
        risk_level: String
    steps:
        if score >= 80 and history == "good" and risk_level == "low":
            - set rating to "excellent"
        else if score >= 50:
            - set rating to "medium"
        else:
            - set rating to "poor"
        - return rating
```

**Every condition traced. Every decision explainable.**

## What APE Deliberately Doesn't Do

❌ **No machine learning** - Deterministic rules, not ML models  
❌ **No probability scores** - Discrete decisions, not uncertainties  
❌ **No external data fetching** - Your app provides all inputs  
❌ **No real-time learning** - Rules are fixed, not adaptive

APE is **explainable by design**, not explainable AI (XAI).

## Regulatory Compliance

This pattern helps with:

- **GDPR Article 22** - Right to explanation for automated decisions
- **EU AI Act** - High-risk AI system transparency requirements
- **Financial regulations** - Audit trail for lending/credit decisions
- **Medical device regulations** - Traceable clinical decision support

**APE provides the audit trail. Your app provides the domain logic.**

---

**Guarantees:** Deterministic, traceable, explainable, replay-safe  
**Real-world use:** Credit scoring, compliance, medical decisions  
**APE version:** v1.0.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Decisions** — Content rating, threshold classification, policy logic  
✅ **Observability** — Full trace of every decision step  
✅ **Explanation** — Human-readable reasoning for each outcome  
✅ **Determinism** — Replay-safe, audit-ready decision trail

**Your application handles:**
✅ **Data access** — Fetching content scores, user context  
✅ **Actions** — Acting on APE's rating decision  
✅ **Storage** — Saving decisions and traces for compliance  
✅ **Reporting** — Formatting APE traces for auditors

**APE never executes:**
❌ Database queries  
❌ Content moderation actions  
❌ User notifications  
❌ External service calls

**Why this matters:** APE provides the auditable decision logic required for compliance (GDPR Article 22, EU AI Act transparency). Your application handles data and execution.
