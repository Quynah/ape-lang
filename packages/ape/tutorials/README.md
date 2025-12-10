# APE Tutorials — Scenario-Based, Evidence-Driven

## What Are These Tutorials?

These tutorials are **scenario-driven demonstrations** of APE v1.0.3 capabilities. Each tutorial:

- **Proves, not promises**: Every scenario runs today with existing features
- **Stands alone**: No sequence, no prerequisites, no learning path
- **Demonstrates multiple guarantees**: Each scenario combines control flow, stdlib, observability, and safety
- **APE-first**: `.ape` files are the primary artifacts, not documentation

**This is not a course**. Pick any scenario relevant to your use case and see APE in action.

## Why No Sequence?

APE scenarios are **independent proofs** of capability. You don't need to complete "Tutorial 1" before understanding "Tutorial 5". Each scenario demonstrates:

- A realistic problem
- How APE solves it
- Which guarantees apply
- What APE deliberately doesn't do

**Start anywhere. Learn by evidence.**

## Scenario Index

### Governance & Safety

- **[scenario_risk_classification/](scenario_risk_classification/)** - Complex control flow with data filtering
- **[scenario_ai_input_governance/](scenario_ai_input_governance/)** - Safe AI input validation before execution
- **[scenario_dry_run_auditing/](scenario_dry_run_auditing/)** - Deciding without mutating state

### Observability

- **[scenario_explainable_decisions/](scenario_explainable_decisions/)** - Traceable, explainable control flow

### Multi-Language

- **[scenario_multilanguage_team/](scenario_multilanguage_team/)** - Same semantics in English and Dutch

### AI Integration Patterns

- **[scenario_ape_openai/](scenario_ape_openai/)** - OpenAI integration with intent separation
- **[scenario_ape_anthropic/](scenario_ape_anthropic/)** - Anthropic Claude with safety-first reasoning
- **[scenario_ape_langchain/](scenario_ape_langchain/)** - LangChain governance over chains

## What Every Scenario Demonstrates

Each tutorial combines multiple APE guarantees:

✅ **Deterministic execution**: Same input → same output  
✅ **Side-effect free**: No implicit mutations or I/O  
✅ **Explainable**: Every decision traceable  
✅ **Replay-safe**: Full audit trail  
✅ **Capability-aware**: Explicit permission model

## Running Tutorials

All tutorials are executable APE programs:

```bash
# Parse and validate
ape validate tutorials/scenario_risk_classification/tutorial.ape

# Execute with runtime
python -m ape run tutorials/scenario_risk_classification/tutorial.ape

# With tracing
python -m ape run --trace tutorials/scenario_risk_classification/tutorial.ape

# In dry-run mode (no mutations)
python -m ape run --dry-run tutorials/scenario_dry_run_auditing/tutorial.ape
```

## Tutorial Structure

Each scenario directory contains:

- **`tutorial.ape`** - Complete, runnable APE code
- **`README.md`** - What this proves, guarantees demonstrated, context

**No Python code**. APE is the tutorial.

## For AI Integration Developers

The `scenario_ape_*` tutorials show **correct patterns** for integrating OpenAI, Anthropic, and LangChain:

- APE defines **intent and governance**, not AI calls
- AI execution happens **outside APE runtime**
- No "magic" - explicit, traceable integration

See each scenario's README for details.

## Verification

All tutorials are tested for executability:

```bash
pytest tests/tutorials/test_tutorials_execute.py -v
```

Expected output is verified via `# EXPECT:` comments in tutorial files.

## Philosophy

APE tutorials are **evidence-based proofs**, not step-by-step guides. We show:

- What works today
- Why it's safe
- What guarantees hold
- What APE deliberately doesn't do

**No promises. Just proof.**

---

**Version:** APE v1.0.3  
**Last Updated:** December 2025  
**Status:** All tutorials executable and tested
