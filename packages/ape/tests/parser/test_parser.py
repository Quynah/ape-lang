"""
Unit tests for Ape Parser

Tests tokenizer, parser, and IR builder components.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ape.tokenizer import Tokenizer, TokenType
from ape.parser import Parser, parse_ape_source
from ape.ir import IRBuilder


class TestTokenizer(unittest.TestCase):
    """Test the tokenizer"""
    
    def test_simple_entity(self):
        """Test tokenizing a simple entity"""
        source = """entity User:
    name: String
    age: Integer
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        # Check first few tokens
        self.assertEqual(tokens[0].type, TokenType.ENTITY)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "User")
        self.assertEqual(tokens[2].type, TokenType.COLON)
    
    def test_indentation(self):
        """Test indentation tracking"""
        source = """entity User:
    name: String
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        # Find indent and dedent tokens
        has_indent = any(t.type == TokenType.INDENT for t in tokens)
        has_dedent = any(t.type == TokenType.DEDENT for t in tokens)
        
        self.assertTrue(has_indent)
        self.assertTrue(has_dedent)
    
    def test_keywords(self):
        """Test keyword recognition"""
        source = "entity task flow policy enum constraints"
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.ENTITY)
        self.assertEqual(tokens[1].type, TokenType.TASK)
        self.assertEqual(tokens[2].type, TokenType.FLOW)
        self.assertEqual(tokens[3].type, TokenType.POLICY)
        self.assertEqual(tokens[4].type, TokenType.ENUM)
        self.assertEqual(tokens[5].type, TokenType.CONSTRAINTS)


class TestParser(unittest.TestCase):
    """Test the parser"""
    
    def test_parse_entity(self):
        """Test parsing an entity definition"""
        source = """entity User:
    name: String
    email: String
    age: Integer
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.entities), 1)
        entity = ast.entities[0]
        self.assertEqual(entity.name, "User")
        self.assertEqual(len(entity.fields), 3)
        self.assertEqual(entity.fields[0].name, "name")
        self.assertEqual(entity.fields[0].type_annotation.type_name, "String")
    
    def test_parse_enum(self):
        """Test parsing an enum definition"""
        source = """enum Status:
    - pending
    - active
    - completed
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.enums), 1)
        enum = ast.enums[0]
        self.assertEqual(enum.name, "Status")
        self.assertEqual(len(enum.values), 3)
        self.assertEqual(enum.values[0], "pending")
    
    def test_parse_task(self):
        """Test parsing a task definition"""
        source = """task CalculateSum:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: Integer
    steps:
        - add a and b
        - return result
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.tasks), 1)
        task = ast.tasks[0]
        self.assertEqual(task.name, "CalculateSum")
        self.assertEqual(len(task.inputs), 2)
        self.assertEqual(len(task.outputs), 1)
        self.assertEqual(len(task.steps), 2)
    
    def test_parse_policy(self):
        """Test parsing a policy definition"""
        source = """policy SecurityPolicy:
    rules:
        - all data must be encrypted
        - no hardcoded credentials
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.policies), 1)
        policy = ast.policies[0]
        self.assertEqual(policy.name, "SecurityPolicy")
        self.assertEqual(len(policy.rules), 2)
    
    def test_parse_flow(self):
        """Test parsing a flow definition"""
        source = """flow UserRegistration:
    steps:
        - validate input
        - create user
        - send confirmation
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.flows), 1)
        flow = ast.flows[0]
        self.assertEqual(flow.name, "UserRegistration")
        self.assertEqual(len(flow.steps), 3)


class TestIRBuilder(unittest.TestCase):
    """Test the IR builder"""
    
    def test_build_entity_ir(self):
        """Test building IR from entity AST"""
        source = """entity User:
    name: String
    age: Integer
"""
        ast = parse_ape_source(source)
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "test.ape")
        
        self.assertEqual(len(ir_module.entities), 1)
        entity = ir_module.entities[0]
        self.assertEqual(entity.name, "User")
        self.assertEqual(len(entity.fields), 2)
        self.assertEqual(entity.fields[0].name, "name")
        self.assertEqual(entity.fields[0].type, "String")
    
    def test_build_task_ir(self):
        """Test building IR from task AST"""
        source = """task Process:
    inputs:
        data: String
    outputs:
        result: String
    steps:
        - process data
"""
        ast = parse_ape_source(source)
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "test.ape")
        
        self.assertEqual(len(ir_module.tasks), 1)
        task = ir_module.tasks[0]
        self.assertEqual(task.name, "Process")
        self.assertEqual(len(task.inputs), 1)
        self.assertEqual(len(task.outputs), 1)
        self.assertEqual(len(task.steps), 1)


class TestComplexExamples(unittest.TestCase):
    """Test parsing complete Ape programs"""
    
    def test_complete_module(self):
        """Test parsing a complete module with multiple definitions"""
        source = """entity User:
    id: Integer
    name: String

enum Role:
    - admin
    - user
    - guest

task CreateUser:
    inputs:
        name: String
        role: Role
    outputs:
        user: User
    steps:
        - validate name
        - create user entity
        - assign role
        - return user
"""
        ast = parse_ape_source(source)
        
        self.assertEqual(len(ast.entities), 1)
        self.assertEqual(len(ast.enums), 1)
        self.assertEqual(len(ast.tasks), 1)
        
        # Build IR
        builder = IRBuilder()
        ir_module = builder.build_module(ast, "test.ape")
        
        self.assertEqual(len(ir_module.entities), 1)
        self.assertEqual(len(ir_module.enums), 1)
        self.assertEqual(len(ir_module.tasks), 1)


if __name__ == '__main__':
    unittest.main()
