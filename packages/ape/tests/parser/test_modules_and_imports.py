"""
Tests for Module Declarations and Import Statements (v0.2.0)

Tests the parser's ability to handle:
- module declarations
- import statements with simple and qualified names
- proper placement validation
- backward compatibility with legacy code
"""

import pytest
from ape.tokenizer.tokenizer import Tokenizer
from ape.parser.parser import Parser, ParseError
from ape.parser.ast_nodes import ModuleNode, ImportNode


class TestModuleDeclarations:
    """Test module declaration parsing"""
    
    def test_module_declaration_simple(self):
        """Test basic module declaration"""
        source = """module math

entity Number:
    value: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert isinstance(module, ModuleNode)
        assert module.name == "math"
        assert module.has_module_declaration is True
        assert len(module.entities) == 1
        assert module.entities[0].name == "Number"
    
    def test_module_declaration_without_body(self):
        """Test module declaration with no definitions"""
        source = "module mymodule\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == "mymodule"
        assert module.has_module_declaration is True
        assert len(module.entities) == 0
        assert len(module.tasks) == 0
    
    def test_no_module_declaration_legacy(self):
        """Test that files without module declaration work (backward compatibility)"""
        source = """entity User:
    name: String
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == ""
        assert module.has_module_declaration is False
        assert len(module.entities) == 1
    
    def test_empty_file(self):
        """Test parsing an empty file"""
        source = ""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == ""
        assert module.has_module_declaration is False
        assert len(module.entities) == 0


class TestImportStatements:
    """Test import statement parsing"""
    
    def test_import_simple_module(self):
        """Test simple module import: import math"""
        source = """import math

entity Calculator:
    value: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert len(module.imports) == 1
        import_node = module.imports[0]
        assert isinstance(import_node, ImportNode)
        assert import_node.qualified_name is not None
        assert import_node.qualified_name.parts == ["math"]
        assert import_node.is_specific_symbol is False
        assert import_node.module_name == "math"
        assert import_node.symbol_name is None
    
    def test_import_qualified_symbol(self):
        """Test qualified import: import math.add"""
        source = """import math.add

entity Result:
    sum: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert len(module.imports) == 1
        import_node = module.imports[0]
        assert import_node.qualified_name.parts == ["math", "add"]
        assert import_node.is_specific_symbol is True
        assert import_node.module_name == "math"
        assert import_node.symbol_name == "add"
    
    def test_import_deeply_nested(self):
        """Test deeply nested import: import collections.list.sort"""
        source = "import collections.list.sort\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert len(module.imports) == 1
        import_node = module.imports[0]
        assert import_node.qualified_name.parts == ["collections", "list", "sort"]
        assert import_node.module_name == "collections"
        assert import_node.symbol_name == "sort"
    
    def test_multiple_imports(self):
        """Test multiple import statements"""
        source = """import math
import strings.upper
import collections

entity Data:
    value: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert len(module.imports) == 3
        
        # First import: math
        assert module.imports[0].qualified_name.parts == ["math"]
        assert module.imports[0].is_specific_symbol is False
        
        # Second import: strings.upper
        assert module.imports[1].qualified_name.parts == ["strings", "upper"]
        assert module.imports[1].is_specific_symbol is True
        
        # Third import: collections
        assert module.imports[2].qualified_name.parts == ["collections"]
        assert module.imports[2].is_specific_symbol is False


class TestModuleAndImportCombinations:
    """Test combinations of module declarations and imports"""
    
    def test_module_with_single_import(self):
        """Test module declaration followed by import"""
        source = """module calculator

import math

entity Result:
    value: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == "calculator"
        assert module.has_module_declaration is True
        assert len(module.imports) == 1
        assert module.imports[0].qualified_name.parts == ["math"]
        assert len(module.entities) == 1
    
    def test_module_with_multiple_imports(self):
        """Test module with multiple imports"""
        source = """module app

import math
import strings.upper
import io

task process:
    inputs:
        x: int
    outputs:
        y: int
    steps:
        - compute y
        - return y
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == "app"
        assert len(module.imports) == 3
        assert len(module.tasks) == 1
    
    def test_imports_without_module_declaration(self):
        """Test imports in file without module declaration (legacy)"""
        source = """import math
import strings

entity Data:
    value: int
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        assert module.name == ""
        assert module.has_module_declaration is False
        assert len(module.imports) == 2
        assert len(module.entities) == 1


class TestImportPlacementValidation:
    """Test that imports must be at the top of the file"""
    
    def test_import_after_entity_fails(self):
        """Test that import after entity declaration raises error"""
        source = """entity User:
    name: String

import math
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError) as exc_info:
            parser.parse()
        
        assert "Import statements must appear at the top" in str(exc_info.value)
    
    def test_import_after_task_fails(self):
        """Test that import after task declaration raises error"""
        source = """task calculate:
    inputs:
        x: int
    outputs:
        y: int
    steps:
        - compute y
        - return y

