"""
Tests for email_policy_basic.ape example

Verifies that the email policy module:
- Parses correctly
- Builds valid IR
- Passes semantic validation
- Passes strictness checks
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ape.parser.parser import parse_ape_source
from ape.ir import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.strictness_engine import StrictnessEngine


def load_ape_source(name: str) -> str:
    """Load an Ape source file from examples/"""
    path = Path("examples") / name
    return path.read_text(encoding="utf-8")


def parse_to_ir(name: str):
    """Parse an Ape source file and return the IR module"""
    source = load_ape_source(name)
    
    # Parse to AST
    ast = parse_ape_source(source, name)
    
    # Build IR
    builder = IRBuilder()
    module_ir = builder.build_module(ast, name)
    
    return module_ir


class TestEmailPolicyBasic:
    """Tests for email_policy_basic.ape parsing and IR structure"""
    
    def test_parse_and_ir(self):
        """Test that email_policy_basic.ape parses and builds IR correctly"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        assert module_ir is not None
        assert module_ir.name == "email_policy_basic.ape"
        
        # Check entities
        entity_names = [e.name for e in module_ir.entities]
        assert "Email" in entity_names, "Expected Email entity"
        assert "EmailAssessment" in entity_names, "Expected EmailAssessment entity"
        
        # Check enum
        enum_names = [e.name for e in module_ir.enums]
        assert "ThreatLevel" in enum_names, "Expected ThreatLevel enum"
        
        # Check task
        task_names = [t.name for t in module_ir.tasks]
        assert "assess_email" in task_names, "Expected assess_email task"
        
        # Check policy
        policy_names = [p.name for p in module_ir.policies]
        assert "email_threat_policy" in policy_names, "Expected email_threat_policy"
    
    def test_entity_fields_correct(self):
        """Test that entity fields are correctly parsed"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        # Find Email entity
        email = next((e for e in module_ir.entities if e.name == "Email"), None)
        assert email is not None, "Email entity not found"
        
        field_names = [f.name for f in email.fields]
        assert "from_domain" in field_names
        assert "subject" in field_names
        assert "body" in field_names
        
        # Find EmailAssessment entity
        assessment = next((e for e in module_ir.entities if e.name == "EmailAssessment"), None)
        assert assessment is not None, "EmailAssessment entity not found"
        
        field_names = [f.name for f in assessment.fields]
        assert "email" in field_names
        assert "level" in field_names
        assert "reason" in field_names
    
    def test_enum_values(self):
        """Test that ThreatLevel enum has correct values"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        threat_level = next((e for e in module_ir.enums if e.name == "ThreatLevel"), None)
        assert threat_level is not None, "ThreatLevel enum not found"
        
        assert "LOW" in threat_level.values
        assert "MEDIUM" in threat_level.values
        assert "HIGH" in threat_level.values
        assert len(threat_level.values) == 3
    
    def test_task_structure(self):
        """Test that assess_email task has correct structure"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        task = next((t for t in module_ir.tasks if t.name == "assess_email"), None)
        assert task is not None, "assess_email task not found"
        
        # Check inputs
        assert len(task.inputs) == 1
        assert task.inputs[0].name == "email"
        assert task.inputs[0].type == "Email"
        
        # Check outputs
        assert len(task.outputs) == 1
        assert task.outputs[0].name == "assessment"
        assert task.outputs[0].type == "EmailAssessment"
        
        # Check constraints
        assert len(task.constraints) > 0
        
        # Check steps
        assert len(task.steps) > 0
    
    def test_policy_structure(self):
        """Test that email_threat_policy has correct structure"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        policy = next((p for p in module_ir.policies if p.name == "email_threat_policy"), None)
        assert policy is not None, "email_threat_policy not found"
        
        assert policy.scope == "global"
        assert len(policy.rules) > 0
        
        # Check that rules mention key concepts
        rules_text = " ".join(policy.rules).lower()
        assert "trusted" in rules_text or "safelist" in rules_text
        assert "high" in rules_text
        assert "quarantine" in rules_text or "review" in rules_text
    
    def test_semantic_and_strictness_valid(self):
        """Test that email_policy_basic.ape passes semantic validation and strictness checks"""
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        # Wrap in ProjectNode
        project = ProjectNode(name="EmailPolicyExample", modules=[module_ir])
        
        # Semantic validation
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        
        assert len(semantic_errors) == 0, \
            f"Expected no semantic errors, got: {[str(e) for e in semantic_errors]}"
        
        # Strictness validation
        engine = StrictnessEngine()
        strictness_errors = engine.enforce(project)
        
        assert len(strictness_errors) == 0, \
            f"Expected no strictness errors, got: {[str(e) for e in strictness_errors]}"


class TestEmailPolicyIntegration:
    """Integration tests for email policy example"""
    
    def test_full_pipeline_no_errors(self):
        """Test the complete parse → validate → strictness pipeline"""
        # Parse
        module_ir = parse_to_ir("email_policy_basic.ape")
        
        # Wrap in ProjectNode
        project = ProjectNode(name="EmailPolicyExample", modules=[module_ir])
        
        # Validate
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        
        # Strictness
        engine = StrictnessEngine()
        strictness_errors = engine.enforce(project)
        
        # Both should pass
        all_errors = list(semantic_errors) + list(strictness_errors)
        assert len(all_errors) == 0, \
            f"Pipeline should have no errors, got: {[str(e) for e in all_errors]}"
