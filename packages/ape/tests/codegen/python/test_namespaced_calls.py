"""
Unit tests for Python Code Generator - Namespaced/Module-Qualified Calls

Tests the Ape v0.2.0 module system codegen with deterministic name mangling.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ape.codegen.python_codegen import PythonCodeGenerator, mangle_name
from ape.compiler.ir_nodes import (
    ProjectNode, ModuleNode, EntityNode, TaskNode, FieldNode
)


class TestNameMangling(unittest.TestCase):
    """Test the name mangling helper function"""
    
    def test_mangle_with_module(self):
        """Test mangling with module name"""
        self.assertEqual(mangle_name("math", "add"), "math__add")
        self.assertEqual(mangle_name("strings", "upper"), "strings__upper")
        self.assertEqual(mangle_name("my_module", "my_func"), "my_module__my_func")
    
    def test_mangle_without_module(self):
        """Test mangling without module (backward compatible)"""
        self.assertEqual(mangle_name(None, "calculate"), "calculate")
        self.assertEqual(mangle_name("", "process"), "process")
    
    def test_mangle_preserves_symbol_name(self):
        """Test that symbol name is preserved correctly"""
        self.assertEqual(mangle_name("mod", "func_123"), "mod__func_123")
        self.assertEqual(mangle_name("mod", "CamelCase"), "mod__CamelCase")


class TestModuleAwareTaskGeneration(unittest.TestCase):
    """Test code generation for tasks with module awareness"""
    
    def test_task_in_named_module(self):
        """Test that task in named module gets mangled name"""
        task = TaskNode(
            name="add",
            inputs=[
                FieldNode(name="a", type="Integer"),
                FieldNode(name="b", type="Integer")
            ],
            outputs=[
                FieldNode(name="result", type="Integer")
            ]
        )
        
        module = ModuleNode(name="math", tasks=[task])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should have mangled function name
        self.assertIn("def math__add(", content)
        # Should NOT have unmangled name
        self.assertNotIn("def add(", content)
    
    def test_task_without_module_declaration(self):
        """Test that task without module keeps original name (backward compatible)"""
        task = TaskNode(
            name="calculate",
            inputs=[
                FieldNode(name="x", type="Integer")
            ],
            outputs=[
                FieldNode(name="result", type="Integer")
            ]
        )
        
        # Module with empty name (no module declaration)
        module = ModuleNode(name="", tasks=[task])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should have original name (no mangling)
        self.assertIn("def calculate(", content)
    
    def test_task_in_module_with_none_name(self):
        """Test task in module with None name (legacy behavior)"""
        task = TaskNode(
            name="process",
            inputs=[],
            outputs=[]
        )
        
        # Module with None name
        module = ModuleNode(name=None, tasks=[task])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should have original name (no mangling)
        self.assertIn("def process(", content)
    
    def test_multiple_tasks_same_module(self):
        """Test multiple tasks in same module all get mangled"""
        task1 = TaskNode(name="add", inputs=[], outputs=[])
        task2 = TaskNode(name="subtract", inputs=[], outputs=[])
        task3 = TaskNode(name="multiply", inputs=[], outputs=[])
        
        module = ModuleNode(name="math", tasks=[task1, task2, task3])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # All tasks should be mangled
        self.assertIn("def math__add(", content)
        self.assertIn("def math__subtract(", content)
        self.assertIn("def math__multiply(", content)


class TestModuleAwareFlowGeneration(unittest.TestCase):
    """Test code generation for flows with module awareness"""
    
    def test_flow_in_named_module(self):
        """Test that flow in named module gets mangled name"""
        from ape.compiler.ir_nodes import FlowNode, StepNode
        
        flow = FlowNode(
            name="process_data",
            steps=[
                StepNode(action="load data"),
                StepNode(action="transform data")
            ]
        )
        
        module = ModuleNode(name="workflows", flows=[flow])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should have mangled function name
        self.assertIn("def workflows__process_data(", content)
    
    def test_flow_without_module(self):
        """Test flow without module keeps original name"""
        from ape.compiler.ir_nodes import FlowNode, StepNode
        
        flow = FlowNode(
            name="simple_flow",
            steps=[StepNode(action="do something")]
        )
        
        module = ModuleNode(name="", flows=[flow])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should have original name
        self.assertIn("def simple_flow(", content)


class TestQualifiedIdentifierResolution(unittest.TestCase):
    """Test resolution of qualified identifiers in expressions"""
    
    def test_resolve_simple_identifier(self):
        """Test resolving simple (non-qualified) identifier"""
        project = ProjectNode(name="test", modules=[])
        codegen = PythonCodeGenerator(project)
        
        # Simple names should pass through unchanged
        self.assertEqual(codegen.resolve_qualified_name("calculate"), "calculate")
        self.assertEqual(codegen.resolve_qualified_name("process"), "process")
    
    def test_resolve_qualified_identifier(self):
        """Test resolving module-qualified identifier"""
        project = ProjectNode(name="test", modules=[])
        codegen = PythonCodeGenerator(project)
        
        # Qualified names should be mangled
        self.assertEqual(codegen.resolve_qualified_name("math.add"), "math__add")
        self.assertEqual(codegen.resolve_qualified_name("strings.upper"), "strings__upper")
    
    def test_resolve_deeply_nested_identifier(self):
        """Test resolving deeply nested qualified identifier"""
        project = ProjectNode(name="test", modules=[])
        codegen = PythonCodeGenerator(project)
        
        # Deeply nested: module.submodule.symbol -> module.submodule__symbol
        self.assertEqual(
            codegen.resolve_qualified_name("strings.utils.upper"),
            "strings.utils__upper"
        )


class TestMultiModuleProject(unittest.TestCase):
    """Test code generation for projects with multiple modules"""
    
    def test_two_modules_different_tasks(self):
        """Test generating code for multiple modules with different task names"""
        task1 = TaskNode(name="add", inputs=[], outputs=[])
        module1 = ModuleNode(name="math", tasks=[task1])
        
        task2 = TaskNode(name="upper", inputs=[], outputs=[])
        module2 = ModuleNode(name="strings", tasks=[task2])
        
        project = ProjectNode(name="TestProject", modules=[module1, module2])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 2)
        
        # Check first module
        math_content = [f.content for f in files if "math" in f.path][0]
        self.assertIn("def math__add(", math_content)
        
        # Check second module
        strings_content = [f.content for f in files if "strings" in f.path][0]
        self.assertIn("def strings__upper(", strings_content)
    
    def test_two_modules_same_task_name(self):
        """Test that same task name in different modules gets different mangled names"""
        task1 = TaskNode(name="process", inputs=[], outputs=[])
        module1 = ModuleNode(name="module_a", tasks=[task1])
        
        task2 = TaskNode(name="process", inputs=[], outputs=[])
        module2 = ModuleNode(name="module_b", tasks=[task2])
        
        project = ProjectNode(name="TestProject", modules=[module1, module2])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 2)
        
        # Each module should have its own mangled version
        module_a_content = [f.content for f in files if "module_a" in f.path][0]
        self.assertIn("def module_a__process(", module_a_content)
        
        module_b_content = [f.content for f in files if "module_b" in f.path][0]
        self.assertIn("def module_b__process(", module_b_content)


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing code without modules still works"""
    
    def test_legacy_single_file_no_module(self):
        """Test generating code for single file without module declaration"""
        entity = EntityNode(
            name="User",
            fields=[FieldNode(name="name", type="String")]
        )
        
        task = TaskNode(
            name="create_user",
            inputs=[FieldNode(name="name", type="String")],
            outputs=[FieldNode(name="user", type="User")]
        )
        
        # Module with no name (legacy)
        module = ModuleNode(name="", entities=[entity], tasks=[task])
        project = ProjectNode(name="Legacy", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Should generate without mangling
        self.assertIn("class User:", content)
        self.assertIn("def create_user(", content)
        # Should NOT have mangled names
        self.assertNotIn("__create_user", content)


if __name__ == '__main__':
    unittest.main()
