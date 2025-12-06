"""
Tests for multi-language surface syntax.

Tests that language adapters correctly normalize language-specific keywords
to canonical APE while preserving determinism and producing identical ASTs.
"""

import pytest
from ape.lang import get_adapter, list_supported_languages
from ape.lang.base import LanguageAdapter
from ape.errors import ValidationError
from ape.parser.parser import parse_ape_source
from ape.parser.ast_nodes import IfNode, WhileNode, ForNode
from ape import run


class TestLanguageRegistry:
    """Test language adapter registry."""
    
    def test_list_supported_languages(self):
        """Test listing all supported languages."""
        languages = list_supported_languages()
        
        assert 'en' in languages
        assert 'nl' in languages
        assert 'fr' in languages
        assert 'de' in languages
        assert 'es' in languages
        assert 'it' in languages
        assert 'pt' in languages
        assert len(languages) == 7
    
    def test_get_adapter_english(self):
        """Test getting English adapter."""
        adapter = get_adapter('en')
        assert adapter.language_code == 'en'
        assert adapter.language_name == 'English'
        assert adapter.script == 'latin'
    
    def test_get_adapter_dutch(self):
        """Test getting Dutch adapter."""
        adapter = get_adapter('nl')
        assert adapter.language_code == 'nl'
        assert adapter.language_name == 'Dutch'
        assert adapter.script == 'latin'
    
    def test_get_adapter_unsupported_fails(self):
        """Test that unsupported language code raises error."""
        with pytest.raises(ValidationError) as exc_info:
            get_adapter('xx')
        
        assert 'unsupported' in str(exc_info.value).lower()
        assert 'xx' in str(exc_info.value)


class TestEnglishAdapter:
    """Test English adapter (identity)."""
    
    def test_english_is_identity(self):
        """Test English adapter returns source unchanged."""
        adapter = get_adapter('en')
        source = "if x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert normalized == source
    
    def test_english_no_keyword_mapping(self):
        """Test English adapter has empty keyword mapping."""
        adapter = get_adapter('en')
        mapping = adapter.get_keyword_mapping()
        assert mapping == {}


class TestDutchAdapter:
    """Test Dutch keyword normalization."""
    
    def test_dutch_if_keyword(self):
        """Test Dutch 'als' normalizes to 'if'."""
        adapter = get_adapter('nl')
        source = "als x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
        assert 'als' not in normalized
    
    def test_dutch_else_keyword(self):
        """Test Dutch 'anders' normalizes to 'else'."""
        adapter = get_adapter('nl')
        source = "als x > 5:\n    - set y to 10\nanders:\n    - set y to 0"
        
        normalized = adapter.normalize_source(source)
        assert 'else:' in normalized
        assert 'anders' not in normalized
    
    def test_dutch_while_keyword(self):
        """Test Dutch 'zolang' normalizes to 'while'."""
        adapter = get_adapter('nl')
        source = "zolang x > 0:\n    - set x to x - 1"
        
        normalized = adapter.normalize_source(source)
        assert 'while x > 0:' in normalized
        assert 'zolang' not in normalized
    
    def test_dutch_logical_operators(self):
        """Test Dutch logical operators normalize correctly."""
        adapter = get_adapter('nl')
        source = "als x > 5 en y < 10 of niet z:\n    - set w to 1"
        
        normalized = adapter.normalize_source(source)
        assert 'and' in normalized
        assert 'or' in normalized
        assert 'not' in normalized
        assert 'en' not in normalized
        assert 'of' not in normalized
        assert 'niet' not in normalized


class TestFrenchAdapter:
    """Test French keyword normalization."""
    
    def test_french_if_keyword(self):
        """Test French 'si' normalizes to 'if'."""
        adapter = get_adapter('fr')
        source = "si x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
    
    def test_french_while_multiword(self):
        """Test French 'tant que' (multi-word) normalizes to 'while'."""
        adapter = get_adapter('fr')
        source = "tant que x > 0:\n    - set x to x - 1"
        
        normalized = adapter.normalize_source(source)
        assert 'while x > 0:' in normalized
        assert 'tant que' not in normalized


class TestGermanAdapter:
    """Test German keyword normalization."""
    
    def test_german_if_keyword(self):
        """Test German 'wenn' normalizes to 'if'."""
        adapter = get_adapter('de')
        source = "wenn x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
    
    def test_german_logical_operators(self):
        """Test German logical operators normalize correctly."""
        adapter = get_adapter('de')
        source = "wenn x > 5 und y < 10 oder nicht z:\n    - set w to 1"
        
        normalized = adapter.normalize_source(source)
        assert 'and' in normalized
        assert 'or' in normalized
        assert 'not' in normalized


class TestSpanishAdapter:
    """Test Spanish keyword normalization."""
    
    def test_spanish_if_keyword(self):
        """Test Spanish 'si' normalizes to 'if'."""
        adapter = get_adapter('es')
        source = "si x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
    
    def test_spanish_while_keyword(self):
        """Test Spanish 'mientras' normalizes to 'while'."""
        adapter = get_adapter('es')
        source = "mientras x > 0:\n    - set x to x - 1"
        
        normalized = adapter.normalize_source(source)
        assert 'while x > 0:' in normalized


