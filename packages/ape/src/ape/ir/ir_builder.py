"""
Ape IR Builder

Transforms AST nodes into IR (Intermediate Representation) nodes.
The IR is used by the semantic validator and code generator.
"""

from typing import List
from ape.parser import ast_nodes as AST
from ape.compiler.ir_nodes import (
    ProjectNode, ModuleNode, EntityNode, TaskNode, FlowNode,
    PolicyNode, EnumNode, DeviationNode, FieldNode, StepNode,
    ConstraintNode, Location, DeviationMode
)



class IRBuilder:
    """
    Builds IR from AST.
    This is a scaffold implementation that will be extended.
    """
    
    def __init__(self):
        self.current_file = "<unknown>"
    
    def build_module(self, ast_module: AST.ModuleNode, filename: str = "<unknown>") -> ModuleNode:
        """
        Convert AST ModuleNode to IR ModuleNode.
        
        Args:
            ast_module: Parsed AST module
            filename: Source filename for location tracking
        
        Returns:
            IR ModuleNode
        """
        self.current_file = filename
        
        ir_module = ModuleNode(
            name=ast_module.name or filename,
            location=Location(filename, ast_module.line)
        )
        
        # Convert imports (handle new QualifiedIdentifierNode structure)
        for imp in ast_module.imports:
            if imp.qualified_name:
                # Use the module name (first part of qualified identifier)
                ir_module.imports.append(imp.module_name)
        
        # Convert entities
        for entity in ast_module.entities:
            ir_module.entities.append(self._build_entity(entity))
        
        # Convert enums
        for enum in ast_module.enums:
            ir_module.enums.append(self._build_enum(enum))
        
        # Convert tasks
        for task in ast_module.tasks:
            ir_module.tasks.append(self._build_task(task))
        
        # Convert flows
        for flow in ast_module.flows:
            ir_module.flows.append(self._build_flow(flow))
        
        # Convert policies
        for policy in ast_module.policies:
            ir_module.policies.append(self._build_policy(policy))
        
        return ir_module
    
    def _build_entity(self, ast_entity: AST.EntityDefNode) -> EntityNode:
        """Convert AST EntityDefNode to IR EntityNode"""
        return EntityNode(
            name=ast_entity.name,
            fields=[self._build_field(f) for f in ast_entity.fields],
            constraints=[self._build_constraint_or_deviation(c) for c in ast_entity.constraints],
            location=Location(self.current_file, ast_entity.line)
        )
    
    def _build_field(self, ast_field: AST.FieldDefNode) -> FieldNode:
        """Convert AST FieldDefNode to IR FieldNode"""
        return FieldNode(
            name=ast_field.name,
            type=ast_field.type_annotation.type_name if ast_field.type_annotation else "Any",
            optional=ast_field.type_annotation.is_optional if ast_field.type_annotation else False,
            default=ast_field.default_value,
            location=Location(self.current_file, ast_field.line)
        )
    
    def _build_enum(self, ast_enum: AST.EnumDefNode) -> EnumNode:
        """Convert AST EnumDefNode to IR EnumNode"""
        return EnumNode(
            name=ast_enum.name,
            values=ast_enum.values,
            location=Location(self.current_file, ast_enum.line)
        )
    
    def _build_task(self, ast_task: AST.TaskDefNode) -> TaskNode:
        """Convert AST TaskDefNode to IR TaskNode"""
        return TaskNode(
            name=ast_task.name,
            inputs=[self._build_field(f) for f in ast_task.inputs],
            outputs=[self._build_field(f) for f in ast_task.outputs],
            steps=[self._build_step(s) for s in ast_task.steps],
            constraints=[self._build_constraint_or_deviation(c) for c in ast_task.constraints],
            deviation=self._build_deviation(ast_task.deviation) if ast_task.deviation else None,
            location=Location(self.current_file, ast_task.line)
        )
    
    def _build_step(self, ast_step: AST.StepNode) -> StepNode:
        """Convert AST StepNode to IR StepNode"""
        return StepNode(
            action=ast_step.action,
            description=ast_step.description,
            substeps=[self._build_step(s) for s in ast_step.substeps],
            location=Location(self.current_file, ast_step.line)
        )
    
    def _build_constraint(self, ast_constraint: AST.ConstraintNode) -> ConstraintNode:
        """Convert AST ConstraintNode to IR ConstraintNode"""
        return ConstraintNode(
            expression=ast_constraint.expression,
            location=Location(self.current_file, ast_constraint.line)
        )
    
    def _build_constraint_or_deviation(self, ast_item):
        """Convert AST constraint or deviation to IR"""
        if isinstance(ast_item, AST.DeviationNode):
            return self._build_deviation(ast_item)
        elif isinstance(ast_item, AST.ConstraintNode):
            return self._build_constraint(ast_item)
        else:
            # Fallback for unknown types
            return self._build_constraint(ast_item)
    
    def _build_deviation(self, ast_deviation: AST.DeviationNode) -> DeviationNode:
        """Convert AST DeviationNode to IR DeviationNode"""
        return DeviationNode(
            scope=ast_deviation.scope,
            mode=DeviationMode(ast_deviation.mode),
            bounds=ast_deviation.bounds,
            rationale=ast_deviation.rationale,
            location=Location(self.current_file, ast_deviation.line)
        )
    
    def _build_flow(self, ast_flow: AST.FlowDefNode) -> FlowNode:
        """Convert AST FlowDefNode to IR FlowNode"""
        return FlowNode(
            name=ast_flow.name,
            steps=[self._build_step(s) for s in ast_flow.steps],
            constraints=[self._build_constraint_or_deviation(c) for c in ast_flow.constraints],
            deviation=self._build_deviation(ast_flow.deviation) if ast_flow.deviation else None,
            location=Location(self.current_file, ast_flow.line)
        )
    
    def _build_policy(self, ast_policy: AST.PolicyDefNode) -> PolicyNode:
        """Convert AST PolicyDefNode to IR PolicyNode"""
        return PolicyNode(
            name=ast_policy.name,
            rules=ast_policy.rules,
            scope=ast_policy.scope,
            location=Location(self.current_file, ast_policy.line)
        )
    
    def build_project(self, modules: List[ModuleNode], project_name: str = "ApeProject") -> ProjectNode:
        """
        Build a project IR from multiple modules.
        
        Args:
            modules: List of IR ModuleNodes
            project_name: Name of the project
        
        Returns:
            IR ProjectNode
        """
        project = ProjectNode(name=project_name)
        project.modules = modules
        
        # Collect global policies
        for module in modules:
            for policy in module.policies:
                if policy.scope == "global":
                    project.global_policies.append(policy)
        
        return project
