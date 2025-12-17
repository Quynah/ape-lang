"""
Tests for APE Decision Engine Components

Policy Engine, Rule Engine, Decision Tables, and Constraint Validation.

Author: David Van Aelst
Status: Decision Engine v2024 - Complete
"""

import pytest
from ape.runtime.policy_engine import PolicyEngine, PolicyAction, PolicyRule, PolicyDecision
from ape.runtime.rule_engine import RuleEngine, RuleMode, WhenThenRule, RuleResult
from ape.runtime.decision_table import DecisionTable, HitPolicy, DecisionTableResult
from ape.runtime.constraint_checker import ConstraintChecker, ConstraintType, ValidationResult


# ============================================================================
# Policy Engine Tests
# ============================================================================

def test_policy_engine_basic_allow():
    """Test basic allow policy"""
    engine = PolicyEngine()
    engine.add_policy("basic_allow", "user.verified == True", PolicyAction.ALLOW)
    
    context = {"user": {"verified": True}}
    decision = engine.evaluate(context)
    
    assert decision.action == PolicyAction.ALLOW
    assert decision.allowed == True
    assert "basic_allow" in decision.matched_rules


def test_policy_engine_basic_deny():
    """Test basic deny policy"""
    engine = PolicyEngine()
    engine.add_policy("deny_minor", "age < 18", PolicyAction.DENY)
    
    context = {"age": 16}
    decision = engine.evaluate(context)
    
    assert decision.action == PolicyAction.DENY
    assert decision.allowed == False


def test_policy_engine_priority():
    """Test priority-based conflict resolution"""
    engine = PolicyEngine()
    engine.add_policy("high_value_gate", "amount > 10000", PolicyAction.GATE, priority=10)
    engine.add_policy("basic_allow", "amount > 0", PolicyAction.ALLOW, priority=1)
    
    context = {"amount": 15000}
    decision = engine.evaluate(context)
    
    # Higher priority (GATE) should win
    assert decision.action == PolicyAction.GATE
    assert decision.requires_gate == True
    assert len(decision.matched_rules) == 2


def test_policy_engine_no_match_default_allow():
    """Test default allow when no policies match"""
    engine = PolicyEngine()
    engine.add_policy("specific", "category == 'special'", PolicyAction.DENY)
    
    context = {"category": "normal"}
    decision = engine.evaluate(context)
    
    assert decision.action == PolicyAction.ALLOW
    assert decision.allowed == True


def test_policy_engine_escalation():
    """Test escalation action"""
    engine = PolicyEngine()
    engine.add_policy("escalate_large", "amount > 50000", PolicyAction.ESCALATE, priority=10)
    
    context = {"amount": 75000}
    decision = engine.evaluate(context)
    
    assert decision.action == PolicyAction.ESCALATE
    assert decision.requires_escalation == True


def test_policy_engine_disabled():
    """Test disabled policy engine"""
    engine = PolicyEngine()
    engine.add_policy("deny_all", "True", PolicyAction.DENY)
    engine.disable()
    
    context = {}
    decision = engine.evaluate(context)
    
    assert decision.allowed == True  # Disabled = default allow


def test_policy_engine_remove_policy():
    """Test removing a policy"""
    engine = PolicyEngine()
    engine.add_policy("temp", "x > 5", PolicyAction.DENY)
    
    assert "temp" in engine.list_policies()
    assert engine.remove_policy("temp") == True
    assert "temp" not in engine.list_policies()


# ============================================================================
# Rule Engine Tests
# ============================================================================

def test_rule_engine_basic_when_then():
    """Test basic when/then rule"""
    engine = RuleEngine()
    engine.add_rule(
        "adult_check",
        when="age >= 18",
        then=["status = 'adult'"]
    )
    
    context = {"age": 25}
    result = engine.evaluate(context)
    
    assert result.matched_count == 1
    assert result.final_outputs["status"] == "adult"


def test_rule_engine_when_then_else():
    """Test when/then/else rule"""
    engine = RuleEngine()
    engine.add_rule(
        "age_status",
        when="age >= 18",
        then=["status = 'adult'"],
        else_actions=["status = 'minor'"]
    )
    
    # Test when condition true
    context = {"age": 25}
    result = engine.evaluate(context)
    assert result.final_outputs["status"] == "adult"
    
    # Test when condition false
    context = {"age": 15}
    result = engine.evaluate(context)
    assert result.final_outputs["status"] == "minor"


