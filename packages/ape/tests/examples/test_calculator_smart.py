"""
Tests for calculator_smart.ape example
Demonstrates Controlled Deviation System (CDS) in Ape
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ape.parser import Parser, parse_ape_source
from ape.ir import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.strictness_engine import StrictnessEngine
from ape.codegen.python_codegen import PythonCodeGenerator


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


class TestCalculatorSmart:
    """Tests for calculator_smart.ape parsing and IR structure"""

    def test_parse_and_ir(self):
        """Test that calculator_smart.ape parses correctly with all expected declarations"""
        module_ir = parse_to_ir("calculator_smart.ape")

        # Check entities
        entity_names = [e.name for e in module_ir.entities]
        assert "CalculationRequest" in entity_names, \
            f"Expected entity 'CalculationRequest', got {entity_names}"
        assert "CalculationResult" in entity_names, \
            f"Expected entity 'CalculationResult', got {entity_names}"

        # Check enum
        enum_names = [e.name for e in module_ir.enums]
        assert "Operation" in enum_names, \
            f"Expected enum 'Operation', got {enum_names}"

        # Check task
        task_names = [t.name for t in module_ir.tasks]
        assert "calculate_smart" in task_names, \
            f"Expected task 'calculate_smart', got {task_names}"

        # Check flow
        flow_names = [f.name for f in module_ir.flows]
        assert "calculator_smart_demo" in flow_names, \
            f"Expected flow 'calculator_smart_demo', got {flow_names}"

    def test_entity_fields_correct(self):
        """Test that CalculationRequest and CalculationResult have correct fields"""
        module_ir = parse_to_ir("calculator_smart.ape")

        # Find CalculationResult entity
        result_entity = next((e for e in module_ir.entities if e.name == "CalculationResult"), None)
        assert result_entity is not None, "CalculationResult entity not found"

        # Check fields
        field_names = [f.name for f in result_entity.fields]
        assert "left" in field_names, "CalculationResult should have 'left' field"
        assert "right" in field_names, "CalculationResult should have 'right' field"
        assert "op" in field_names, "CalculationResult should have 'op' field"
        assert "result" in field_names, "CalculationResult should have 'result' field"
        assert "summary" in field_names, "CalculationResult should have 'summary' field"

    def test_semantic_and_strictness_valid(self):
        """Test that calculator_smart.ape passes semantic validation and strictness checks"""
        module_ir = parse_to_ir("calculator_smart.ape")

        # Wrap in ProjectNode
        project = ProjectNode(name="CalculatorSmartExample", modules=[module_ir])

        # Semantic validation
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)

        # Strictness enforcement
        strict = StrictnessEngine()
        strict_errors = strict.enforce(project)

        # Combine all errors
        all_errors = list(semantic_errors) + list(strict_errors)
        
        if all_errors:
            error_msgs = [f"{e.code.value}: {e.message}" for e in all_errors]
            assert False, f"Expected no errors, got {len(all_errors)} errors:\n" + "\n".join(error_msgs)

    def test_deviation_used_with_bounds(self):
        """Test that calculate_smart task has DeviationNode in IR with proper bounds"""
        module_ir = parse_to_ir("calculator_smart.ape")

        # Find the calculate_smart task
        task = next((t for t in module_ir.tasks if t.name == "calculate_smart"), None)
        assert task is not None, "Task 'calculate_smart' not found"

        # Find deviation constraint in IR (should be DeviationNode now)
        from ape.compiler.ir_nodes import DeviationNode
        deviation_nodes = [
            c for c in task.constraints
            if isinstance(c, DeviationNode)
        ]
        assert deviation_nodes, "Expected a DeviationNode in calculate_smart constraints"
        dev = deviation_nodes[0]

        # Verify deviation properties
        assert dev.scope == "steps", f"Expected scope='steps', got '{dev.scope}'"
        assert str(dev.mode) == "DeviationMode.CREATIVE" or dev.mode.value == "creative", \
            f"Expected mode='creative', got '{dev.mode}'"
        assert dev.bounds, "Deviation bounds must not be empty"
        assert len(dev.bounds) >= 3, \
            f"Expected at least 3 bounds, got {len(dev.bounds)}"
        
        # Check that bounds mention key constraints
        bounds_text = " ".join(dev.bounds).lower()
        assert "result" in bounds_text or "mathematically correct" in bounds_text, \
            "Bounds should mention result or mathematical correctness"
        assert "summary" in bounds_text, "Bounds should mention 'summary'"

    def test_deviation_rationale_exists(self):
        """Test that deviation has a rationale explaining why it's needed"""
        module_ir = parse_to_ir("calculator_smart.ape")

        # Find the calculate_smart task
        task = next((t for t in module_ir.tasks if t.name == "calculate_smart"), None)
        assert task is not None, "Task 'calculate_smart' not found"

        # Find deviation with rationale
        from ape.compiler.ir_nodes import DeviationNode
        deviation_nodes = [
            c for c in task.constraints
            if isinstance(c, DeviationNode)
        ]
        assert deviation_nodes, "Expected a DeviationNode"
        dev = deviation_nodes[0]

        assert dev.rationale, "Deviation should have a rationale"
        # Rationale includes the quotes in the string
        assert len(dev.rationale) > 10, \
            f"Rationale should be descriptive, got: '{dev.rationale}'"


class TestCalculatorSmartIntegration:
    """Integration tests for the complete calculator_smart pipeline"""

    def test_full_pipeline_no_errors(self):
        """Test the complete parse → validate → strictness → codegen pipeline"""
        # Parse
        module_ir = parse_to_ir("calculator_smart.ape")

        # Wrap in ProjectNode
        project = ProjectNode(name="CalculatorSmartExample", modules=[module_ir])

        # Validate
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        assert not list(semantic_errors), \
            f"Semantic validation failed: {list(semantic_errors)}"

        # Strictness
        strict = StrictnessEngine()
        strict_errors = strict.enforce(project)
        assert not list(strict_errors), \
            f"Strictness enforcement failed: {list(strict_errors)}"

        # Codegen
        codegen = PythonCodeGenerator(project)
        generated_files = codegen.generate()
        
        assert generated_files, "Expected generated files from codegen"
        assert len(generated_files) > 0, "Expected at least one generated file"

        # Verify generated Python compiles
        py_file = generated_files[0]
        assert py_file.language == "python", \
            f"Expected language='python', got '{py_file.language}'"
        
        try:
            compile(py_file.content, py_file.path, 'exec')
        except SyntaxError as e:
            assert False, f"Generated Python has syntax error: {e}"

    def test_generated_code_has_deviation_constructs(self):
        """Test that generated Python code includes deviation-related constructs"""
        module_ir = parse_to_ir("calculator_smart.ape")
        
        # Wrap in ProjectNode
        project = ProjectNode(name="CalculatorSmartExample", modules=[module_ir])
        
        codegen = PythonCodeGenerator(project)
        generated_files = codegen.generate()
        
        assert generated_files, "Expected generated files"
        py_content = generated_files[0].content

        # Check for expected constructs in generated code
        assert "calculate_smart" in py_content, \
            "Generated code should contain calculate_smart function"
        assert "CalculationResult" in py_content, \
            "Generated code should contain CalculationResult class"
        assert "summary" in py_content, \
            "Generated code should handle summary field"
        
        # Verify the code is compilable Python
        try:
            compile(py_content, "<generated>", 'exec')
        except SyntaxError as e:
            assert False, f"Generated code has syntax errors: {e}"
