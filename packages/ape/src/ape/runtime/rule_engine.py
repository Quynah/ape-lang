"""
APE When/Then/Else Rule Engine

Deterministic rule evaluation for decision logic.

Author: David Van Aelst
Status: Decision Engine v2024 - Complete
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class RuleMode(Enum):
    """Rule evaluation modes"""
    FIRST_MATCH = "first"  # Stop at first matching rule
    ALL_MATCHES = "all"    # Evaluate all matching rules
    PRIORITY = "priority"  # Use priority-based ordering


@dataclass
class WhenThenRule:
    """
    When/Then rule with optional Else.
    
    Example:
        when age >= 18:
            then status = "adult"
        else:
            status = "minor"
    """
    name: str
    when_condition: str  # APE expression
    then_actions: List[str] = field(default_factory=list)  # APE statements
    else_actions: List[str] = field(default_factory=list)  # APE statements
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleResult:
    """Result of rule evaluation"""
    matched: bool
    rule_name: str
    outputs: Dict[str, Any]  # Variables set by rule
    executed_actions: List[str]  # Actions that were executed
    reason: str  # Explanation
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleSetResult:
    """Result of evaluating a rule set"""
    rule_results: List[RuleResult]
    final_outputs: Dict[str, Any]  # Combined outputs from all rules
    matched_count: int
    total_evaluated: int
    
    @property
    def any_matched(self) -> bool:
        """Check if any rules matched"""
        return self.matched_count > 0
    
    @property
    def all_matched(self) -> bool:
        """Check if all rules matched"""
        return self.matched_count == self.total_evaluated


class RuleEngine:
    """
    When/Then/Else rule execution engine.
    
    Evaluates conditions and executes actions deterministically.
    Supports chaining, priority ordering, and conflict resolution.
    
    Example:
        engine = RuleEngine(mode=RuleMode.PRIORITY)
        
        engine.add_rule(
            "premium_discount",
            when="customer.tier == 'premium' and order.total > 100",
            then=["discount = 0.20", "free_shipping = True"],
            priority=10
        )
        
        engine.add_rule(
            "standard_discount",
            when="order.total > 50",
            then=["discount = 0.10"],
            priority=5
        )
        
        context = {"customer": {"tier": "premium"}, "order": {"total": 150}}
        result = engine.evaluate(context)
        # result.final_outputs = {"discount": 0.20, "free_shipping": True}
    """
    
    def __init__(self, mode: RuleMode = RuleMode.FIRST_MATCH):
        self.rules: List[WhenThenRule] = []
        self.mode = mode
        self.enabled = True
    
    def add_rule(self, name: str, when: str, then: List[str], 
                 else_actions: Optional[List[str]] = None,
                 priority: int = 0) -> None:
        """
        Add a when/then rule.
        
        Args:
            name: Unique rule identifier
            when: Condition expression
            then: Actions to execute if condition is true
            else_actions: Actions to execute if condition is false
            priority: Priority level (higher executes first in PRIORITY mode)
        """
        rule = WhenThenRule(
            name=name,
            when_condition=when,
            then_actions=then,
            else_actions=else_actions or [],
            priority=priority
        )
        self.rules.append(rule)
        
        # Sort by priority if in priority mode
        if self.mode == RuleMode.PRIORITY:
            self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name"""
        original_len = len(self.rules)
        self.rules = [r for r in self.rules if r.name != name]
        return len(self.rules) < original_len
    
    def evaluate(self, context: Dict[str, Any], 
                 executor: Optional[Any] = None) -> RuleSetResult:
        """
        Evaluate all rules against context.
        
        Args:
            context: Input variables for evaluation
            executor: RuntimeExecutor instance for evaluating expressions
        
        Returns:
            RuleSetResult with all matched rules and combined outputs
        """
        if not self.enabled:
            return RuleSetResult(
                rule_results=[],
                final_outputs={},
                matched_count=0,
                total_evaluated=0
            )
        
        results: List[RuleResult] = []
        combined_outputs = dict(context)  # Start with input context
        matched_count = 0
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Evaluate condition
            condition_met = self._evaluate_condition(
                rule.when_condition, 
                combined_outputs,  # Use accumulated context
                executor
            )
            
            # Execute appropriate actions
            if condition_met:
                actions = rule.then_actions
                executed = actions
                matched_count += 1
            else:
                actions = rule.else_actions
                executed = actions if actions else []
            
            # Execute actions and collect outputs
            rule_outputs = self._execute_actions(actions, combined_outputs, executor)
            
            # Update combined outputs
            combined_outputs.update(rule_outputs)
            
            # Record result
            result = RuleResult(
                matched=condition_met,
                rule_name=rule.name,
                outputs=rule_outputs,
                executed_actions=executed,
                reason=f"Rule '{rule.name}' {'matched' if condition_met else 'did not match'}"
            )
            results.append(result)
            
            # Stop at first match if in FIRST_MATCH or PRIORITY mode
            if (self.mode in (RuleMode.FIRST_MATCH, RuleMode.PRIORITY)) and condition_met:
                break
        
        return RuleSetResult(
            rule_results=results,
            final_outputs=combined_outputs,
            matched_count=matched_count,
            total_evaluated=len(results)
        )
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any],
                           executor: Optional[Any]) -> bool:
        """Evaluate a when condition"""
        if not condition:
            return True  # Empty condition = always true
        
        if executor is None:
            # Fallback: convert dicts to objects for dot notation support
            try:
                class DictWrapper:
                    def __init__(self, data):
                        for k, v in data.items():
                            if isinstance(v, dict):
                                setattr(self, k, DictWrapper(v))
                            else:
                                setattr(self, k, v)
                
                namespace = {}
                for key, value in context.items():
                    if isinstance(value, dict):
                        namespace[key] = DictWrapper(value)
                    else:
                        namespace[key] = value
                
                result = eval(condition, {"__builtins__": {}}, namespace)
                return bool(result)
            except Exception:
                return False
        else:
            # Use APE executor
            try:
                result = executor.eval_expression_with_context(condition, context)
                return bool(result)
            except Exception:
                return False
    
    def _flatten_context(self, context: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dicts for expression evaluation"""
        result = {}
        for key, value in context.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_context(value, full_key))
                result[key if not prefix else full_key] = value
            else:
                result[full_key] = value
                if not prefix:
                    result[key] = value
        return result
    
    def _execute_actions(self, actions: List[str], context: Dict[str, Any],
                        executor: Optional[Any]) -> Dict[str, Any]:
        """
        Execute a list of action statements.
        
        Returns:
            Dict of variables set by actions
        """
        outputs = {}
        
        for action in actions:
            # Parse assignment: "variable = expression"
            if '=' in action:
                parts = action.split('=', 1)
                var_name = parts[0].strip()
                expression = parts[1].strip()
                
                # Evaluate expression
                if executor is None:
                    # Fallback: Python eval
                    try:
                        namespace = dict(context)
                        namespace.update(outputs)  # Include previously set vars
                        value = eval(expression, {"__builtins__": {}}, namespace)
                        outputs[var_name] = value
                        context[var_name] = value  # Update context for next action
                    except Exception:
                        outputs[var_name] = None
                else:
                    # Use APE executor
                    try:
                        value = executor.eval_expression_with_context(
                            expression,
                            {**context, **outputs}
                        )
                        outputs[var_name] = value
                        context[var_name] = value
                    except Exception:
                        outputs[var_name] = None
        
        return outputs
    
    def get_rule(self, name: str) -> Optional[WhenThenRule]:
        """Get a rule by name"""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def list_rules(self) -> List[str]:
        """Get list of all rule names"""
        return [r.name for r in self.rules]
    
    def clear_rules(self) -> None:
        """Remove all rules"""
        self.rules.clear()
    
    def enable_rule(self, name: str) -> bool:
        """Enable a specific rule"""
        rule = self.get_rule(name)
        if rule:
            rule.enabled = True
            return True
        return False
    
    def disable_rule(self, name: str) -> bool:
        """Disable a specific rule"""
        rule = self.get_rule(name)
        if rule:
            rule.enabled = False
            return True
        return False


__all__ = ['RuleEngine', 'RuleMode', 'WhenThenRule', 'RuleResult', 'RuleSetResult']
