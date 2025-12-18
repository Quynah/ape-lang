"""
Test Suite for APE JSON Module

Tests for JSON parsing, serialization, and manipulation.

Author: David Van Aelst
Status: Complete - Production Ready
"""

import pytest
from ape.std import json


class TestJSONParsing:
    """Test cases for JSON parsing"""
    
    def test_parse_object(self):
        """Test parsing JSON object"""
        data = json.parse('{"name": "Alice", "age": 30}')
        assert data["name"] == "Alice"
        assert data["age"] == 30
    
    def test_parse_array(self):
        """Test parsing JSON array"""
        data = json.parse('[1, 2, 3]')
        assert data == [1, 2, 3]
    
    def test_parse_nested(self):
        """Test parsing nested JSON structures"""
        data = json.parse('{"user": {"name": "Bob", "address": {"city": "NYC"}}}')
        assert data["user"]["name"] == "Bob"
        assert data["user"]["address"]["city"] == "NYC"
    
    def test_parse_malformed(self):
        """Test parsing malformed JSON raises error"""
        with pytest.raises(ValueError, match="Invalid JSON"):
            json.parse('{"name": "Alice"')  # Missing closing brace


class TestJSONSerialization:
    """Test cases for JSON serialization"""
    
    def test_stringify_object(self):
        """Test serializing object to JSON"""
        data = {"name": "Alice", "age": 30}
        result = json.stringify(data)
        assert '"name"' in result
        assert '"Alice"' in result
        assert '30' in result
    
    def test_stringify_array(self):
        """Test serializing array to JSON"""
        data = [1, 2, 3]
        result = json.stringify(data)
        assert result == '[1, 2, 3]'
    
    def test_stringify_with_indent(self):
        """Test pretty-printing with indentation"""
        data = {"name": "Alice"}
        result = json.stringify(data, indent=2)
        assert '\n' in result  # Should have newlines when indented


class TestJSONPathAccess:
    """Test cases for path-based JSON access"""
    
    def test_get_nested_value(self):
        """Test getting nested value with dot notation"""
        data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        assert json.get(data, "user.name") == "Alice"
        assert json.get(data, "user.address.city") == "NYC"
    
    def test_get_with_default(self):
        """Test get with default value for missing path"""
        data = {"user": {"name": "Alice"}}
        assert json.get(data, "user.phone", "N/A") == "N/A"
        assert json.get(data, "missing.path", None) is None
    
    def test_set_nested_value(self):
        """Test setting nested value with dot notation"""
        data = {"user": {"name": "Alice"}}
        result = json.set(data, "user.email", "alice@example.com")
        assert result["user"]["email"] == "alice@example.com"
        assert result["user"]["name"] == "Alice"  # Original value preserved
    
    def test_has_path(self):
        """Test checking path existence"""
        data = {"user": {"name": "Alice"}}
        assert json.has_path(data, "user.name") is True
        assert json.has_path(data, "user.email") is False
        assert json.has_path(data, "missing") is False
