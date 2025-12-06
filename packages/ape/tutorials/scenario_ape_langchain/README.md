# Scenario: APE + LangChain Integration

**What This Proves:**  
APE can govern LangChain chain execution by validating chain steps before they run. This demonstrates control over multi-step AI workflows.

## Guarantees Demonstrated

✅ **Step Validation**: Only approved chain steps execute  
✅ **Audit Trail**: Every chain decision is traceable  
✅ **Deterministic Governance**: Same steps → same validation  
✅ **No Side Effects**: Validation never mutates data  
✅ **Explainable**: Why each step was allowed/blocked

---

## How It Works

```ape
import std.collections

task filter_chain_steps:
    inputs:
        proposed_steps: List
    steps:
        - set safe_steps to empty list
        for step in proposed_steps:
            if step != "execute":
                - add step to safe_steps
        - return safe_steps
```

**Logic:**
1. **Input**: List of proposed LangChain steps
2. **Filter**: Block "execute" step (code execution)
3. **Return**: Only safe steps (classify, summarize, etc.)

**Result:**  
```python
["classify", "summarize"]  # "execute" was blocked
```

---

## Context: Why APE for LangChain Governance?

**Problem:**  
LangChain chains can include arbitrary steps. You need to control which steps run in production.

**APE Solution:**  
- Validate chain steps **before** execution
- Block dangerous operations (code execution, data mutation)
- Maintain audit trail of governance decisions

**Without APE:**  
```python
# ❌ WRONG: No governance over chain steps
chain = load_chain_from_config(config)
result = chain.run(input)  # What steps just ran?
```

**With APE:**  
```python
# ✅ CORRECT: Validate steps first
from ape import run
from langchain.chains import SequentialChain

class GovernedChainExecutor:
    def __init__(self, policy_path: str):
        self.policy = load_ape(policy_path)
    
    def execute_chain(self, proposed_steps: list, input_data: dict) -> dict:
        # APE validation
        trace = TraceCollector()
        safe_steps = run(
            self.policy,
            input={"proposed_steps": proposed_steps},
            trace=trace
        )
        
        if len(safe_steps) == 0:
            return {
                "status": "blocked",
                "reason": "All steps rejected by policy"
            }
        
        # Build chain with only safe steps
        chain = SequentialChain(chains=[
            self._step_to_chain(step) for step in safe_steps
        ])
        
        result = chain.run(input_data)
        
        return {
            "status": "success",
            "result": result,
            "governance_trace": trace,
            "approved_steps": safe_steps,
            "blocked_steps": list(set(proposed_steps) - set(safe_steps))
        }
    
    def _step_to_chain(self, step: str):
        # Convert step name to LangChain component
        pass
```

**Key Insights:**
1. **APE validates** → App executes chain (separation)
2. **Deterministic governance** → Same steps always validated the same way
3. **No LangChain dependency in APE** → Policy is framework-agnostic
4. **Audit trail preserved** → Compliance reporting is trivial

---

## Integration Pattern

```python
# production_system.py
from ape import load_ape
from langchain.chains import LLMChain, SequentialChain
from langchain.llms import OpenAI

class ProductionChainSystem:
    def __init__(self):
        self.policy = load_ape("tutorial.ape")
        self.llm = OpenAI()
    
    def execute_user_request(self, user_config: dict) -> dict:
        proposed = user_config["steps"]  # ["classify", "summarize", "execute"]
        
        # APE governance
        safe = run(self.policy, input={"proposed_steps": proposed})
        
        # Build chain with only approved steps
        chains = []
        for step in safe:
            if step == "classify":
                chains.append(LLMChain(llm=self.llm, prompt=self.classify_prompt))
            elif step == "summarize":
                chains.append(LLMChain(llm=self.llm, prompt=self.summarize_prompt))
            # "execute" is not in safe, so it's skipped
        
        chain = SequentialChain(chains=chains)
        result = chain.run(user_config["input"])
        
        return {
            "result": result,
            "approved_steps": safe,
            "blocked_steps": list(set(proposed) - set(safe))
        }
```

**Why This Matters:**
- **Agents**: Govern autonomous agent chains
- **Workflows**: Control multi-step LLM pipelines
- **Compliance**: Audit which operations were allowed

