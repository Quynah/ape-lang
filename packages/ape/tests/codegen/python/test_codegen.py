"""
Unit tests for Python Code Generator

Tests the Ape → Python code generation pipeline.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ape.codegen.python_codegen import PythonCodeGenerator
from ape.compiler.ir_nodes import (
    ProjectNode, ModuleNode, EntityNode, TaskNode, FlowNode,
    PolicyNode, EnumNode, FieldNode, StepNode
)
from ape.parser import parse_ape_source
from ape.ir import IRBuilder


class TestPythonCodegenBasic(unittest.TestCase):
    """Test basic Python code generation"""
    
    def test_generate_empty_project(self):
        """Test generating code for empty project"""
        project = ProjectNode(name="EmptyProject", modules=[])
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 0)
    
    def test_generate_simple_entity(self):
        """Test generating a simple entity"""
        # Create IR manually
        entity = EntityNode(
            name="User",
            fields=[
                FieldNode(name="id", type="Integer"),
                FieldNode(name="name", type="String"),
                FieldNode(name="email", type="String"),
            ]
        )
        
        module = ModuleNode(name="test", entities=[entity])
        project = ProjectNode(name="TestProject", modules=[module])
        
        # Generate code
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].language, "python")
        self.assertIn("class User:", files[0].content)
        self.assertIn("@dataclass", files[0].content)
        self.assertIn("id: int", files[0].content)
        self.assertIn("name: str", files[0].content)
        self.assertIn("email: str", files[0].content)
    
    def test_generate_enum(self):
        """Test generating an enum"""
        enum = EnumNode(
            name="Status",
            values=["pending", "active", "completed"]
        )
        
        module = ModuleNode(name="test", enums=[enum])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        self.assertIn("class Status:", content)
        self.assertIn('PENDING = "pending"', content)
        self.assertIn('ACTIVE = "active"', content)
        self.assertIn('COMPLETED = "completed"', content)
    
    def test_generate_task(self):
        """Test generating a task"""
        task = TaskNode(
            name="ProcessData",
            inputs=[
                FieldNode(name="data", type="String")
            ],
            outputs=[
                FieldNode(name="result", type="String")
            ],
            steps=[
                StepNode(action="validate data"),
                StepNode(action="transform data"),
            ]
        )
        
        # Use empty module name for backward compatibility (no module declaration)
        module = ModuleNode(name="", tasks=[task])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        self.assertIn("def ProcessData(data: str) -> str:", content)
        self.assertIn("raise NotImplementedError", content)
        self.assertIn("validate data", content)
        self.assertIn("transform data", content)
    
    def test_generate_flow(self):
        """Test generating a flow"""
        flow = FlowNode(
            name="UserRegistrationFlow",
            steps=[
                StepNode(action="validate input"),
                StepNode(action="create user"),
                StepNode(action="send email"),
            ]
        )
        
        # Use empty module name for backward compatibility (no module declaration)
        module = ModuleNode(name="", flows=[flow])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        self.assertIn("FLOW_UserRegistrationFlow", content)
        self.assertIn("def UserRegistrationFlow(context: RunContext) -> None:", content)
        self.assertIn("validate input", content)
    
    def test_generate_policy(self):
        """Test generating a policy"""
        policy = PolicyNode(
            name="SecurityPolicy",
            rules=["all data must be encrypted", "no plaintext passwords"],
            scope="global"
        )
        
        module = ModuleNode(name="test", policies=[policy])
        project = ProjectNode(name="TestProject", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        self.assertIn("POLICY_SecurityPolicy", content)
        self.assertIn("all data must be encrypted", content)
        self.assertIn("no plaintext passwords", content)


class TestPythonCodegenSyntax(unittest.TestCase):
    """Test that generated code is syntactically valid Python"""
    
    def test_generated_code_is_valid_python(self):
        """Test that generated code compiles"""
        # Create a comprehensive module
        entity = EntityNode(
            name="User",
            fields=[
                FieldNode(name="id", type="Integer"),
                FieldNode(name="name", type="String"),
            ]
        )
        
        enum = EnumNode(name="Role", values=["admin", "user"])
        
        task = TaskNode(
            name="CreateUser",
            inputs=[FieldNode(name="name", type="String")],
            outputs=[FieldNode(name="user", type="User")],
            steps=[StepNode(action="create user instance")]
        )
        
        module = ModuleNode(
            name="test",
            entities=[entity],
            enums=[enum],
            tasks=[task]
        )
        
        project = ProjectNode(name="TestProject", modules=[module])
        
        # Generate code
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        
        # Try to compile the generated code
        try:
            compile(files[0].content, '<generated>', 'exec')
        except SyntaxError as e:
            self.fail(f"Generated code has syntax error: {e}\n\nCode:\n{files[0].content}")


class TestPythonCodegenFromParser(unittest.TestCase):
    """Test code generation from parsed Ape source"""
    
    def test_generate_from_parsed_source(self):
        """Test complete pipeline: parse → IR → codegen"""
        source = """entity User:
    id: Integer
    name: String
    email: String

