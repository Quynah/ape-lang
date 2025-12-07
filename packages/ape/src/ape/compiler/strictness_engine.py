"""
Ape Strictness Engine

Enforces Ape's strictness principles:
- Detects ambiguity in behavior
- Enforces determinism
- Validates deviation bounds and policy conflicts
- Ensures all behavior is explicitly declared
"""

from typing import List, Dict
from .ir_nodes import (
    ProjectNode, ModuleNode, TaskNode, FlowNode, StepNode,
    PolicyNode, DeviationNode
)
from .errors import (
    ApeError, ErrorCode, ErrorCategory, ErrorCollector
)


class StrictnessEngine:
    """
    Strictness enforcement engine for Ape.
    
    Implements the core Ape principle:
    "What is allowed, is fully allowed. 
     What is forbidden, is strictly forbidden. 
     What is not declared, does not exist."
    """
    
    def __init__(self):
        self.errors = ErrorCollector()
        self.policies: Dict[str, PolicyNode] = {}
    
    def enforce(self, project: ProjectNode) -> List[ApeError]:
        """
        Enforce strictness rules on an Ape project.
        
        Checks:
        - Ambiguity detection in steps
        - Undeclared behavior
        - Determinism enforcement
        - Deviation bounds validation
        - Policy conflicts
        
        Args:
            project: The project IR to validate
        
        Returns:
            List of strictness violations (empty if all rules satisfied)
        """
        self.errors.clear()
        self.policies.clear()
        
        # Collect all policies
        self._collect_policies(project)
        
        # Check each module
        for module in project.modules:
            self._check_module_strictness(module)
        
        return self.errors.get_errors()
    
    def _collect_policies(self, project: ProjectNode):
        """Collect all policies from project"""
        for policy in project.global_policies:
            self.policies[policy.name] = policy
        
        for module in project.modules:
            for policy in module.policies:
                if policy.name not in self.policies:
                    self.policies[policy.name] = policy
    
    def _check_module_strictness(self, module: ModuleNode):
        """Check strictness for all constructs in a module"""
        # Check tasks
        for task in module.tasks:
            self._check_task_strictness(task)
        
        # Check flows
        for flow in module.flows:
            self._check_flow_strictness(flow)
    
    def _check_task_strictness(self, task: TaskNode):
        """
        Check strictness rules for a task.
        
        Validates:
        - No ambiguous steps
        - All behavior is declared
        - Determinism is maintained
        - Deviation is properly controlled
        """
        # Check if task has steps (already validated in SemanticValidator, but double-check)
        if not task.steps:
            self.errors.add_error(
                ErrorCode.E_UNDECLARED_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Task '{task.name}' has no declared behavior (no steps)",
                task.location,
                {"task": task.name}
            )
        
        # Check each step for ambiguity
        for step in task.steps:
            self._check_step_ambiguity(step, f"task '{task.name}'")
        
        # Check deviation rules - can be in task.deviation or in constraints
        deviation_node = task.deviation
        if not deviation_node:
            # Check if there's a DeviationNode in constraints
            for constraint in task.constraints:
                if isinstance(constraint, DeviationNode):
                    deviation_node = constraint
                    break
        
        if deviation_node:
            self._check_deviation_strictness(deviation_node, task, f"task '{task.name}'")
        else:
            # No deviation allowed - check for implicit ambiguity
            self._check_no_implicit_ambiguity(task.steps, f"task '{task.name}'")
    
    def _check_flow_strictness(self, flow: FlowNode):
        """
        Check strictness rules for a flow.
        
        Similar to task strictness but for flows.
        """
        if not flow.steps:
            self.errors.add_error(
                ErrorCode.E_UNDECLARED_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Flow '{flow.name}' has no declared behavior (no steps)",
                flow.location,
                {"flow": flow.name}
            )
        
        # Check each step for ambiguity
        for step in flow.steps:
            self._check_step_ambiguity(step, f"flow '{flow.name}'")
        
        # Check deviation rules - can be in flow.deviation or in constraints
        deviation_node = flow.deviation
        if not deviation_node:
            # Check if there's a DeviationNode in constraints
            for constraint in flow.constraints:
                if isinstance(constraint, DeviationNode):
                    deviation_node = constraint
                    break
        
        if deviation_node:
            self._check_deviation_strictness(deviation_node, flow, f"flow '{flow.name}'")
        else:
            # No deviation allowed - check for implicit ambiguity
            self._check_no_implicit_ambiguity(flow.steps, f"flow '{flow.name}'")
    
    def _check_step_ambiguity(self, step: StepNode, context: str):
        """
        Check a step for ambiguous behavior.
        
        Ambiguous indicators:
        - Vague action words without clear semantics
        - Multiple interpretations possible
        - Unclear control flow
        """
        if not step.action:
            return
        
        action_lower = step.action.lower()
        
        # Check for ambiguous keywords
        ambiguous_keywords = [
            'maybe', 'possibly', 'might', 'could', 
            'if needed', 'as appropriate', 'when necessary',
            'somehow', 'etc', 'and so on'
        ]
        
        for keyword in ambiguous_keywords:
            if keyword in action_lower:
                self.errors.add_error(
                    ErrorCode.E_AMBIGUOUS_BEHAVIOR,
                    ErrorCategory.STRICTNESS,
                    f"Ambiguous step in {context}: contains '{keyword}' which is non-deterministic",
                    step.location,
                    {"context": context, "step": step.action, "keyword": keyword},
                    suggestion="Make the step action explicit and deterministic, or declare controlled deviation"
                )
        
        # Check for question marks (indicate uncertainty)
        if '?' in step.action:
            self.errors.add_error(
                ErrorCode.E_AMBIGUOUS_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Ambiguous step in {context}: contains '?' indicating uncertainty",
                step.location,
                {"context": context, "step": step.action},
                suggestion="Remove questions and make behavior explicit"
            )
        
        # Check substeps recursively
        for substep in step.substeps:
            self._check_step_ambiguity(substep, context)
    
    def _check_no_implicit_ambiguity(self, steps: List[StepNode], context: str):
        """
        When no deviation is declared, ensure there's no implicit ambiguity.
        
        This is a strict check: without explicit deviation declaration,
        any ambiguity is forbidden.
        """
        import re
        
        for step in steps:
            # Check for words that suggest choice or variation
            if not step.action:
                continue
            
            action_lower = step.action.lower()
            
            # Check for 'or' as a separate word (not part of 'for', 'or' in words like 'format')
            # Use word boundaries to match 'or' as a standalone word
            if re.search(r'\bor\b', action_lower):
                self.errors.add_error(
                    ErrorCode.E_DEVIATION_NOT_DECLARED,
                    ErrorCategory.DEVIATION,
                    f"Step in {context} suggests choice ('or') but no deviation is declared",
                    step.location,
                    {"context": context, "step": step.action, "keyword": "or"},
                    suggestion="Declare controlled deviation with explicit bounds, or make behavior deterministic"
                )
            
            # Check for other choice keywords
            choice_keywords = [
                'alternatively', 'optionally', 'either',
                'choose', 'select', 'pick', 'decide'
            ]
            
            for keyword in choice_keywords:
                if re.search(r'\b' + keyword + r'\b', action_lower):
                    self.errors.add_error(
                        ErrorCode.E_DEVIATION_NOT_DECLARED,
                        ErrorCategory.DEVIATION,
                        f"Step in {context} suggests choice ('{keyword}') but no deviation is declared",
                        step.location,
                        {"context": context, "step": step.action, "keyword": keyword},
                        suggestion="Declare controlled deviation with explicit bounds, or make behavior deterministic"
                    )
            
            # Check substeps
            if step.substeps:
                self._check_no_implicit_ambiguity(step.substeps, context)
    
    def _check_deviation_strictness(self, deviation: DeviationNode, 
                                    parent: any, context: str):
        """
        Check that deviation is properly controlled and doesn't conflict with policies.
        
        RFC-0001 rules:
        - Deviation must have bounds
        - Bounds must be explicit
        - Deviation must not conflict with policies
        """
        # Check bounds existence (should be caught by semantic validator, but enforce here too)
        if not deviation.bounds:
            self.errors.add_error(
                ErrorCode.E_DEVIATION_UNBOUNDED,
                ErrorCategory.DEVIATION,
                f"Unbounded deviation in {context} is strictly forbidden",
                deviation.location,
                {"context": context},
                suggestion="Add explicit bounds to control the deviation"
            )
            return
        
        # Check that bounds are not trivial
        trivial_bounds = ['anything', 'any', 'whatever', 'no restrictions']
        for bound in deviation.bounds:
            bound_lower = bound.lower().strip()
            if bound_lower in trivial_bounds or len(bound_lower) < 5:
                self.errors.add_error(
                    ErrorCode.E_DEVIATION_AMBIGUOUS_BOUND,
                    ErrorCategory.DEVIATION,
                    f"Deviation bound '{bound}' in {context} is too vague or trivial",
                    deviation.location,
                    {"context": context, "bound": bound},
                    suggestion="Provide specific, measurable bounds"
                )
        
        # Check for policy conflicts
        self._check_deviation_policy_conflicts(deviation, context)
    
    def _check_deviation_policy_conflicts(self, deviation: DeviationNode, context: str):
        """
        Check if deviation conflicts with any policies.
        
        This is a simplified check - a full implementation would parse
        bounds and rules to detect semantic conflicts.
        """
        # For each policy, check if deviation violates it
        for policy_name, policy in self.policies.items():
            for rule in policy.rules:
                rule_lower = rule.lower()
                
                # Check if deviation mode conflicts with policy rules
                # Examples of conflicts:
                # - Policy requires determinism, but deviation is creative
                # - Policy forbids side effects, but deviation allows them
                
                deterministic_keywords = ['deterministic', 'predictable', 'reproducible']
                if deviation.mode.value == 'creative':
                    for keyword in deterministic_keywords:
                        if keyword in rule_lower:
                            self.errors.add_error(
                                ErrorCode.E_DEVIATION_POLICY_CONFLICT,
                                ErrorCategory.DEVIATION,
                                f"Deviation in {context} conflicts with policy '{policy_name}': "
                                f"creative mode violates '{rule}'",
                                deviation.location,
                                {
                                    "context": context,
                                    "policy": policy_name,
                                    "rule": rule,
                                    "deviation_mode": deviation.mode.value
                                },
                                suggestion="Either change deviation mode or adjust policy scope"
                            )
                
                # Check if bounds mention forbidden things in policy
                forbidden_keywords = ['side effect', 'external', 'random', 'non-deterministic']
                for bound in deviation.bounds:
                    bound_lower = bound.lower()
                    for keyword in forbidden_keywords:
                        if keyword in rule_lower and keyword in bound_lower:
                            # This is a potential conflict - policy forbids something that bound mentions
                            if 'no' in rule_lower or 'forbidden' in rule_lower or 'must not' in rule_lower:
                                self.errors.add_error(
                                    ErrorCode.E_DEVIATION_POLICY_CONFLICT,
                                    ErrorCategory.DEVIATION,
                                    f"Deviation bound in {context} may conflict with policy '{policy_name}': "
                                    f"bound mentions '{keyword}' which policy restricts",
                                    deviation.location,
                                    {
                                        "context": context,
                                        "policy": policy_name,
                                        "rule": rule,
                                        "bound": bound,
                                        "keyword": keyword
                                    },
                                    suggestion="Ensure deviation bounds comply with all applicable policies"
                                )
    
    def _check_determinism(self, steps: List[StepNode], context: str):
        """
        Check that steps are deterministic.
        
        Non-deterministic indicators:
        - Random operations
        - Time-dependent operations without explicit bounds
        - External dependencies without contracts
        """
        for step in steps:
            if not step.action:
                continue
            
            action_lower = step.action.lower()
            
            # Check for non-deterministic operations
            non_deterministic_keywords = [
                'random', 'shuffle', 'arbitrary', 
                'current time', 'now()', 'timestamp',
                'uuid', 'guid'
            ]
            
            for keyword in non_deterministic_keywords:
                if keyword in action_lower:
                    self.errors.add_error(
                        ErrorCode.E_NON_DETERMINISTIC,
                        ErrorCategory.STRICTNESS,
                        f"Non-deterministic operation in {context}: '{keyword}' without explicit deviation",
                        step.location,
                        {"context": context, "step": step.action, "operation": keyword},
                        suggestion="Either make operation deterministic or declare controlled deviation"
                    )
            
            # Check substeps
            if step.substeps:
                self._check_determinism(step.substeps, context)
