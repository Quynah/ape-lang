"""
Tests for Controlled Deviation System (CDS) semantic validation
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ape.compiler.ir_nodes import (
    ModuleNode, TaskNode, DeviationNode, DeviationMode,
    FieldNode, StepNode, Location, ProjectNode
)
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.errors import ErrorCode


def create_task_with_deviation(deviation: DeviationNode) -> TaskNode:
    """Helper to create a task with a deviation in constraints"""
    return TaskNode(
        name="test_task",
        inputs=[FieldNode(name="input", type="String", optional=False, location=Location("test", 1))],
        outputs=[FieldNode(name="output", type="String", optional=False, location=Location("test", 1))],
        steps=[StepNode(action="process", description="Process input", substeps=[], location=Location("test", 1))],
        constraints=[deviation],
        deviation=None,
        location=Location("test", 1)
    )


class TestDeviationValidation:
    """Tests for DeviationNode semantic validation"""
    
    def test_valid_deviation_steps_creative(self):
        """Test that a valid deviation with scope=steps and mode=creative passes validation"""
        deviation = DeviationNode(
            scope="steps",
            mode=DeviationMode.CREATIVE,
            bounds=[
                "output must be a valid string",
                "output must relate to input",
                "no side effects"
            ],
            rationale="Testing creative deviation",
            location=Location("test", 1)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        # Should have no errors
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"
    
    def test_valid_deviation_strategy_semantic_choice(self):
        """Test that deviation with scope=strategy and mode=semantic_choice is valid"""
        deviation = DeviationNode(
            scope="strategy",
            mode=DeviationMode.SEMANTIC_CHOICE,
            bounds=["must choose valid approach", "must be efficient"],
            rationale="Multiple valid approaches exist",
            location=Location("test", 1)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"
    
    def test_valid_deviation_flow_fuzzy_goal(self):
        """Test that deviation with scope=flow and mode=fuzzy_goal is valid"""
        deviation = DeviationNode(
            scope="flow",
            mode=DeviationMode.FUZZY_GOAL,
            bounds=["outcome must satisfy user intent"],
            rationale="Goal is subjective",
            location=Location("test", 1)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        assert len(errors) == 0
    
    def test_invalid_scope(self):
        """Test that invalid scope triggers E_DEVIATION_OUT_OF_SCOPE"""
        deviation = DeviationNode(
            scope="invalid_scope",
            mode=DeviationMode.CREATIVE,
            bounds=["some bound"],
            rationale="Testing invalid scope",
            location=Location("test", 10)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        # Should have E_DEVIATION_OUT_OF_SCOPE error
        assert len(errors) > 0
        assert any(e.code == ErrorCode.E_DEVIATION_OUT_OF_SCOPE for e in errors)
    
    def test_empty_bounds(self):
        """Test that empty bounds triggers E_DEVIATION_UNBOUNDED"""
        deviation = DeviationNode(
            scope="steps",
            mode=DeviationMode.CREATIVE,
            bounds=[],
            rationale="Testing empty bounds",
            location=Location("test", 10)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        # Should have E_DEVIATION_UNBOUNDED error
        assert len(errors) > 0
        assert any(e.code == ErrorCode.E_DEVIATION_UNBOUNDED for e in errors)
    
    def test_missing_rationale_is_allowed(self):
        """Test that missing rationale is allowed (it's optional)"""
        deviation = DeviationNode(
            scope="steps",
            mode=DeviationMode.CREATIVE,
            bounds=["output must be valid"],
            rationale=None,
            location=Location("test", 1)
        )
        
        task = create_task_with_deviation(deviation)
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        # Should pass - rationale is optional
        assert len(errors) == 0
    
    def test_multiple_valid_deviations(self):
        """Test that a task can have multiple deviation nodes"""
        dev1 = DeviationNode(
            scope="steps",
            mode=DeviationMode.CREATIVE,
            bounds=["bound1"],
            rationale="First deviation",
            location=Location("test", 1)
        )
        dev2 = DeviationNode(
            scope="strategy",
            mode=DeviationMode.SEMANTIC_CHOICE,
            bounds=["bound2"],
            rationale="Second deviation",
            location=Location("test", 2)
        )
        
        task = TaskNode(
            name="test_task",
            inputs=[],
            outputs=[],
            steps=[StepNode(action="do", description="Do something", substeps=[], location=Location("test", 1))],
            constraints=[dev1, dev2],
            deviation=None,
            location=Location("test", 1)
        )
        
        module = ModuleNode(name="TestModule", location=Location("test", 1))
        module.tasks.append(task)
        
        project = ProjectNode(name="TestProject", modules=[module])
        validator = SemanticValidator()
        errors = validator.validate_project(project)
        
        # Both deviations should be valid
        assert len(errors) == 0