enum Status:
    - pending
    - active
    - completed

task CreateUser:
    inputs:
        name: String
        email: String
    outputs:
        user: User
    steps:
        - validate name and email
        - create User instance
        - return user
"""
        
        # Parse to AST
        ast = parse_ape_source(source, "test.ape")
        
        # Build IR
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "test.ape")
        
        # Create project
        project = ProjectNode(name="TestProject", modules=[ir_module])
        
        # Generate Python code
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "generated/test_gen.py")
        self.assertEqual(files[0].language, "python")
        
        content = files[0].content
        
        # Check entity
        self.assertIn("@dataclass", content)
        self.assertIn("class User:", content)
        self.assertIn("id: int", content)
        self.assertIn("name: str", content)
        
        # Check enum
        self.assertIn("class Status:", content)
        self.assertIn('PENDING = "pending"', content)
        
        # Check task
        self.assertIn("def CreateUser(name: str, email: str)", content)
        self.assertIn('-> "User":', content)
        
        # Verify Python syntax
        try:
            compile(content, '<generated>', 'exec')
        except SyntaxError as e:
            self.fail(f"Generated code has syntax error: {e}")
    
    def test_generate_complete_module(self):
        """Test generating a complete module with all constructs"""
        source = """entity DriveFile:
    file_id: String
    owner: String
    created_at: String

enum SharingType:
    - anyone
    - user
    - group

task CollectAclFindings:
    inputs:
        files: String
    outputs:
        findings: String
    steps:
        - analyze file permissions
        - identify issues
        - return findings

flow DriveAclAudit:
    steps:
        - fetch files from drive
        - call CollectAclFindings
        - generate report

policy DataSafetyPolicy:
    rules:
        - all file access must be logged
        - sensitive files require approval
"""
        
        # Parse and build IR
        ast = parse_ape_source(source, "drive_audit.ape")
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "drive_audit.ape")
        project = ProjectNode(name="DriveAudit", modules=[ir_module])
        
        # Generate code
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        self.assertEqual(len(files), 1)
        content = files[0].content
        
        # Verify all constructs are present
        self.assertIn("class DriveFile:", content)
        self.assertIn("class SharingType:", content)
        self.assertIn("def CollectAclFindings", content)
        self.assertIn("def DriveAclAudit", content)
        self.assertIn("POLICY_DataSafetyPolicy", content)
        
        # Verify Python syntax
        try:
            compile(content, '<generated>', 'exec')
        except SyntaxError as e:
            self.fail(f"Generated code has syntax error: {e}\n\nCode:\n{content}")


class TestTypeMapping(unittest.TestCase):
    """Test Ape type to Python type mapping"""
    
    def test_basic_type_mapping(self):
        """Test basic type mappings"""
        entity = EntityNode(
            name="TestEntity",
            fields=[
                FieldNode(name="str_field", type="String"),
                FieldNode(name="int_field", type="Integer"),
                FieldNode(name="float_field", type="Float"),
                FieldNode(name="bool_field", type="Boolean"),
            ]
        )
        
        module = ModuleNode(name="test", entities=[entity])
        project = ProjectNode(name="Test", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        content = files[0].content
        self.assertIn("str_field: str", content)
        self.assertIn("int_field: int", content)
        self.assertIn("float_field: float", content)
        self.assertIn("bool_field: bool", content)
    
    def test_optional_fields(self):
        """Test optional field handling"""
        entity = EntityNode(
            name="TestEntity",
            fields=[
                FieldNode(name="required", type="String", optional=False),
                FieldNode(name="optional", type="String", optional=True),
            ]
        )
        
        module = ModuleNode(name="test", entities=[entity])
        project = ProjectNode(name="Test", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        content = files[0].content
        self.assertIn("required: str", content)
        self.assertIn("optional: str | None = None", content)
    
    def test_user_defined_types(self):
        """Test references to user-defined types"""
        task = TaskNode(
            name="ProcessUser",
            inputs=[FieldNode(name="user", type="User")],
            outputs=[FieldNode(name="result", type="ProcessResult")],
            steps=[]
        )
        
        module = ModuleNode(name="test", tasks=[task])
        project = ProjectNode(name="Test", modules=[module])
        
        codegen = PythonCodeGenerator(project)
        files = codegen.generate()
        
        content = files[0].content
        # User-defined types should be quoted for forward references
        self.assertIn('user: "User"', content)
        self.assertIn('-> "ProcessResult":', content)


if __name__ == '__main__':
    unittest.main()
