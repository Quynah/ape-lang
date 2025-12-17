"""
APE Policy Execution Engine

Policy enforcement runtime for decision validation and authorization.

Author: David Van Aelst
Status: Decision Engine v2024 - Complete
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class PolicyAction(Enum):
    """Policy enforcement actions"""
    ALLOW = "allow"
    DENY = "deny"
    GATE = "gate"  # Requires additional approval/condition
    OVERRIDE = "override"  # Override previous decisions
    ESCALATE = "escalate"  # Escalate to higher authority


@dataclass
class PolicyRule:
    """Individual policy rule"""
    name: str
    condition: str  # APE expression
    action: PolicyAction
    priority: int = 0  # Higher priority wins on conflicts
    reason: Optional[str] = None  # Human-readable explanation
    metadata: Dict[str, Any] = None  # Additional context
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PolicyDecision:
    """Result of policy evaluation"""
    action: PolicyAction
    allowed: bool
    matched_rules: List[str]  # Names of matched rules
    reason: str  # Combined reasoning
    requires_escalation: bool = False
    requires_gate: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PolicyEngine:
    """
    Policy execution and enforcement engine.
    
    Evaluates policies against context to make allow/deny decisions.
    Supports priority-based conflict resolution.
    
    Example:
        engine = PolicyEngine()
        engine.add_policy("high_value_approval", "amount > 10000", PolicyAction.GATE, priority=10)
        engine.add_policy("basic_allow", "user.verified == True", PolicyAction.ALLOW, priority=1)
        
        context = {"amount": 15000, "user": {"verified": True}}
        decision = engine.evaluate(context)
        # decision.action = GATE (higher priority wins)
    """
    
    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.enabled: bool = True
    
    def add_policy(self, name: str, condition: str, action: PolicyAction, 
                   priority: int = 0, reason: Optional[str] = None) -> None:
        """
        Add a policy rule.
        
        Args:
            name: Unique policy identifier
            condition: APE expression to evaluate
            action: Action to take if condition matches
            priority: Priority level (higher wins conflicts)
            reason: Human-readable explanation
        """
        policy = PolicyRule(
            name=name,
            condition=condition,
            action=action,
            priority=priority,
            reason=reason
        )
        self.policies.append(policy)
        # Keep sorted by priority (descending)
        self.policies.sort(key=lambda p: p.priority, reverse=True)
    
    def remove_policy(self, name: str) -> bool:
        """
        Remove a policy by name.
        
        Args:
            name: Policy identifier
        
        Returns:
            True if policy was found and removed
        """
        original_len = len(self.policies)
        self.policies = [p for p in self.policies if p.name != name]
        return len(self.policies) < original_len
    
    def evaluate(self, context: Dict[str, Any], 
                 executor: Optional[Any] = None) -> PolicyDecision:
        """
        Evaluate all policies against a context.
        
        Args:
            context: Context data for evaluation
            executor: RuntimeExecutor instance for evaluating conditions
        
        Returns:
            PolicyDecision with action and reasoning
        """
        if not self.enabled:
            return PolicyDecision(
                action=PolicyAction.ALLOW,
                allowed=True,
                matched_rules=[],
                reason="Policy engine disabled"
            )
        
        matched: List[PolicyRule] = []
        
        # Evaluate all policies (already sorted by priority)
        for policy in self.policies:
            # Evaluate condition against context
            if self._evaluate_condition(policy.condition, context, executor):
                matched.append(policy)
        
        # No matches = default allow
        if not matched:
            return PolicyDecision(
                action=PolicyAction.ALLOW,
                allowed=True,
                matched_rules=[],
                reason="No policy rules matched - default allow"
            )
        
        # Take highest priority match
        winning_policy = matched[0]
        
        # Build decision
        decision = PolicyDecision(
            action=winning_policy.action,
            allowed=winning_policy.action == PolicyAction.ALLOW,
            matched_rules=[p.name for p in matched],
            reason=winning_policy.reason or f"Policy '{winning_policy.name}' matched",
            requires_escalation=winning_policy.action == PolicyAction.ESCALATE,
            requires_gate=winning_policy.action == PolicyAction.GATE,
            metadata={"priority": winning_policy.priority}
        )
        
        return decision
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any], 
                           executor: Optional[Any]) -> bool:
        """
        Evaluate a condition expression.
        
        Args:
            condition: APE expression string
            context: Context variables
            executor: RuntimeExecutor instance
        
        Returns:
            True if condition evaluates to truthy value
        """
        if executor is None:
            # Simple fallback: convert dicts to objects for dot notation support
            try:
                # Wrapper class that allows dict.key notation
                class DictWrapper:
                    def __init__(self, data):
                        for k, v in data.items():
                            if isinstance(v, dict):
                                setattr(self, k, DictWrapper(v))
                            else:
                                setattr(self, k, v)
                
                # Build namespace with wrapped objects
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
            # Use APE executor to evaluate expression
            try:
                from ape.tokenizer.tokenizer import Tokenizer
                from ape.parser.parser import Parser
                
                tokenizer = Tokenizer(condition)
                tokens = tokenizer.tokenize()
                parser = Parser(tokens)
                
                # Parse as expression
                # Note: This is simplified - in production would need proper expression parsing
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
                # Recursively flatten
                result.update(self._flatten_context(value, full_key))
                # Also keep the dict itself for dict access
                result[key if not prefix else full_key] = value
            else:
                result[full_key] = value
                if not prefix:
                    result[key] = value
        return result
    
    def get_policy(self, name: str) -> Optional[PolicyRule]:
        """Get a policy by name"""
        for policy in self.policies:
            if policy.name == name:
                return policy
        return None
    
    def list_policies(self) -> List[str]:
        """Get list of all policy names"""
        return [p.name for p in self.policies]
    
    def clear_policies(self) -> None:
        """Remove all policies"""
        self.policies.clear()
    
    def disable(self) -> None:
        """Disable policy enforcement"""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable policy enforcement"""
        self.enabled = True


__all__ = ['PolicyEngine', 'PolicyAction', 'PolicyRule', 'PolicyDecision']
