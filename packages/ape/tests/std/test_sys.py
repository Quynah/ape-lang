"""
Tests for ape_std/sys.ape module

Verifies that the sys module can be imported, parsed, linked, and compiled.
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


class TestSysModule(unittest.TestCase):
    """Test the sys standard library module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Get the ape_std directory
        self.repo_root = Path(__file__).parent.parent.parent
        self.ape_std_dir = self.repo_root / "ape_std"
        self.sys_module_path = self.ape_std_dir / "sys.ape"
        
        self.assertTrue(self.sys_module_path.exists(), 
                       f"sys.ape not found at {self.sys_module_path}")
    
    def test_sys_module_exists(self):
        """Test that sys.ape exists in ape_std/"""
        self.assertTrue(self.sys_module_path.exists())
        self.assertTrue(self.sys_module_path.is_file())
    
    def test_sys_module_parses(self):
        """Test that sys.ape can be parsed"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        self.assertEqual(ast.name, "sys")
        self.assertTrue(len(ast.tasks) > 0, "sys module should have tasks")
    
    def test_sys_module_has_expected_functions(self):
        """Test that sys module has the expected functions"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        task_names = [t.name for t in ast.tasks]
        
        # Check for system operations
        self.assertIn("print", task_names)
        self.assertIn("exit", task_names)
    
    def test_sys_module_builds_ir(self):
        """Test that sys module can be converted to IR"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "sys.ape")
        
        self.assertEqual(ir_module.name, "sys")
        self.assertTrue(len(ir_module.tasks) > 0)
    
    def test_sys_module_generates_code(self):
        """Test that sys module generates Python code"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "sys.ape")
        
        project = ProjectNode(name="TestSys", modules=[ir_module])
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Check that functions are generated with proper name mangling
        self.assertIn("def sys__print(", content)
        self.assertIn("def sys__exit(", content)
    
    def test_sys_print_signature(self):
        """Test that sys.print has correct signature"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        print_task = next((t for t in ast.tasks if t.name == "print"), None)
        self.assertIsNotNone(print_task, "print task should exist")
        
        # Check inputs - should have message
        input_names = [f.name for f in print_task.inputs]
        self.assertIn("message", input_names)
        
        # Check outputs - should have success indicator
        self.assertTrue(len(print_task.outputs) > 0)
    
    def test_sys_exit_signature(self):
        """Test that sys.exit has correct signature"""
        source = self.sys_module_path.read_text()
        ast = parse_ape_source(source, "sys.ape")
        
        exit_task = next((t for t in ast.tasks if t.name == "exit"), None)
        self.assertIsNotNone(exit_task, "exit task should exist")
        
        # Check inputs - should have exit code
        input_names = [f.name for f in exit_task.inputs]
        self.assertIn("code", input_names)
        
        # Check outputs
        self.assertTrue(len(exit_task.outputs) > 0)


class TestSysImport(unittest.TestCase):
    """Test importing sys module from user code"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
    
    def test_import_sys_module(self):
        """Test that user code can import sys module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.ape"
            test_file.write_text("""module test

import sys

task greet:
    inputs:
        name: String
    outputs:
        success: Boolean

    constraints:
        - deterministic
    steps:
        - construct greeting from name
        - call sys.print with greeting
        - return success
""")
            
            # Link the program
            linker = Linker()
            result = linker.link(test_file)
            
            # Verify sys module was linked
            module_names = [m.module_name for m in result.modules]
            self.assertIn("sys", module_names)
            self.assertIn("test", module_names)
    
    def test_sys_module_compilation_pipeline(self):
        """Test complete compilation pipeline with sys module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "use_sys.ape"
            test_file.write_text("""module use_sys

import sys

task main:
    inputs:
        message: String
    outputs:
        done: Boolean

    constraints:
        - deterministic
    steps:
        - call sys.print with message
        - return done
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
                name="UseSys",
                modules=ir_modules
            )
            codegen = PythonCodeGenerator(project)
            files = codegen.generate()
            
            # Should generate files for both modules
            self.assertEqual(len(files), 2)
            
            # Check that sys functions are available
            sys_file = next((f for f in files if "sys" in f.path), None)
            self.assertIsNotNone(sys_file)
            self.assertIn("def sys__print(", sys_file.content)
            self.assertIn("def sys__exit(", sys_file.content)


class TestSysFunctionProperties(unittest.TestCase):
    """Test properties of sys module functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.sys_module_path = self.repo_root / "ape_std" / "sys.ape"
        
        source = self.sys_module_path.read_text()
        self.ast = parse_ape_source(source, "sys.ape")
    
    def test_all_functions_are_deterministic(self):
        """Test that all sys functions are marked deterministic"""
        for task in self.ast.tasks:
            # Check constraints
            has_deterministic = any(
                "deterministic" in str(c).lower() 
                for c in task.constraints
            )
            self.assertTrue(has_deterministic, 
                          f"Task {task.name} should be deterministic")
    
    def test_functions_have_valid_signatures(self):
        """Test that sys functions have valid signatures"""
        for task in self.ast.tasks:
            # All tasks should have inputs and outputs
            self.assertTrue(len(task.inputs) > 0, 
                          f"{task.name} should have inputs")
            self.assertTrue(len(task.outputs) > 0, 
                          f"{task.name} should have outputs")


if __name__ == '__main__':
    unittest.main()
