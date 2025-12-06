# Dry-Run Auditing — Deciding Without Executing

## What This Proves

This scenario demonstrates APE's **dry-run mode** for safe analysis:

- **Analyze without executing**: Validate logic without side effects
- **Test in production**: Run against real data safely
- **Audit trail without risk**: See what would happen, without actually doing it
- **Capability isolation**: Ensure no mutations possible

**Real-world use case**: Testing new policies in production, compliance audits, what-if analysis.

## Guarantees Demonstrated

- ✅ **Deterministic execution** - Same inputs, same analysis
- ✅ **Side-effect free execution** - Guaranteed no mutations in dry-run
- ✅ **Explainable control flow** - Full trace of hypothetical execution
- ✅ **Replay-safe behavior** - Audit without affecting state
- ✅ **Capability-aware design** - No permissions needed for dry-run

## How It Works

```ape
task calculate_total:
    inputs:
        values: List
    steps:
        - set total to 0
        for value in values:
            if value > 15:
                - set total to total plus value
        - return total
```

**Normal mode:**
- Executes all steps
- Can mutate context
- Returns final result

**Dry-run mode:**
- Executes logic flow
- **Blocks all mutations**
- Returns what *would* happen
- Produces full trace

**Input example:** `[10, 20, 30]`  
**Normal result:** `50` (20 + 30)  
**Dry-run result:** Same `50`, but with guarantee that nothing was mutated

## Context

### Where This Fits

In systems requiring **safe production testing**:

```
New policy → Dry-run against real data → Verify results → Deploy
```

**Use cases:**

1. **Policy testing**: Test new decision rules against historical data
2. **Compliance audits**: Show what system would do without doing it
3. **What-if analysis**: Explore scenarios without committing
4. **Shadow deployments**: Run new logic alongside old, compare results

### Why APE Here?

Traditional testing approaches:
- Require test environments (not real data)
- Risk of side effects in production
- No built-in isolation guarantees
- Manual validation needed

APE provides:
- **Built-in dry-run mode** - Language-level guarantee
- **Runtime enforcement** - Mutations blocked automatically
- **Full trace capture** - See exactly what would happen
- **Production-safe** - Run against real data with zero risk

## Running This Tutorial

```bash
# Normal execution (with mutations allowed)
python -m ape run tutorials/scenario_dry_run_auditing/tutorial.ape \
    --input values='[10, 20, 30]'

# Dry-run mode (mutations blocked)
python -m ape run --dry-run tutorials/scenario_dry_run_auditing/tutorial.ape \
    --input values='[10, 20, 30]'

# With trace to see execution path
python -m ape run --dry-run --trace tutorials/scenario_dry_run_auditing/tutorial.ape
```

**Both modes produce same result. Dry-run guarantees no side effects.**

## Integration Pattern

### Testing New Policy in Production

```python
from ape import run
from ape.runtime import TraceCollector

# Current policy
old_policy = load_policy("current.ape")

# New policy (testing)
new_policy = load_policy("proposed.ape")

# Run both against real production data
for transaction in production_data:
    # Old policy executes normally
    old_result = run(old_policy, input=transaction)
    
    # NEW policy runs in dry-run (safe!)
    trace = TraceCollector()
    new_result = run(new_policy, input=transaction, dry_run=True, trace=trace)
    
    # Compare results
    if old_result != new_result:
        log_difference(transaction, old_result, new_result, trace)

# After validation, deploy new policy
deploy_policy("proposed.ape")
```

**Zero risk. Full production data. Complete validation.**

### Compliance Audit

Auditor asks: "What would happen if we applied this rule to last month's data?"

```python
from ape import run

# Load historical data
transactions = load_transactions(month="2024-11")

# Run proposed rule in dry-run
results = []
for tx in transactions:
    result = run("audit_rule.ape", input=tx, dry_run=True)
    results.append((tx, result))

# Generate audit report
generate_report(results)  # Safe - nothing was mutated
```

## Dry-Run Guarantees

### What's Blocked in Dry-Run Mode

❌ Context mutations (`context.set()` fails)  
❌ File I/O (if capability-gated)  
❌ Database writes (if capability-gated)  
❌ Network calls (if capability-gated)

### What Still Works

✅ Reading inputs  
✅ Control flow (if, for, while)  
✅ Expressions and calculations  
✅ Trace recording  
✅ Return values

**Dry-run mode = "read-only execution"**

## Advanced: Shadow Deployment

Run new and old logic side-by-side:

```python
from ape import run
from ape.runtime import TraceCollector

def shadow_deploy(new_policy_file, input_data):
    # Old policy (production)
    old_result = run("current_policy.ape", input=input_data)
    
    # New policy (shadow, dry-run)
    new_trace = TraceCollector()
    new_result = run(new_policy_file, input=input_data, 
                     dry_run=True, trace=new_trace)
    
    # Compare and log
    if old_result != new_result:
        alert_deviation(input_data, old_result, new_result, new_trace)
    
    # Return production result
    return old_result

# Use in production safely
result = shadow_deploy("new_policy.ape", user_request)
```

**Users see old results. You validate new logic. Zero risk.**

## What APE Deliberately Doesn't Do

❌ **No partial dry-run** - All or nothing isolation  
❌ **No simulation** - Real logic, just blocked mutations  
❌ **No mocking** - Actual execution, not fake  
❌ **No rollback** - Mutations prevented, not reverted

Dry-run is **prevention**, not simulation.

## Testing Your Own Tasks

Any APE task can run in dry-run mode:

```bash
# Your custom task
ape run --dry-run your_task.ape --input data.json
```

**If it runs in dry-run, it's side-effect free.**

If dry-run fails, your task has side effects that need capability gates.

---

**Guarantees:** Deterministic, mutation-free, traceable, production-safe  
**Real-world use:** Policy testing, compliance audits, shadow deployments  
**APE version:** v1.0.0

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Analysis** — Calculating what would happen without doing it  
✅ **Decisions** — Filtering, accumulation, threshold logic  
✅ **Safety** — Guaranteed no mutations in dry-run mode  
✅ **Preview** — See results before committing to execution

**Your application handles:**
✅ **Data access** — Fetching values to analyze  
✅ **Actual execution** — Running actions after dry-run validation  
✅ **Comparison** — Old policy vs new policy analysis  
✅ **Deployment** — Promoting policies after safe testing

**APE never executes:**
❌ Data mutations (even in normal mode)  
❌ Side effects  
❌ External API calls  
❌ Database writes

**Why this matters:** Dry-run mode lets you test new policies against production data safely. APE analyzes; your application controls when to execute approved changes.
