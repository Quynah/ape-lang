"""
Tests for calculator_basic.ape example

Verifies that the calculator module:
- Parses correctly
- Builds valid IR
- Passes semantic validation
- Passes strictness checks
- Generates valid Python code (optional)
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ape.tokenizer import Tokenizer
from ape.parser import Parser, parse_ape_source
from ape.ir import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.strictness_engine import StrictnessEngine
from ape.codegen.python_codegen import PythonCodeGenerator


def load_ape_source(name: str) -> str:
    """Load Ape source file from examples directory"""
    path = Path("examples") / name
    return path.read_text(encoding="utf-8")


def parse_to_ir(name: str):
    """Parse Ape source file to IR"""
    source = load_ape_source(name)
    
    # Parse to AST
    ast = parse_ape_source(source, name)
    
    # Build IR
    builder = IRBuilder()
    module_ir = builder.build_module(ast, name)
    
    return module_ir


class TestCalculatorBasic(unittest.TestCase):
    """Test suite for calculator_basic.ape example"""
    
    def test_parse_and_ir(self):
        """Test that calculator_basic.ape parses and builds valid IR"""
        module_ir = parse_to_ir("calculator_basic.ape")
        
        # Basic sanity checks
        self.assertIsNotNone(module_ir)
        self.assertEqual(module_ir.kind, "Module")
        
        # Check entities
        entity_names = [e.name for e in module_ir.entities]
        self.assertIn("CalculationRequest", entity_names)
        self.assertIn("CalculationResult", entity_names)
        
        # Check enum
        enum_names = [e.name for e in module_ir.enums]
        self.assertIn("Operation", enum_names)
        
        # Check task
        task_names = [t.name for t in module_ir.tasks]
        self.assertIn("calculate", task_names)
        
        # Check flow
        flow_names = [f.name for f in module_ir.flows]
        self.assertIn("calculator_demo", flow_names)
        
        # Verify Operation enum values
        operation_enum = next(e for e in module_ir.enums if e.name == "Operation")
        self.assertEqual(len(operation_enum.values), 4)
        self.assertIn("add", operation_enum.values)
        self.assertIn("subtract", operation_enum.values)
        self.assertIn("multiply", operation_enum.values)
        self.assertIn("divide", operation_enum.values)
        
        # Verify CalculationRequest fields
        calc_request = next(e for e in module_ir.entities if e.name == "CalculationRequest")
        field_names = [f.name for f in calc_request.fields]
        self.assertIn("left", field_names)
        self.assertIn("right", field_names)
        self.assertIn("op", field_names)
        
        # Verify CalculationResult fields
        calc_result = next(e for e in module_ir.entities if e.name == "CalculationResult")
        result_field_names = [f.name for f in calc_result.fields]
        self.assertIn("result", result_field_names)
        
        # Verify calculate task
        calc_task = next(t for t in module_ir.tasks if t.name == "calculate")
        self.assertEqual(len(calc_task.inputs), 1)
        self.assertEqual(calc_task.inputs[0].name, "request")
        self.assertEqual(len(calc_task.outputs), 1)
        self.assertEqual(calc_task.outputs[0].name, "result")
        self.assertGreater(len(calc_task.steps), 0)
    
    def test_semantic_and_strictness_valid(self):
        """Test that calculator_basic.ape passes semantic validation and strictness checks"""
        module_ir = parse_to_ir("calculator_basic.ape")
        
        # Wrap in ProjectNode
        project = ProjectNode(name="CalculatorExample", modules=[module_ir])
        
        # Run semantic validation
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        
        # Run strictness checks
        strict_engine = StrictnessEngine()
        strict_errors = strict_engine.enforce(project)
        
        # Combine all errors
        all_errors = list(semantic_errors) + list(strict_errors)
        
        # Assert no errors
        if all_errors:
            error_messages = [f"[{e.code.value}] {e.message}" for e in all_errors]
            self.fail(f"Expected no errors, got {len(all_errors)} error(s):\n" + 
                     "\n".join(error_messages))
        
        self.assertEqual(len(all_errors), 0, "Calculator example should have no validation errors")
    
    def test_codegen_calculator(self):
        """Test that calculator_basic.ape generates valid Python code"""
        module_ir = parse_to_ir("calculator_basic.ape")
        
        # Wrap in ProjectNode
        project = ProjectNode(name="CalculatorExample", modules=[module_ir])
        
        # Generate Python code
        gen = PythonCodeGenerator(project)
        files = gen.generate()
        
        # Should generate at least one file
        self.assertGreater(len(files), 0, "Should generate at least one file")
        
        # Find calculator file
        calc_files = [f for f in files if "calculator" in f.path.lower()]
        self.assertGreater(len(calc_files), 0, "Expected at least one generated file for calculator")
        
        # Check each generated file
        for file in calc_files:
            # Verify it's Python
            self.assertEqual(file.language, "python")
            
            # Verify basic content
            content = file.content
            self.assertIn("Operation", content)
            self.assertIn("CalculationRequest", content)
            self.assertIn("CalculationResult", content)
            self.assertIn("def calculate", content)
            self.assertIn("def calculator_demo", content)
            
            # Compile to verify syntax
            try:
                code = compile(content, file.path, "exec")
            except SyntaxError as e:
                self.fail(f"Generated code has syntax error in {file.path}: {e}\n\nCode:\n{content}")
            
            # Execute to verify it's valid Python
            # Add src/ to path so generated code can import ape.runtime
            import sys
            src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            exec_globals = {}
            exec(code, exec_globals, exec_globals)
            
            # Verify expected names exist
            self.assertIn("calculate", exec_globals, "calculate function should be in generated code")
            self.assertIn("calculator_demo", exec_globals, "calculator_demo function should be in generated code")
            self.assertIn("Operation", exec_globals, "Operation class should be in generated code")
            self.assertIn("CalculationRequest", exec_globals, "CalculationRequest class should be in generated code")
            self.assertIn("CalculationResult", exec_globals, "CalculationResult class should be in generated code")
    
    def test_calculator_deterministic_constraints(self):
        """Verify that calculator has deterministic constraints"""
        module_ir = parse_to_ir("calculator_basic.ape")
        
        # Check task constraints
        calc_task = next(t for t in module_ir.tasks if t.name == "calculate")
        constraint_texts = [c.expression for c in calc_task.constraints]
        self.assertIn("deterministic", constraint_texts, 
                     "calculate task should have deterministic constraint")
        
        # Check flow constraints
        calc_flow = next(f for f in module_ir.flows if f.name == "calculator_demo")
        flow_constraint_texts = [c.expression for c in calc_flow.constraints]
        self.assertIn("deterministic", flow_constraint_texts,
                     "calculator_demo flow should have deterministic constraint")
    
    def test_no_deviation_used(self):
        """Verify that calculator example uses no controlled deviation"""
        module_ir = parse_to_ir("calculator_basic.ape")
        
        # Check that no tasks have deviation
        for task in module_ir.tasks:
            self.assertIsNone(task.deviation, 
                            f"Task '{task.name}' should not have deviation")
        
        # Check that no flows have deviation
        for flow in module_ir.flows:
            self.assertIsNone(flow.deviation,
                            f"Flow '{flow.name}' should not have deviation")


class TestCalculatorIntegration(unittest.TestCase):
    """Integration tests for complete calculator pipeline"""
    
    def test_complete_pipeline(self):
        """Test complete pipeline: parse → validate → generate"""
        # Parse
        module_ir = parse_to_ir("calculator_basic.ape")
        project = ProjectNode(name="CalculatorExample", modules=[module_ir])
        
        # Validate
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        self.assertEqual(len(semantic_errors), 0)
        
        # Strictness
        engine = StrictnessEngine()
        strictness_errors = engine.enforce(project)
        self.assertEqual(len(strictness_errors), 0)
        
        # Generate
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        self.assertGreater(len(files), 0)
        
        # Verify generated code compiles
        for file in files:
            compile(file.content, file.path, "exec")
    
    def test_calculator_as_regression_test(self):
        """Use calculator as regression test for all components"""
        # This test ensures that any changes to parser, validator, or codegen
        # don't break the basic calculator example
        
        module_ir = parse_to_ir("calculator_basic.ape")
        project = ProjectNode(name="CalculatorExample", modules=[module_ir])
        
        # Should have exactly these components
        self.assertEqual(len(module_ir.entities), 2)
        self.assertEqual(len(module_ir.enums), 1)
        self.assertEqual(len(module_ir.tasks), 1)
        self.assertEqual(len(module_ir.flows), 1)
        self.assertEqual(len(module_ir.policies), 0)
        
        # All validation should pass
        validator = SemanticValidator()
        engine = StrictnessEngine()
        
        all_errors = (validator.validate_project(project) + 
                     engine.enforce(project))
        
        self.assertEqual(len(all_errors), 0, 
                        "Calculator regression test failed - basic example has errors")


if __name__ == '__main__':
    unittest.main()
