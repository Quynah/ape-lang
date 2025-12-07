"""
Tests for v0.2.0 module system examples

Verifies that the new examples demonstrating modules, imports, and stdlib
compile correctly and remain valid as the language evolves.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ape.parser import parse_ape_source
from ape.ir import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.codegen.python_codegen import PythonCodeGenerator
from ape.linker import Linker


class TestHelloImportsExample(unittest.TestCase):
    """Test the hello_imports.ape example"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.example_path = self.repo_root / "examples" / "hello_imports.ape"
        
        self.assertTrue(self.example_path.exists(), 
                       f"Example not found at {self.example_path}")
    
    def test_example_exists(self):
        """Test that hello_imports.ape exists"""
        self.assertTrue(self.example_path.exists())
        self.assertTrue(self.example_path.is_file())
    
    def test_example_parses(self):
        """Test that hello_imports.ape can be parsed"""
        source = self.example_path.read_text()
        ast = parse_ape_source(source, "hello_imports.ape")
        
        self.assertEqual(ast.name, "main")
        self.assertTrue(len(ast.imports) > 0, "Should have imports")
    
    def test_example_has_expected_imports(self):
        """Test that example imports sys and math"""
        source = self.example_path.read_text()
        ast = parse_ape_source(source, "hello_imports.ape")
        
        import_names = [imp.qualified_name.parts[0] for imp in ast.imports]
        self.assertIn("sys", import_names)
        self.assertIn("math", import_names)
    
    def test_example_links_successfully(self):
        """Test that example can be linked"""
        linker = Linker()
        result = linker.link(self.example_path)
        
        # Should link main + stdlib modules
        module_names = [m.module_name for m in result.modules]
        self.assertIn("main", module_names)
        self.assertIn("sys", module_names)
        self.assertIn("math", module_names)
    
    def test_example_compiles_to_python(self):
        """Test complete compilation pipeline"""
        # Link
        linker = Linker()
        linked_program = linker.link(self.example_path)
        
        # Build IR
        builder = IRBuilder()
        ir_modules = []
        for resolved_module in linked_program.modules:
            ir_module = builder.build_module(
                resolved_module.ast,
                str(resolved_module.file_path)
            )
            ir_modules.append(ir_module)
        
        # Generate code
        project = ProjectNode(name="HelloImports", modules=ir_modules)
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        # Should generate main + stdlib modules
        self.assertTrue(len(files) >= 3)
        
        # Check that stdlib functions are properly mangled
        all_content = "\n".join(f.content for f in files)
        self.assertIn("def sys__print(", all_content)
        self.assertIn("def math__add(", all_content)


