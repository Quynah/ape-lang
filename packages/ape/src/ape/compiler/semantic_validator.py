"""
Ape Semantic Validator

Performs semantic validation on Ape IR structures.
Enforces Ape's strict principle: "What is allowed, is fully allowed. 
What is forbidden, is strictly forbidden. What is not declared, does not exist."
"""

from typing import List, Dict, Set, Optional
from .ir_nodes import (
    ProjectNode, ModuleNode, EntityNode, TaskNode, FlowNode,
    PolicyNode, EnumNode, DeviationNode, StepNode,
    Location
)
from .errors import (
    ApeError, ErrorCode, ErrorCategory, ErrorCollector
)


class SymbolTable:
    """
    Symbol table for tracking declared entities, types, and identifiers.
    Enforces: "What is not declared, does not exist."
    """
    
    def __init__(self):
        self.entities: Dict[str, EntityNode] = {}
        self.enums: Dict[str, EnumNode] = {}
        self.tasks: Dict[str, TaskNode] = {}
        self.flows: Dict[str, FlowNode] = {}
        self.policies: Dict[str, PolicyNode] = {}
        self.builtin_types: Set[str] = {
            'String', 'Integer', 'Float', 'Boolean', 
            'Any', 'List', 'Dict', 'Optional'
        }
    
    def add_entity(self, entity: EntityNode, location: Location) -> Optional[ApeError]:
        """Add entity to symbol table, return error if duplicate"""
        if entity.name in self.entities:
            return ApeError(
                code=ErrorCode.E_DUPLICATE_DEFINITION,
                category=ErrorCategory.SEMANTIC,
                message=f"Entity '{entity.name}' is already defined",
                location=location,
                context={"symbol": entity.name, "kind": "entity"}
            )
        self.entities[entity.name] = entity
        return None
    
    def add_enum(self, enum: EnumNode, location: Location) -> Optional[ApeError]:
        """Add enum to symbol table, return error if duplicate"""
        if enum.name in self.enums:
            return ApeError(
                code=ErrorCode.E_DUPLICATE_DEFINITION,
                category=ErrorCategory.SEMANTIC,
                message=f"Enum '{enum.name}' is already defined",
                location=location,
                context={"symbol": enum.name, "kind": "enum"}
            )
        self.enums[enum.name] = enum
        return None
    
    def add_task(self, task: TaskNode, location: Location) -> Optional[ApeError]:
        """Add task to symbol table, return error if duplicate"""
        if task.name in self.tasks:
            return ApeError(
                code=ErrorCode.E_DUPLICATE_DEFINITION,
                category=ErrorCategory.SEMANTIC,
                message=f"Task '{task.name}' is already defined",
                location=location,
                context={"symbol": task.name, "kind": "task"}
            )
        self.tasks[task.name] = task
        return None
    
    def add_flow(self, flow: FlowNode, location: Location) -> Optional[ApeError]:
        """Add flow to symbol table, return error if duplicate"""
        if flow.name in self.flows:
            return ApeError(
                code=ErrorCode.E_DUPLICATE_DEFINITION,
                category=ErrorCategory.SEMANTIC,
                message=f"Flow '{flow.name}' is already defined",
                location=location,
                context={"symbol": flow.name, "kind": "flow"}
            )
        self.flows[flow.name] = flow
        return None
    
    def add_policy(self, policy: PolicyNode, location: Location) -> Optional[ApeError]:
        """Add policy to symbol table, return error if duplicate"""
        if policy.name in self.policies:
            return ApeError(
                code=ErrorCode.E_DUPLICATE_DEFINITION,
                category=ErrorCategory.SEMANTIC,
                message=f"Policy '{policy.name}' is already defined",
                location=location,
                context={"symbol": policy.name, "kind": "policy"}
            )
        self.policies[policy.name] = policy
        return None
    
    def type_exists(self, type_name: str) -> bool:
        """Check if a type is declared or is a builtin"""
        # Remove Optional[] wrapper if present
        if type_name.startswith('Optional[') and type_name.endswith(']'):
            type_name = type_name[9:-1]
        
        return (type_name in self.builtin_types or 
                type_name in self.entities or 
                type_name in self.enums)
    
    def symbol_exists(self, name: str) -> bool:
        """Check if any symbol with given name exists"""
        return (name in self.entities or 
                name in self.enums or 
                name in self.tasks or 
                name in self.flows or
                name in self.policies)


