"""
Tests for ape_std/io.ape module

Verifies that the io module can be imported, parsed, linked, and compiled.
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


class TestIoModule(unittest.TestCase):
    """Test the io standard library module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Get the ape_std directory
        self.repo_root = Path(__file__).parent.parent.parent
        self.ape_std_dir = self.repo_root / "ape_std"
        self.io_module_path = self.ape_std_dir / "io.ape"
        
        self.assertTrue(self.io_module_path.exists(), 
                       f"io.ape not found at {self.io_module_path}")
    
    def test_io_module_exists(self):
        """Test that io.ape exists in ape_std/"""
        self.assertTrue(self.io_module_path.exists())
        self.assertTrue(self.io_module_path.is_file())
    
    def test_io_module_parses(self):
        """Test that io.ape can be parsed"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        self.assertEqual(ast.name, "io")
        self.assertTrue(len(ast.tasks) > 0, "io module should have tasks")
    
    def test_io_module_has_expected_functions(self):
        """Test that io module has the expected functions"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        task_names = [t.name for t in ast.tasks]
        
        # Check for I/O operations
        self.assertIn("read_line", task_names)
        self.assertIn("write_file", task_names)
        self.assertIn("read_file", task_names)
    
    def test_io_module_builds_ir(self):
        """Test that io module can be converted to IR"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "io.ape")
        
        self.assertEqual(ir_module.name, "io")
        self.assertTrue(len(ir_module.tasks) > 0)
    
    def test_io_module_generates_code(self):
        """Test that io module generates Python code"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "io.ape")
        
        project = ProjectNode(name="TestIo", modules=[ir_module])
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Check that functions are generated with proper name mangling
        self.assertIn("def io__read_line(", content)
        self.assertIn("def io__write_file(", content)
        self.assertIn("def io__read_file(", content)
    
    def test_io_read_line_signature(self):
        """Test that io.read_line has correct signature"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        read_line_task = next((t for t in ast.tasks if t.name == "read_line"), None)
        self.assertIsNotNone(read_line_task, "read_line task should exist")
        
        # Check inputs - should have prompt
        input_names = [f.name for f in read_line_task.inputs]
        self.assertIn("prompt", input_names)
        
        # Check outputs - should return line
        output_names = [f.name for f in read_line_task.outputs]
        self.assertIn("line", output_names)
    
    def test_io_write_file_signature(self):
        """Test that io.write_file has correct signature"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        write_file_task = next((t for t in ast.tasks if t.name == "write_file"), None)
        self.assertIsNotNone(write_file_task, "write_file task should exist")
        
        # Check inputs - should have path and content
        input_names = [f.name for f in write_file_task.inputs]
        self.assertIn("path", input_names)
        self.assertIn("content", input_names)
        
        # Check outputs - should have success
        self.assertTrue(len(write_file_task.outputs) > 0)
    
    def test_io_read_file_signature(self):
        """Test that io.read_file has correct signature"""
        source = self.io_module_path.read_text()
        ast = parse_ape_source(source, "io.ape")
        
        read_file_task = next((t for t in ast.tasks if t.name == "read_file"), None)
        self.assertIsNotNone(read_file_task, "read_file task should exist")
        
        # Check inputs - should have path
        input_names = [f.name for f in read_file_task.inputs]
        self.assertIn("path", input_names)
        
        # Check outputs - should return content
        output_names = [f.name for f in read_file_task.outputs]
        self.assertIn("content", output_names)


class TestIoImport(unittest.TestCase):
    """Test importing io module from user code"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
    
    def test_import_io_module(self):
        """Test that user code can import io module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.ape"
            test_file.write_text("""module test

import io

task save_data:
    inputs:
        path: String
        data: String
    outputs:
        success: Boolean

    constraints:
        - deterministic
    steps:
        - call io.write_file with path and data
        - return success
""")
            
            # Link the program
            linker = Linker()
            result = linker.link(test_file)
            
            # Verify io module was linked
            module_names = [m.module_name for m in result.modules]
            self.assertIn("io", module_names)
            self.assertIn("test", module_names)
    
    def test_io_module_compilation_pipeline(self):
        """Test complete compilation pipeline with io module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "use_io.ape"
            test_file.write_text("""module use_io

import io

task read_config:
    inputs:
        config_path: String
    outputs:
        config_data: String

    constraints:
        - deterministic
    steps:
        - call io.read_file with config_path
        - return config_data
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
                name="UseIo",
                modules=ir_modules
            )
            codegen = PythonCodeGenerator(project)
            files = codegen.generate()
            
            # Should generate files for both modules
            self.assertEqual(len(files), 2)
            
            # Check that io functions are available
            io_file = next((f for f in files if "io" in f.path), None)
            self.assertIsNotNone(io_file)
            self.assertIn("def io__read_line(", io_file.content)
            self.assertIn("def io__write_file(", io_file.content)
            self.assertIn("def io__read_file(", io_file.content)


class TestIoFunctionProperties(unittest.TestCase):
    """Test properties of io module functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.io_module_path = self.repo_root / "ape_std" / "io.ape"
        
        source = self.io_module_path.read_text()
        self.ast = parse_ape_source(source, "io.ape")
    
    def test_all_functions_are_deterministic(self):
        """Test that all io functions are marked deterministic"""
        for task in self.ast.tasks:
            # Check constraints
            has_deterministic = any(
                "deterministic" in str(c).lower() 
                for c in task.constraints
            )
            self.assertTrue(has_deterministic, 
                          f"Task {task.name} should be deterministic")
    
    def test_functions_have_valid_signatures(self):
        """Test that io functions have valid signatures"""
        for task in self.ast.tasks:
            # All tasks should have inputs and outputs
            self.assertTrue(len(task.inputs) > 0, 
                          f"{task.name} should have inputs")
            self.assertTrue(len(task.outputs) > 0, 
                          f"{task.name} should have outputs")
    
    def test_file_operations_have_path_parameter(self):
        """Test that file operations have path parameter"""
        file_ops = ["write_file", "read_file"]
        
        for op_name in file_ops:
            task = next((t for t in self.ast.tasks if t.name == op_name), None)
            if task:
                input_names = [f.name for f in task.inputs]
                self.assertIn("path", input_names, 
                            f"{op_name} should have path parameter")


class TestMultipleStdlibImports(unittest.TestCase):
    """Test importing multiple stdlib modules together"""
    
    def test_import_all_stdlib_modules(self):
        """Test that user code can import all stdlib modules"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_all.ape"
            test_file.write_text("""module test_all

import sys
import io
import math

task process:
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
            
            # Verify all modules were linked
            module_names = [m.module_name for m in result.modules]
            self.assertIn("sys", module_names)
            self.assertIn("io", module_names)
            self.assertIn("math", module_names)
            self.assertIn("test_all", module_names)


if __name__ == '__main__':
    unittest.main()