def test_rule_engine_first_match_mode():
    """Test FIRST_MATCH mode"""
    engine = RuleEngine(mode=RuleMode.FIRST_MATCH)
    engine.add_rule("rule1", when="x > 5", then=["result = 'first'"])
    engine.add_rule("rule2", when="x > 3", then=["result = 'second'"])
    
    context = {"x": 10}
    result = engine.evaluate(context)
    
    # Both conditions match, but only first should execute
    assert result.matched_count == 1
    assert result.final_outputs["result"] == "first"


def test_rule_engine_priority_mode():
    """Test PRIORITY mode"""
    engine = RuleEngine(mode=RuleMode.PRIORITY)
    engine.add_rule("low_priority", when="x > 5", then=["result = 'low'"], priority=1)
    engine.add_rule("high_priority", when="x > 5", then=["result = 'high'"], priority=10)
    
    context = {"x": 10}
    result = engine.evaluate(context)
    
    # High priority rule should execute first (and only, in FIRST_MATCH behavior)
    assert "high" in result.final_outputs["result"]


def test_rule_engine_chaining():
    """Test rule chaining (rules can use outputs from previous rules)"""
    engine = RuleEngine(mode=RuleMode.ALL_MATCHES)
    engine.add_rule("step1", when="True", then=["x = 10"])
    engine.add_rule("step2", when="x == 10", then=["y = 20"])
    engine.add_rule("step3", when="y == 20", then=["z = 30"])
    
    context = {}
    result = engine.evaluate(context)
    
    assert result.final_outputs["x"] == 10
    assert result.final_outputs["y"] == 20
    assert result.final_outputs["z"] == 30


def test_rule_engine_disable_rule():
    """Test disabling specific rules"""
    engine = RuleEngine()
    engine.add_rule("rule1", when="True", then=["a = 1"])
    engine.add_rule("rule2", when="True", then=["b = 2"])
    
    engine.disable_rule("rule2")
    
    context = {}
    result = engine.evaluate(context)
    
    assert "a" in result.final_outputs
    assert "b" not in result.final_outputs


def test_rule_engine_multiple_outputs():
    """Test rules setting multiple outputs"""
    engine = RuleEngine()
    engine.add_rule(
        "premium_discount",
        when="tier == 'premium' and total > 100",
        then=["discount = 0.20", "free_shipping = True", "gift = True"]
    )
    
    context = {"tier": "premium", "total": 150}
    result = engine.evaluate(context)
    
    assert result.final_outputs["discount"] == 0.20
    assert result.final_outputs["free_shipping"] == True
    assert result.final_outputs["gift"] == True


# ============================================================================
# Decision Table Tests
# ============================================================================

def test_decision_table_basic():
    """Test basic decision table"""
    table = DecisionTable("basic", hit_policy=HitPolicy.FIRST)
    table.add_input_column("age", "age")
    table.add_output_column("category", default_value="unknown")
    
    table.add_row(["< 18"], ["minor"])
    table.add_row([">= 18"], ["adult"])
    
    # Test minor
    result = table.evaluate({"age": 15})
    assert result.outputs["category"] == "minor"
    
    # Test adult
    result = table.evaluate({"age": 25})
    assert result.outputs["category"] == "adult"


def test_decision_table_multi_input():
    """Test decision table with multiple inputs"""
    table = DecisionTable("loan_approval", hit_policy=HitPolicy.PRIORITY)
    table.add_input_column("age", "customer.age")
    table.add_input_column("income", "customer.income")
    table.add_output_column("approved", default_value=False)
    table.add_output_column("rate", default_value=0.0)
    
    table.add_row([">= 25", ">= 50000"], [True, 0.05], priority=10)
    table.add_row([">= 18", ">= 30000"], [True, 0.08], priority=5)
    table.add_row(["*", "*"], [False, 0.0], priority=1)
    
    context = {"customer": {"age": 30, "income": 60000}}
    result = table.evaluate(context)
    
    assert result.outputs["approved"] == True
    assert result.outputs["rate"] == 0.05  # Higher priority row