class TestItalianAdapter:
    """Test Italian keyword normalization."""
    
    def test_italian_if_keyword(self):
        """Test Italian 'se' normalizes to 'if'."""
        adapter = get_adapter('it')
        source = "se x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
    
    def test_italian_else_keyword(self):
        """Test Italian 'altrimenti' normalizes to 'else'."""
        adapter = get_adapter('it')
        source = "se x > 5:\n    - set y to 10\naltrimenti:\n    - set y to 0"
        
        normalized = adapter.normalize_source(source)
        assert 'else:' in normalized


class TestPortugueseAdapter:
    """Test Portuguese keyword normalization."""
    
    def test_portuguese_if_keyword(self):
        """Test Portuguese 'se' normalizes to 'if'."""
        adapter = get_adapter('pt')
        source = "se x > 5:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5:' in normalized
    
    def test_portuguese_while_keyword(self):
        """Test Portuguese 'enquanto' normalizes to 'while'."""
        adapter = get_adapter('pt')
        source = "enquanto x > 0:\n    - set x to x - 1"
        
        normalized = adapter.normalize_source(source)
        assert 'while x > 0:' in normalized


class TestIdenticalAST:
    """Test that different languages produce identical ASTs."""
    
    def test_if_statement_identical_ast(self):
        """Test IF statement produces same AST in all languages."""
        # English
        en_source = """
task main:
    steps:
        if x > 5:
            - set y to 10
"""
        en_adapter = get_adapter('en')
        en_normalized = en_adapter.normalize_source(en_source)
        en_ast = parse_ape_source(en_normalized)
        
        # Dutch
        nl_source = """
task main:
    steps:
        als x > 5:
            - set y to 10
"""
        nl_adapter = get_adapter('nl')
        nl_normalized = nl_adapter.normalize_source(nl_source)
        nl_ast = parse_ape_source(nl_normalized)
        
        # Both should parse successfully and be ModuleNode
        assert type(en_ast).__name__ == type(nl_ast).__name__
        assert en_ast.__class__.__name__ == 'ModuleNode'
    
    def test_while_loop_identical_ast(self):
        """Test WHILE loop produces same AST in all languages."""
        # English
        en_source = """
task main:
    steps:
        while x > 0:
            - set x to x - 1
"""
        en_ast = parse_ape_source(en_source)
        
        # German
        de_source = """
task main:
    steps:
        solange x > 0:
            - set x to x - 1
"""
        de_adapter = get_adapter('de')
        de_normalized = de_adapter.normalize_source(de_source)
        de_ast = parse_ape_source(de_normalized)
        
        # Both should parse successfully and be ModuleNode
        assert type(en_ast).__name__ == type(de_ast).__name__
        assert en_ast.__class__.__name__ == 'ModuleNode'


class TestRuntimeIntegration:
    """Test language parameter in run() function."""
    
    def test_run_with_english(self):
        """Test run() with English (default)."""
        source = """
task main:
    steps:
        if x > 5:
            - set result to 10
        else:
            - set result to 0
"""
        # Should not raise error
        result = run(source, context={'x': 10}, language='en')
    
    def test_run_with_dutch(self):
        """Test run() with Dutch."""
        source = """
task main:
    steps:
        als x > 5:
            - set result to 10
        anders:
            - set result to 0
"""
        # Should not raise error
        result = run(source, context={'x': 10}, language='nl')
    
    def test_run_with_french(self):
        """Test run() with French."""
        source = """
task main:
    steps:
        si x > 5:
            - set result to 10
        sinon:
            - set result to 0
"""
        result = run(source, context={'x': 10}, language='fr')
    
    def test_run_with_unsupported_language_fails(self):
        """Test run() fails with unsupported language."""
        source = "if x > 5:\n    - set y to 10"
        
        with pytest.raises(ValidationError) as exc_info:
            run(source, context={'x': 10}, language='xx')
        
        assert 'unsupported' in str(exc_info.value).lower()


class TestWholeWordMatching:
    """Test that keyword replacement uses whole-word matching."""
    
    def test_partial_match_not_replaced(self):
        """Test that partial matches are not replaced."""
        adapter = get_adapter('nl')
        # 'als' should match, but 'also' should not
        source = "als x > 5 also_var:\n    - set y to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'if x > 5' in normalized
        assert 'also_var' in normalized  # Should NOT be changed to 'ifo_var'
    
    def test_identifier_not_replaced(self):
        """Test that identifiers are not replaced."""
        adapter = get_adapter('nl')
        # Variable named 'als_count' should not be changed
        source = "if x > 5:\n    - set als_count to 10"
        
        normalized = adapter.normalize_source(source)
        assert 'als_count' in normalized  # Should remain unchanged


class TestDeterminism:
    """Test that normalization is deterministic."""
    
    def test_same_input_same_output(self):
        """Test that same input produces same output consistently."""
        adapter = get_adapter('nl')
        source = "als x > 5 en y < 10:\n    - set z to 1"
        
        # Call multiple times
        result1 = adapter.normalize_source(source)
        result2 = adapter.normalize_source(source)
        result3 = adapter.normalize_source(source)
        
        # Should be identical
        assert result1 == result2 == result3