class TestStdlibCompleteExample(unittest.TestCase):
    """Test the stdlib_complete.ape example"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.example_path = self.repo_root / "examples" / "stdlib_complete.ape"
        
        self.assertTrue(self.example_path.exists(), 
                       f"Example not found at {self.example_path}")
    
    def test_example_uses_all_stdlib_modules(self):
        """Test that example imports all three stdlib modules"""
        source = self.example_path.read_text()
        ast = parse_ape_source(source, "stdlib_complete.ape")
        
        import_names = [imp.qualified_name.parts[0] for imp in ast.imports]
        self.assertIn("sys", import_names)
        self.assertIn("io", import_names)
        self.assertIn("math", import_names)
    
    def test_example_links_all_modules(self):
        """Test that all stdlib modules are linked"""
        linker = Linker()
        result = linker.link(self.example_path)
        
        module_names = [m.module_name for m in result.modules]
        self.assertIn("sys", module_names)
        self.assertIn("io", module_names)
        self.assertIn("math", module_names)
        self.assertIn("file_processor", module_names)
    
    def test_example_compiles(self):
        """Test that example compiles successfully"""
        linker = Linker()
        linked_program = linker.link(self.example_path)
        
        builder = IRBuilder()
        ir_modules = []
        for resolved_module in linked_program.modules:
            ir_module = builder.build_module(
                resolved_module.ast,
                str(resolved_module.file_path)
            )
            ir_modules.append(ir_module)
        
        project = ProjectNode(name="StdlibComplete", modules=ir_modules)
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        # Should generate all modules
        self.assertTrue(len(files) >= 4)
        
        # Check all stdlib functions are present
        all_content = "\n".join(f.content for f in files)
        self.assertIn("def sys__print(", all_content)
        self.assertIn("def io__read_file(", all_content)
        self.assertIn("def io__write_file(", all_content)
        self.assertIn("def math__multiply(", all_content)


class TestCustomLibProjectExample(unittest.TestCase):
    """Test the custom_lib_project example"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.project_dir = self.repo_root / "examples" / "custom_lib_project"
        self.main_path = self.project_dir / "main.ape"
        self.lib_path = self.project_dir / "lib" / "tools.ape"
        
        self.assertTrue(self.main_path.exists(), 
                       f"Main not found at {self.main_path}")
        self.assertTrue(self.lib_path.exists(), 
                       f"Library not found at {self.lib_path}")
    
    def test_project_structure(self):
        """Test that project has correct structure"""
        self.assertTrue(self.project_dir.is_dir())
        self.assertTrue(self.main_path.is_file())
        self.assertTrue((self.project_dir / "lib").is_dir())
        self.assertTrue(self.lib_path.is_file())
    
    def test_main_imports_local_library(self):
        """Test that main.ape imports tools module"""
        source = self.main_path.read_text()
        ast = parse_ape_source(source, "main.ape")
        
        import_names = [imp.qualified_name.parts[0] for imp in ast.imports]
        self.assertIn("tools", import_names)
    
    def test_library_module_parses(self):
        """Test that tools.ape parses correctly"""
        source = self.lib_path.read_text()
        ast = parse_ape_source(source, "tools.ape")
        
        self.assertEqual(ast.name, "tools")
        self.assertTrue(len(ast.tasks) > 0)
    
    def test_linker_resolves_from_lib_folder(self):
        """Test that linker finds tools module in lib/ folder"""
        linker = Linker()
        result = linker.link(self.main_path)
        
        module_names = [m.module_name for m in result.modules]
        self.assertIn("tools", module_names, 
                     "Linker should resolve tools from lib/ folder")
        self.assertIn("main", module_names)
        self.assertIn("sys", module_names)
    
    def test_project_compiles(self):
        """Test that entire project compiles successfully"""
        linker = Linker()
        linked_program = linker.link(self.main_path)
        
        builder = IRBuilder()
        ir_modules = []
        for resolved_module in linked_program.modules:
            ir_module = builder.build_module(
                resolved_module.ast,
                str(resolved_module.file_path)
            )
            ir_modules.append(ir_module)
        
        project = ProjectNode(name="CustomLibProject", modules=ir_modules)
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        # Should generate main, tools, and stdlib modules
        self.assertTrue(len(files) >= 3)
        
        # Check that tools functions are mangled
        all_content = "\n".join(f.content for f in files)
        self.assertIn("def tools__", all_content)


class TestExamplesIntegration(unittest.TestCase):
    """Integration tests for all new examples"""
    
    def test_all_examples_exist(self):
        """Test that all documented examples exist"""
        repo_root = Path(__file__).parent.parent.parent
        examples_dir = repo_root / "examples"
        
        # Check individual files
        self.assertTrue((examples_dir / "hello_imports.ape").exists())
        self.assertTrue((examples_dir / "stdlib_complete.ape").exists())
        
        # Check custom_lib_project structure
        self.assertTrue((examples_dir / "custom_lib_project").is_dir())
        self.assertTrue((examples_dir / "custom_lib_project" / "main.ape").exists())
        self.assertTrue((examples_dir / "custom_lib_project" / "lib" / "tools.ape").exists())
    
    def test_all_examples_are_valid_ape(self):
        """Test that all examples parse without errors"""
        repo_root = Path(__file__).parent.parent.parent
        
        examples = [
            repo_root / "examples" / "hello_imports.ape",
            repo_root / "examples" / "stdlib_complete.ape",
            repo_root / "examples" / "custom_lib_project" / "main.ape",
            repo_root / "examples" / "custom_lib_project" / "lib" / "tools.ape",
        ]
        
        for example_path in examples:
            with self.subTest(example=example_path.name):
                source = example_path.read_text()
                ast = parse_ape_source(source, example_path.name)
                self.assertIsNotNone(ast)


if __name__ == '__main__':
    unittest.main()