def test_decision_table_wildcard():
    """Test wildcard matching"""
    table = DecisionTable("wildcard_test", hit_policy=HitPolicy.FIRST)
    table.add_input_column("status", "status")
    table.add_output_column("action", default_value="none")
    
    table.add_row(["*"], ["default_action"])
    
    result = table.evaluate({"status": "anything"})
    assert result.outputs["action"] == "default_action"


def test_decision_table_range():
    """Test range conditions"""
    table = DecisionTable("age_range", hit_policy=HitPolicy.FIRST)
    table.add_input_column("age", "age")
    table.add_output_column("group", default_value="unknown")
    
    table.add_row(["0..17"], ["child"])
    table.add_row(["18..64"], ["adult"])
    table.add_row(["65..120"], ["senior"])
    
    assert table.evaluate({"age": 10}).outputs["group"] == "child"
    assert table.evaluate({"age": 30}).outputs["group"] == "adult"
    assert table.evaluate({"age": 70}).outputs["group"] == "senior"


def test_decision_table_collect_mode():
    """Test COLLECT hit policy"""
    table = DecisionTable("discount_collect", hit_policy=HitPolicy.COLLECT)
    table.add_input_column("customer_type", "customer_type")
    table.add_output_column("discount", default_value=0.0)
    
    table.add_row(["premium"], [0.10])
    table.add_row(["premium"], [0.05])
    table.add_row(["premium"], [0.02])
    
    result = table.evaluate({"customer_type": "premium"})
    
    # COLLECT mode should return list of all matching outputs
    assert isinstance(result.outputs["discount"], list)
    assert len(result.outputs["discount"]) == 3
    assert 0.10 in result.outputs["discount"]


def test_decision_table_no_match_default():
    """Test default values when no rules match"""
    table = DecisionTable("defaults", hit_policy=HitPolicy.FIRST)
    table.add_input_column("category", "category")
    table.add_output_column("price", default_value=100.0)
    
    table.add_row(["special"], [50.0])
    
    result = table.evaluate({"category": "normal"})
    assert result.outputs["price"] == 100.0  # Default value


def test_decision_table_comparison_operators():
    """Test comparison operators in conditions"""
    table = DecisionTable("comparisons", hit_policy=HitPolicy.FIRST)
    table.add_input_column("score", "score")
    table.add_output_column("grade", default_value="F")
    
    table.add_row([">= 90"], ["A"])
    table.add_row([">= 80"], ["B"])
    table.add_row([">= 70"], ["C"])
    table.add_row(["< 70"], ["F"])
    
    assert table.evaluate({"score": 95}).outputs["grade"] == "A"
    assert table.evaluate({"score": 85}).outputs["grade"] == "B"
    assert table.evaluate({"score": 75}).outputs["grade"] == "C"
    assert table.evaluate({"score": 65}).outputs["grade"] == "F"


# ============================================================================
# Constraint Checker Tests
# ============================================================================

def test_constraint_checker_precondition():
    """Test precondition validation"""
    checker = ConstraintChecker()
    checker.add_constraint(
        "positive_amount",
        ConstraintType.PRECONDITION,
        "amount > 0",
        error_message="Amount must be positive"
    )
    
    # Valid input
    result = checker.validate_preconditions({"amount": 100})
    assert result.passed == True
    
    # Invalid input
    result = checker.validate_preconditions({"amount": -50})
    assert result.passed == False
    assert len(result.violations) == 1


def test_constraint_checker_postcondition():
    """Test postcondition validation"""
    checker = ConstraintChecker()
    checker.add_constraint(
        "valid_discount",
        ConstraintType.POSTCONDITION,
        "discount >= 0 and discount <= 1",
        error_message="Discount must be between 0 and 1"
    )
    
    # Valid output
    result = checker.validate_postconditions({"discount": 0.15})
    assert result.passed == True
    
    # Invalid output
    result = checker.validate_postconditions({"discount": 1.5})
    assert result.passed == False


def test_constraint_checker_invariant():
    """Test invariant validation"""
    checker = ConstraintChecker()
    checker.add_constraint(
        "balance_positive",
        ConstraintType.INVARIANT,
        "balance >= 0",
        error_message="Balance cannot be negative"
    )
    
    result = checker.validate_invariants({"balance": 100})
    assert result.passed == True
    
    result = checker.validate_invariants({"balance": -10})
    assert result.passed == False


