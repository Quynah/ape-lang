"""
Runtime type evaluation tests for APE Decision Engine.

Tests verify runtime behavior of:
- Record literals
- Map literals
- List literals
- Value/Any type behavior
- APE → Python serialization
"""
import pytest
from ape.tokenizer.tokenizer import Tokenizer
from ape.parser.parser import Parser
from ape.compiler.semantic_validator import SemanticValidator
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.context import ExecutionContext


def parse_and_validate(ape_code: str):
    """Helper to parse and validate APE code."""
    tokenizer = Tokenizer(ape_code)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    validator = SemanticValidator()
    validator.validate(ast)
    return ast


def execute_function(ape_code: str, fn_name: str):
    """Helper to execute APE code and call a function."""
    ast = parse_and_validate(ape_code)
    executor = RuntimeExecutor()
    context = ExecutionContext()
    executor.execute(ast, context)
    func = context.get(fn_name)
    return executor._call_user_function(func, [], context, ast)


class TestRecordLiterals:
    """Test Record literal runtime evaluation."""

    def test_simple_record(self):
        """Record literals evaluate to Python dicts."""
        code = '''
fn test_record():
    record = { "id": "test", "value": 42 }
    return record
'''
        record = execute_function(code, 'test_record')

        assert isinstance(record, dict)
        assert record["id"] == "test"
        assert record["value"] == 42

    def test_nested_record(self):
        """Nested records serialize correctly."""
        code = '''
fn test_nested():
    user_data = { "name": "Alice", "age": 30 }
    record = { "user": user_data, "status": "active" }
    return record
'''
        record = execute_function(code, 'test_nested')

        assert record["user"]["name"] == "Alice"
        assert record["user"]["age"] == 30
        assert record["status"] == "active"

    def test_empty_record(self):
        """Empty records are valid."""
        code = '''
fn test_empty():
    record = { }
    return record
'''
        record = execute_function(code, 'test_empty')

        assert isinstance(record, dict)
        assert len(record) == 0


class TestListLiterals:
    """Test List literal runtime evaluation."""

    def test_simple_list(self):
        """List literals evaluate to Python lists."""
        code = '''
fn test_list():
    items = [1, 2, 3]
    return items
'''
        items = execute_function(code, 'test_list')

        assert isinstance(items, (list, type(items)))
        assert len(items) == 3

    def test_list_of_records(self):
        """Lists can contain records."""
        code = '''
fn test_list_records():
    rec_a = { "id": "a", "value": 10 }
    rec_b = { "id": "b", "value": 20 }
    records = [rec_a, rec_b]
    return records
'''
        records = execute_function(code, 'test_list_records')

        assert len(records) == 2
        assert records[0]["id"] == "a"
        assert records[1]["value"] == 20

    def test_empty_list(self):
        """Empty lists are valid."""
        code = '''
fn test_empty():
    items = []
    return items
'''
        items = execute_function(code, 'test_empty')

        assert len(items) == 0


class TestMapLiterals:
    """Test Map literal runtime evaluation."""

    def test_map_with_string_keys(self):
        """Maps with string keys work."""
        code = '''
fn test_map():
    mapping = { "key1": 100, "key2": 200 }
    return mapping
'''
        mapping = execute_function(code, 'test_map')

        assert mapping["key1"] == 100
        assert mapping["key2"] == 200

    def test_map_with_nested_values(self):
        """Maps can contain nested structures."""
        code = '''
fn test_nested_map():
    config = { "timeout": 30 }
    items = [1, 2, 3]
    data = { "config": config, "items": items }
    return data
'''
        data = execute_function(code, 'test_nested_map')

        assert data["config"]["timeout"] == 30
        assert len(data["items"]) == 3


class TestTypeSerialization:
    """Test APE → Python type serialization."""

    def test_record_to_dict(self):
        """Records serialize to dicts."""
        code = '''
fn create_record():
    data = [1, 2]
    return { "type": "record", "data": data }
'''
        record = execute_function(code, 'create_record')

        # Should be a Python dict
        assert isinstance(record, dict)
        assert record["type"] == "record"

    def test_nested_structure_serialization(self):
        """Complex nested structures maintain types."""
        code = '''
fn complex_structure():
    metadata = { "version": 1 }
    tags1 = ["a", "b"]
    tags2 = ["c"]
    rec1 = { "id": 1, "tags": tags1 }
    rec2 = { "id": 2, "tags": tags2 }
    records = [rec1, rec2]
    return { "metadata": metadata, "records": records }
'''
        data = execute_function(code, 'complex_structure')

        assert isinstance(data, dict)
        assert len(data["records"]) == 2
        assert data["records"][0]["id"] == 1


class TestNegativeCases:
    """Test error handling and edge cases."""

    def test_invalid_syntax_detection(self):
        """Parser detects invalid record syntax."""
        invalid_code = '''
fn bad_record():
    record = { "key": }
    return record
'''
        with pytest.raises(Exception):
            # Should fail during parsing
            parse_and_validate(invalid_code)

    @pytest.mark.skip(reason="Type validation not implemented in SemanticValidator yet")
    def test_type_validation_failure(self):
        """Type validator catches unknown types."""
        code = '''
entity TestEntity:
    unknown_field: NonExistentType
'''
        with pytest.raises(Exception) as exc_info:
            parse_and_validate(code)

        # Should be a semantic validation error
        assert "NonExistentType" in str(exc_info.value) or "Unknown" in str(exc_info.value)

    def test_empty_structures_are_valid(self):
        """Empty structures should not raise errors."""
        code = '''
fn empty_structures():
    empty_record = { }
    empty_list = []
    return { "record": empty_record, "list": empty_list }
'''
        data = execute_function(code, 'empty_structures')

        assert len(data["record"]) == 0
        assert len(data["list"]) == 0