---

## Testing Without LangChain

```python
# test_chain_governance.py
from ape import run

def test_blocks_execute_step():
    policy = load_ape("tutorial.ape")
    
    result = run(
        policy,
        input={"proposed_steps": ["classify", "execute", "summarize"]}
    )
    
    assert result == ["classify", "summarize"]
    assert "execute" not in result

def test_allows_safe_steps():
    policy = load_ape("tutorial.ape")
    
    result = run(
        policy,
        input={"proposed_steps": ["classify", "summarize"]}
    )
    
    assert len(result) == 2
```

**No LangChain required** → Test governance independently.

---

## Dynamic Chain Policies

```python
# Advanced: Policy as input
class AdaptiveChainGovernor:
    def __init__(self, policy_path: str):
        self.base_policy = load_ape(policy_path)
    
    def execute_with_context(self, steps: list, context: dict) -> dict:
        # Augment policy with runtime context
        if context.get("user_role") == "admin":
            # Admin gets different step allowance
            extended_policy = load_ape("admin_policy.ape")
            safe = run(extended_policy, input={"proposed_steps": steps})
        else:
            safe = run(self.base_policy, input={"proposed_steps": steps})
        
        # Execute chain with governed steps
        # ...
```

**Pattern**: Different policies for different user roles/contexts.

---

## What APE Deliberately Doesn't Do

❌ **Execute LangChain**: APE validates, your app runs the chain  
❌ **Parse Chain Configs**: APE receives structured step lists  
❌ **Manage LangChain State**: APE is stateless, app handles chain memory  
❌ **Dynamic Chain Building**: APE validates steps, app constructs the chain

**Why:**  
APE is a governance engine, not a workflow engine. It decides what's allowed; your application decides how to execute it.

---

## Compliance and Audit

```python
# compliance_reporter.py
from ape import run, TraceCollector

def audit_chain_execution(log_entries: list) -> dict:
    blocked_count = 0
    allowed_count = 0
    
    for entry in log_entries:
        trace = TraceCollector()
        safe = run(policy, input={"proposed_steps": entry["steps"]}, trace=trace)
        
        blocked = set(entry["steps"]) - set(safe)
        
        if blocked:
            blocked_count += len(blocked)
            print(f"Blocked: {blocked} (reason: {trace.explain()})")
        
        allowed_count += len(safe)
    
    return {
        "total_steps_requested": blocked_count + allowed_count,
        "allowed": allowed_count,
        "blocked": blocked_count,
        "compliance_rate": allowed_count / (blocked_count + allowed_count)
    }
```

**Result:**  
- Every chain execution is auditable
- Policy changes are traceable
- Compliance reporting is deterministic

---

## 🔒 What Runs in APE vs Your Application

**APE handles:**
✅ **Step validation** — Which chain steps are allowed  
✅ **Governance decisions** — Allow/block/review for each operation  
✅ **Determinism** — Same proposed steps always get same validation  
✅ **Audit trail** — Record of what was approved/blocked and why

**Your application handles:**
✅ **Chain execution** — Running LangChain with approved steps  
✅ **Step extraction** — Determining what steps a chain would execute  
✅ **Chain construction** — Building SequentialChain with safe steps  
✅ **Integration** — Wrapping LangChain with APE governance layer

**APE never executes:**
❌ LangChain chains  
❌ LLM calls within chains  
❌ Tool execution  
❌ Agent actions

**Why this matters:** LangChain chains can include arbitrary steps (including code execution). APE validates the chain composition before execution, enabling governance over autonomous agent behavior.

---

## Related

- **OpenAI Scenario**: Intent validation before API calls
- **Anthropic Scenario**: Safety-first reasoning
- **Dry-Run Scenario**: Analyze chains without executing them

---

## Run This Tutorial

```bash
cd packages/ape
python -m ape.cli.run tutorials/scenario_ape_langchain/tutorial.ape \
  --input '{"proposed_steps": ["classify", "summarize", "execute"]}'
```

**Expected Output:**  
```json
["classify", "summarize"]
```

**Validation:**  
```bash
pytest tests/tutorials/test_tutorials_execute.py::test_tutorial_executes_without_error[scenario_ape_langchain]
```