class SemanticValidator:
    """
    Semantic validator for Ape IR.
    
    Validates:
    - Symbol definitions and references
    - Type correctness
    - Contract compliance
    - Policy adherence
    - Deviation correctness (RFC-0001)
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = ErrorCollector()
        self.current_module: Optional[ModuleNode] = None
    
    def validate_project(self, project: ProjectNode) -> List[ApeError]:
        """
        Validate an entire Ape project.
        
        Args:
            project: The project IR to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        self.errors.clear()
        self.symbol_table = SymbolTable()
        
        # First pass: collect all symbols
        for module in project.modules:
            self._collect_module_symbols(module)
        
        # Second pass: validate each module
        for module in project.modules:
            self._validate_module(module)
        
        # Validate global policies
        for policy in project.global_policies:
            self._validate_policy(policy)
        
        return self.errors.get_errors()
    
    def _collect_module_symbols(self, module: ModuleNode):
        """First pass: collect all symbol definitions"""
        for entity in module.entities:
            error = self.symbol_table.add_entity(entity, entity.location)
            if error:
                self.errors.add(error)
        
        for enum in module.enums:
            error = self.symbol_table.add_enum(enum, enum.location)
            if error:
                self.errors.add(error)
        
        for task in module.tasks:
            error = self.symbol_table.add_task(task, task.location)
            if error:
                self.errors.add(error)
        
        for flow in module.flows:
            error = self.symbol_table.add_flow(flow, flow.location)
            if error:
                self.errors.add(error)
        
        for policy in module.policies:
            error = self.symbol_table.add_policy(policy, policy.location)
            if error:
                self.errors.add(error)
    
    def _validate_module(self, module: ModuleNode):
        """
        Validate a module and all its contents.
        
        Checks:
        - All imported modules exist (placeholder)
        - All definitions are valid
        """
        self.current_module = module
        
        # Validate entities
        for entity in module.entities:
            self._validate_entity(entity)
        
        # Validate enums
        for enum in module.enums:
            self._validate_enum(enum)
        
        # Validate tasks
        for task in module.tasks:
            self._validate_task(task)
        
        # Validate flows
        for flow in module.flows:
            self._validate_flow(flow)
        
        # Validate policies
        for policy in module.policies:
            self._validate_policy(policy)
    
    def _validate_entity(self, entity: EntityNode):
        """
        Validate an entity definition.
        
        Checks:
        - All field types exist
        - No duplicate field names
        - Constraints are valid
        """
        if not entity.name:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                "Entity must have a name",
                entity.location,
                {"kind": "entity"}
            )
            return
        
        # Check for duplicate field names
        field_names: Set[str] = set()
        for field in entity.fields:
            if field.name in field_names:
                self.errors.add_error(
                    ErrorCode.E_DUPLICATE_DEFINITION,
                    ErrorCategory.SEMANTIC,
                    f"Duplicate field '{field.name}' in entity '{entity.name}'",
                    field.location,
                    {"entity": entity.name, "field": field.name}
                )
            field_names.add(field.name)
            
            # Validate field type exists
            if not self.symbol_table.type_exists(field.type):
                self.errors.add_error(
                    ErrorCode.E_UNKNOWN_TYPE,
                    ErrorCategory.TYPE,
                    f"Unknown type '{field.type}' for field '{field.name}' in entity '{entity.name}'",
                    field.location,
                    {"entity": entity.name, "field": field.name, "type": field.type},
                    suggestion=f"Did you mean one of: {', '.join(list(self.symbol_table.entities.keys())[:3])}?"
                )
        
        # Validate constraints (can be ConstraintNode or DeviationNode)
        for constraint in entity.constraints:
            if isinstance(constraint, DeviationNode):
                self._validate_deviation(constraint, f"entity '{entity.name}'")
            else:
                self._validate_constraint(constraint, f"entity '{entity.name}'")
    
    def _validate_enum(self, enum: EnumNode):
        """
        Validate an enum definition.
        
        Checks:
        - Has at least one value
        - No duplicate values
        """
        if not enum.name:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                "Enum must have a name",
                enum.location,
                {"kind": "enum"}
            )
            return
        
        if not enum.values:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                f"Enum '{enum.name}' must have at least one value",
                enum.location,
                {"enum": enum.name}
            )
        
        # Check for duplicate values
        value_set: Set[str] = set()
        for value in enum.values:
            if value in value_set:
                self.errors.add_error(
                    ErrorCode.E_DUPLICATE_DEFINITION,
                    ErrorCategory.SEMANTIC,
                    f"Duplicate value '{value}' in enum '{enum.name}'",
                    enum.location,
                    {"enum": enum.name, "value": value}
                )
            value_set.add(value)
    
    def _validate_task(self, task: TaskNode):
        """
        Validate a task definition.
        
        Checks:
        - Input/output types exist
        - Steps are valid
        - Constraints are valid
        - Deviation (if present) is valid
        """
        if not task.name:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                "Task must have a name",
                task.location,
                {"kind": "task"}
            )
            return
        
        # Validate inputs
        input_names: Set[str] = set()
        for input_field in task.inputs:
            if input_field.name in input_names:
                self.errors.add_error(
                    ErrorCode.E_DUPLICATE_DEFINITION,
                    ErrorCategory.SEMANTIC,
                    f"Duplicate input '{input_field.name}' in task '{task.name}'",
                    input_field.location,
                    {"task": task.name, "input": input_field.name}
                )
            input_names.add(input_field.name)
            
            if not self.symbol_table.type_exists(input_field.type):
                self.errors.add_error(
                    ErrorCode.E_UNKNOWN_TYPE,
                    ErrorCategory.TYPE,
                    f"Unknown type '{input_field.type}' for input '{input_field.name}' in task '{task.name}'",
                    input_field.location,
                    {"task": task.name, "input": input_field.name, "type": input_field.type}
                )
        
        # Validate outputs
        output_names: Set[str] = set()
        for output_field in task.outputs:
            if output_field.name in output_names:
                self.errors.add_error(
                    ErrorCode.E_DUPLICATE_DEFINITION,
                    ErrorCategory.SEMANTIC,
                    f"Duplicate output '{output_field.name}' in task '{task.name}'",
                    output_field.location,
                    {"task": task.name, "output": output_field.name}
                )
            output_names.add(output_field.name)
            
            if not self.symbol_table.type_exists(output_field.type):
                self.errors.add_error(
                    ErrorCode.E_UNKNOWN_TYPE,
                    ErrorCategory.TYPE,
                    f"Unknown type '{output_field.type}' for output '{output_field.name}' in task '{task.name}'",
                    output_field.location,
                    {"task": task.name, "output": output_field.name, "type": output_field.type}
                )
        
        # Validate steps
        if not task.steps:
            self.errors.add_error(
                ErrorCode.E_UNDECLARED_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Task '{task.name}' has no steps defined",
                task.location,
                {"task": task.name},
                suggestion="Add at least one step to define the task behavior"
            )
        
        for step in task.steps:
            self._validate_step(step, f"task '{task.name}'")
        
        # Validate constraints (can be ConstraintNode or DeviationNode)
        for constraint in task.constraints:
            if isinstance(constraint, DeviationNode):
                self._validate_deviation(constraint, f"task '{task.name}'")
            else:
                self._validate_constraint(constraint, f"task '{task.name}'")
        
        # Validate deviation if present
        if task.deviation:
            self._validate_deviation(task.deviation, f"task '{task.name}'")
    
    def _validate_flow(self, flow: FlowNode):
        """
        Validate a flow definition.
        
        Checks:
        - Steps are valid
        - Constraints are valid
        - Deviation (if present) is valid
        """
        if not flow.name:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                "Flow must have a name",
                flow.location,
                {"kind": "flow"}
            )
            return
        
        # Validate steps
        if not flow.steps:
            self.errors.add_error(
                ErrorCode.E_UNDECLARED_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Flow '{flow.name}' has no steps defined",
                flow.location,
                {"flow": flow.name},
                suggestion="Add at least one step to define the flow behavior"
            )
        
        for step in flow.steps:
            self._validate_step(step, f"flow '{flow.name}'")
        
        # Validate constraints (can be ConstraintNode or DeviationNode)
        for constraint in flow.constraints:
            if isinstance(constraint, DeviationNode):
                self._validate_deviation(constraint, f"flow '{flow.name}'")
            else:
                self._validate_constraint(constraint, f"flow '{flow.name}'")
        
        # Validate deviation if present
        if flow.deviation:
            self._validate_deviation(flow.deviation, f"flow '{flow.name}'")
    
    def _validate_policy(self, policy: PolicyNode):
        """
        Validate a policy definition.
        
        Checks:
        - Has at least one rule
        - Scope is valid
        """
        if not policy.name:
            self.errors.add_error(
                ErrorCode.E_UNDEFINED_SYMBOL,
                ErrorCategory.SEMANTIC,
                "Policy must have a name",
                policy.location,
                {"kind": "policy"}
            )
            return
        
        if not policy.rules:
            self.errors.add_error(
                ErrorCode.E_POLICY_VIOLATION,
                ErrorCategory.POLICY,
                f"Policy '{policy.name}' has no rules defined",
                policy.location,
                {"policy": policy.name}
            )
        
        # Validate scope
        valid_scopes = {'global', 'module', 'task', 'flow'}
        if policy.scope not in valid_scopes:
            self.errors.add_error(
                ErrorCode.E_POLICY_SCOPE_INVALID,
                ErrorCategory.POLICY,
                f"Invalid policy scope '{policy.scope}' for policy '{policy.name}'",
                policy.location,
                {"policy": policy.name, "scope": policy.scope},
                suggestion=f"Valid scopes are: {', '.join(valid_scopes)}"
            )
    
    def _validate_deviation(self, deviation: DeviationNode, context: str):
        """
        Validate a controlled deviation block (RFC-0001).
        
        Checks:
        - Scope is valid
        - Mode is valid
        - Bounds are defined (unbounded deviation is illegal)
        - Bounds are not ambiguous
        """
        if not deviation.scope:
            self.errors.add_error(
                ErrorCode.E_DEVIATION_OUT_OF_SCOPE,
                ErrorCategory.DEVIATION,
                f"Deviation in {context} must have a scope defined",
                deviation.location,
                {"context": context}
            )
        
        valid_scopes = {'steps', 'strategy', 'flow'}
        if deviation.scope not in valid_scopes:
            self.errors.add_error(
                ErrorCode.E_DEVIATION_OUT_OF_SCOPE,
                ErrorCategory.DEVIATION,
                f"Invalid deviation scope '{deviation.scope}' in {context}",
                deviation.location,
                {"context": context, "scope": deviation.scope},
                suggestion=f"Valid scopes are: {', '.join(valid_scopes)}"
            )
        
        # Check bounds (must not be empty)
        if not deviation.bounds:
            self.errors.add_error(
                ErrorCode.E_DEVIATION_UNBOUNDED,
                ErrorCategory.DEVIATION,
                f"Deviation in {context} must have bounds defined (unbounded deviation is illegal)",
                deviation.location,
                {"context": context},
                suggestion="Add explicit bounds to control the deviation"
            )
        
        # Check for ambiguous bounds (very basic check)
        for bound in deviation.bounds:
            if not bound or bound.strip() == "":
                self.errors.add_error(
                    ErrorCode.E_DEVIATION_AMBIGUOUS_BOUND,
                    ErrorCategory.DEVIATION,
                    f"Deviation in {context} has empty or ambiguous bound",
                    deviation.location,
                    {"context": context}
                )
    
    def _validate_step(self, step: StepNode, context: str):
        """
        Validate a step.
        
        Checks:
        - Step has an action
        - Substeps are valid
        """
        if not step.action or step.action.strip() == "":
            self.errors.add_error(
                ErrorCode.E_UNDECLARED_BEHAVIOR,
                ErrorCategory.STRICTNESS,
                f"Step in {context} has no action defined",
                step.location,
                {"context": context}
            )
        
        # Validate substeps recursively
        for substep in step.substeps:
            self._validate_step(substep, context)
    
    def _validate_constraint(self, constraint, context: str):
        """
        Validate a constraint or deviation.
        
        DeviationNode is validated separately, so we skip it here.
        """
        # Skip DeviationNode - it's validated by _validate_deviation
        if isinstance(constraint, DeviationNode):
            return
            
        # Validate ConstraintNode
        if not constraint.expression or constraint.expression.strip() == "":
            self.errors.add_error(
                ErrorCode.E_CONTRACT_VIOLATION,
                ErrorCategory.CONTRACT,
                f"Empty constraint in {context}",
                constraint.location,
                {"context": context}
            )