def test_constraint_checker_determinism():
    """Test determinism checking"""
    checker = ConstraintChecker()
    
    inputs = {"x": 10, "y": 20}
    
    # First execution
    result1 = checker.check_determinism(inputs, 30, "add_function")
    assert result1.passed == True
    
    # Second execution with same inputs and same output
    result2 = checker.check_determinism(inputs, 30, "add_function")
    assert result2.passed == True
    
    # Third execution with same inputs but different output
    result3 = checker.check_determinism(inputs, 50, "add_function")
    assert result3.passed == False
    assert len(result3.violations) == 1


def test_constraint_checker_performance():
    """Test performance constraint checking"""
    checker = ConstraintChecker()
    
    # Fast execution - should pass
    result = checker.check_performance(50.0, max_time_ms=1000)
    assert result.passed == True
    
    # Slow execution - should fail
    result = checker.check_performance(1500.0, max_time_ms=1000)
    assert result.passed == False
    assert len(result.violations) == 1
    
    # Approaching limit - should warn
    result = checker.check_performance(850.0, max_time_ms=1000)
    assert result.passed == True
    assert len(result.warnings) == 1


def test_constraint_checker_severity_levels():
    """Test different severity levels"""
    checker = ConstraintChecker()
    checker.add_constraint(
        "error_constraint",
        ConstraintType.PRECONDITION,
        "x > 0",
        severity="error"
    )
    checker.add_constraint(
        "warning_constraint",
        ConstraintType.PRECONDITION,
        "x < 100",
        severity="warning"
    )
    
    result = checker.validate_preconditions({"x": 150})
    
    # Error constraint passed, warning constraint failed
    assert result.passed == True  # No errors
    assert len(result.warnings) == 1  # But has warning


def test_constraint_checker_disabled():
    """Test disabled constraint checker"""
    checker = ConstraintChecker()
    checker.add_constraint("test", ConstraintType.PRECONDITION, "False")
    checker.enabled = False
    
    result = checker.validate_preconditions({})
    assert result.passed == True  # Disabled checker always passes


def test_constraint_checker_clear_cache():
    """Test determinism cache clearing"""
    checker = ConstraintChecker()
    
    inputs = {"x": 5}
    checker.check_determinism(inputs, 10, "test")
    
    # Cache is populated
    assert len(checker._execution_cache) > 0
    
    checker.clear_cache()
    
    # Cache is cleared
    assert len(checker._execution_cache) == 0


# ============================================================================
# Integration Tests
# ============================================================================

def test_integration_policy_rules_constraints():
    """Test integration of policy engine, rules, and constraints"""
    # Setup constraint checker
    constraints = ConstraintChecker()
    constraints.add_constraint(
        "valid_age",
        ConstraintType.PRECONDITION,
        "age > 0 and age < 150"
    )
    constraints.add_constraint(
        "valid_discount",
        ConstraintType.POSTCONDITION,
        "discount >= 0 and discount <= 1"
    )
    
    # Setup policy engine
    policies = PolicyEngine()
    policies.add_policy("allow_adults", "age >= 18", PolicyAction.ALLOW, priority=5)
    policies.add_policy("deny_minors", "age < 18", PolicyAction.DENY, priority=10)
    
    # Setup rule engine
    rules = RuleEngine()
    rules.add_rule(
        "premium_discount",
        when="age >= 25 and tier == 'premium'",
        then=["discount = 0.20"]
    )
    rules.add_rule(
        "standard_discount",
        when="age >= 18",
        then=["discount = 0.10"]
    )
    
    # Test flow for adult premium customer
    context = {"age": 30, "tier": "premium"}
    
    # 1. Validate preconditions
    pre_check = constraints.validate_preconditions(context)
    assert pre_check.passed == True
    
    # 2. Check policy
    policy_decision = policies.evaluate(context)
    assert policy_decision.allowed == True
    
    # 3. Execute rules
    rule_result = rules.evaluate(context)
    assert rule_result.final_outputs["discount"] == 0.20
    
    # 4. Validate postconditions
    post_check = constraints.validate_postconditions(rule_result.final_outputs)
    assert post_check.passed == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
