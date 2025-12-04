"""
Tests for ape_std/math.ape module

Verifies that the math module can be imported, parsed, linked, and compiled.
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ape.parser import parse_ape_source
from ape.ir import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.codegen.python_codegen import PythonCodeGenerator
from ape.linker import Linker


class TestMathModule(unittest.TestCase):
    """Test the math standard library module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Get the ape_std directory
        self.repo_root = Path(__file__).parent.parent.parent
        self.ape_std_dir = self.repo_root / "ape_std"
        self.math_module_path = self.ape_std_dir / "math.ape"
        
        self.assertTrue(self.math_module_path.exists(), 
                       f"math.ape not found at {self.math_module_path}")
    
    def test_math_module_exists(self):
        """Test that math.ape exists in ape_std/"""
        self.assertTrue(self.math_module_path.exists())
        self.assertTrue(self.math_module_path.is_file())
    
    def test_math_module_parses(self):
        """Test that math.ape can be parsed"""
        source = self.math_module_path.read_text()
        ast = parse_ape_source(source, "math.ape")
        
        self.assertEqual(ast.name, "math")
        self.assertTrue(len(ast.tasks) > 0, "math module should have tasks")
    
    def test_math_module_has_expected_functions(self):
        """Test that math module has the expected functions"""
        source = self.math_module_path.read_text()
        ast = parse_ape_source(source, "math.ape")
        
        task_names = [t.name for t in ast.tasks]
        
        # Check for basic arithmetic operations
        self.assertIn("add", task_names)
        self.assertIn("subtract", task_names)
        self.assertIn("multiply", task_names)
        self.assertIn("divide", task_names)
    
    def test_math_module_builds_ir(self):
        """Test that math module can be converted to IR"""
        source = self.math_module_path.read_text()
        ast = parse_ape_source(source, "math.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "math.ape")
        
        self.assertEqual(ir_module.name, "math")
        self.assertTrue(len(ir_module.tasks) > 0)
    
    def test_math_module_generates_code(self):
        """Test that math module generates Python code"""
        source = self.math_module_path.read_text()
        ast = parse_ape_source(source, "math.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "math.ape")
        
        project = ProjectNode(name="TestMath", modules=[ir_module])
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Check that functions are generated with proper name mangling
        self.assertIn("def math__add(", content)
        self.assertIn("def math__subtract(", content)
        self.assertIn("def math__multiply(", content)
        self.assertIn("def math__divide(", content)
    
    def test_math_add_signature(self):
        """Test that math.add has correct signature"""
        source = self.math_module_path.read_text()
        ast = parse_ape_source(source, "math.ape")
        
        add_task = next((t for t in ast.tasks if t.name == "add"), None)
        self.assertIsNotNone(add_task, "add task should exist")
        
        # Check inputs
        self.assertEqual(len(add_task.inputs), 2)
        input_names = [f.name for f in add_task.inputs]
        self.assertIn("a", input_names)
        self.assertIn("b", input_names)
        
        # Check outputs
        self.assertTrue(len(add_task.outputs) > 0, "add should have outputs")


class TestMathImport(unittest.TestCase):
    """Test importing math module from user code"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.temp_dir = None
    
    def tearDown(self):
        """Clean up temporary files"""
        # Temp directory will be cleaned up automatically
        pass
    
    def test_import_math_module(self):
        """Test that user code can import math module"""
        # Create a temporary Ape file that imports math
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.ape"
            test_file.write_text("""module test

import math

task calculate:
    inputs:
        x: Integer
        y: Integer
    outputs:
        result: Integer

    constraints:
        - deterministic
    steps:
        - call math.add with x and y
        - return result
""")
            
            # Link the program
            linker = Linker()
            result = linker.link(test_file)
            
            # Verify math module was linked
            module_names = [m.module_name for m in result.modules]
            self.assertIn("math", module_names)
            self.assertIn("test", module_names)
    
    def test_math_module_compilation_pipeline(self):
        """Test complete compilation pipeline with math module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "use_math.ape"
            test_file.write_text("""module use_math

import math

task sum_three:
    inputs:
        a: Integer
        b: Integer
        c: Integer
    outputs:
        result: Integer

    constraints:
        - deterministic
    steps:
        - add a and b to get temp
        - add temp and c to get result
        - return result
""")
            
            # Parse and link
            linker = Linker()
            linked_program = linker.link(test_file)
            
            # Build IR from AST modules
            builder = IRBuilder()
            ir_modules = []
            for resolved_module in linked_program.modules:
                ir_module = builder.build_module(
                    resolved_module.ast,
                    str(resolved_module.file_path)
                )
                ir_modules.append(ir_module)
            
            # Generate code
            project = ProjectNode(
                name="UseMath",
                modules=ir_modules
            )
            codegen = PythonCodeGenerator(project)
            files = codegen.generate()
            
            # Should generate files for both modules
            self.assertEqual(len(files), 2)
            
            # Check that math functions are available
            math_file = next((f for f in files if "math" in f.path), None)
            self.assertIsNotNone(math_file)
            self.assertIn("def math__add(", math_file.content)


class TestMathFunctionProperties(unittest.TestCase):
    """Test properties of math module functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.math_module_path = self.repo_root / "ape_std" / "math.ape"
        
        source = self.math_module_path.read_text()
        self.ast = parse_ape_source(source, "math.ape")
    
    def test_all_functions_are_deterministic(self):
        """Test that all math functions are marked deterministic"""
        for task in self.ast.tasks:
            # Check constraints
            has_deterministic = any(
                "deterministic" in str(c).lower() 
                for c in task.constraints
            )
            self.assertTrue(has_deterministic, 
                          f"Task {task.name} should be deterministic")
    
    def test_arithmetic_functions_have_two_inputs(self):
        """Test that basic arithmetic functions have two integer inputs"""
        binary_ops = ["add", "subtract", "multiply", "divide"]
        
        for op_name in binary_ops:
            task = next((t for t in self.ast.tasks if t.name == op_name), None)
            if task:  # Only test if the function exists
                self.assertEqual(len(task.inputs), 2, 
                               f"{op_name} should have 2 inputs")
                
                # Check that inputs are integers
                for inp in task.inputs:
                    type_name = inp.type_annotation.type_name if inp.type_annotation else "Unknown"
                    self.assertIn("Integer", type_name, 
                                f"{op_name} input should be Integer")


if __name__ == '__main__':
    unittest.main()