import math
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError) as exc_info:
            parser.parse()
        
        assert "Import statements must appear at the top" in str(exc_info.value)
    
    def test_import_after_enum_fails(self):
        """Test that import after enum declaration raises error"""
        source = """enum Color:
    - RED
    - GREEN

import strings
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError) as exc_info:
            parser.parse()
        
        assert "Import statements must appear at the top" in str(exc_info.value)
    
    def test_correct_order_module_imports_definitions(self):
        """Test correct ordering: module, imports, then definitions"""
        source = """module app

import math
import strings

entity User:
    name: String

enum Status:
    - ACTIVE
    - INACTIVE

task process:
    inputs:
        x: int
    outputs:
        y: int
    steps:
        - do something
        - return y
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        # Should parse successfully
        assert module.name == "app"
        assert len(module.imports) == 2
        assert len(module.entities) == 1
        assert len(module.enums) == 1
        assert len(module.tasks) == 1


class TestQualifiedIdentifierNode:
    """Test QualifiedIdentifierNode helper properties"""
    
    def test_simple_identifier(self):
        """Test properties of simple identifier"""
        source = "import math\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        qid = module.imports[0].qualified_name
        assert qid.is_simple is True
        assert qid.module_name == "math"
        assert qid.symbol_name is None
        assert str(qid) == "math"
    
    def test_qualified_identifier(self):
        """Test properties of qualified identifier"""
        source = "import strings.upper\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        qid = module.imports[0].qualified_name
        assert qid.is_simple is False
        assert qid.module_name == "strings"
        assert qid.symbol_name == "upper"
        assert str(qid) == "strings.upper"
    
    def test_deeply_qualified_identifier(self):
        """Test properties of deeply qualified identifier"""
        source = "import collections.list.sort\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        qid = module.imports[0].qualified_name
        assert qid.is_simple is False
        assert qid.module_name == "collections"
        assert qid.symbol_name == "sort"
        assert str(qid) == "collections.list.sort"


class TestBackwardCompatibility:
    """Test that existing Ape programs continue to work"""
    
    def test_legacy_program_without_modules(self):
        """Test that programs without module/import continue to parse"""
        source = """entity Calculator:
    left: int
    right: int

enum Operation:
    - ADD
    - SUBTRACT

task calculate:
    inputs:
        calc: Calculator
        op: Operation
    outputs:
        result: int
    steps:
        - perform operation
        - return result
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        # Should parse exactly as before
        assert module.name == ""
        assert module.has_module_declaration is False
        assert len(module.imports) == 0
        assert len(module.entities) == 1
        assert len(module.enums) == 1
        assert len(module.tasks) == 1
    
    def test_complex_program_without_modules(self):
        """Test complex existing program structure"""
        source = """entity User:
    id: int
    name: String

entity Post:
    author: User
    content: String

task create_post:
    inputs:
        user: User
        text: String
    outputs:
        post: Post
    constraints:
        - deterministic
    steps:
        - validate user
        - create post object
        - return post

flow PostCreationFlow:
    steps:
        - receive request
        - call create_post
        - store in database
        - return response

policy DataPolicy:
    rules:
        - all data must be validated
        - no empty posts allowed
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        # All legacy constructs should still work
        assert len(module.entities) == 2
        assert len(module.tasks) == 1
        assert len(module.flows) == 1
        assert len(module.policies) == 1
        assert len(module.imports) == 0
        assert module.has_module_declaration is False


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_module_keyword_requires_name(self):
        """Test that 'module' keyword requires an identifier"""
        source = "module\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError):
            parser.parse()
    
    def test_import_keyword_requires_path(self):
        """Test that 'import' keyword requires a qualified name"""
        source = "import\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError):
            parser.parse()
    
    def test_import_with_trailing_dot_fails(self):
        """Test that import with trailing dot fails"""
        source = "import math.\n"
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError):
            parser.parse()
    
    def test_module_declaration_can_only_appear_once(self):
        """Test that module declaration appears only at the top"""
        # Note: This is enforced by grammar - module keyword after first line
        # would be parsed as unexpected token
        source = """entity User:
    name: String

module late_module
"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(ParseError):
            parser.parse()
    
    def test_whitespace_handling(self):
        """Test proper handling of whitespace around module and import"""
        source = """

module myapp


import math

import strings.upper


entity Data:
    value: int


"""
        tokens = Tokenizer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        
        # Should handle extra whitespace gracefully
        assert module.name == "myapp"
        assert len(module.imports) == 2
        assert len(module.entities) == 1
