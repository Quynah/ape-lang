"""
Nested data access runtime tests for APE Decision Engine.

Tests verify:
- json.get with dotted path notation
- json.has_path for path existence
- json.set for immutable updates
- json.flatten for nested structures
- Works with Record, Map, nested combinations
"""
import pytest
from ape.std import json


class TestJsonGet:
    """Test json.get dotted path access."""
    
    def test_simple_path(self):
        """get retrieves simple nested values."""
        data = {
            "user": {
                "name": "Alice"
            }
        }
        
        result = json.get(data, "user.name")
        assert result == "Alice"
    
    def test_deep_nested_path(self):
        """get retrieves deeply nested values."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": 42
                    }
                }
            }
        }
        
        result = json.get(data, "level1.level2.level3.value")
        assert result == 42
    
    def test_missing_path_returns_default(self):
        """get returns default for missing paths."""
        data = {"a": {"b": 1}}
        
        result = json.get(data, "a.c", default="not_found")
        assert result == "not_found"
    
    def test_missing_path_none_default(self):
        """get returns None by default for missing paths."""
        data = {"a": 1}
        
        result = json.get(data, "b.c")
        assert result is None
    
    def test_array_index_access(self):
        """get can access list elements by index."""
        data = {
            "items": [
                {"id": 1},
                {"id": 2}
            ]
        }
        
        result = json.get(data, "items.0.id")
        assert result == 1
        
        result = json.get(data, "items.1.id")
        assert result == 2
    
    def test_mixed_dict_list_access(self):
        """get handles mixed dict/list structures."""
        data = {
            "users": [
                {"name": "Alice", "tags": ["admin", "user"]},
                {"name": "Bob", "tags": ["user"]}
            ]
        }
        
        result = json.get(data, "users.0.tags.0")
        assert result == "admin"


class TestJsonHasPath:
    """Test json.has_path for path existence."""
    
    def test_existing_path_returns_true(self):
        """has_path returns True for existing paths."""
        data = {"a": {"b": {"c": 1}}}
        
        assert json.has_path(data, "a.b.c") is True
    
    def test_missing_path_returns_false(self):
        """has_path returns False for missing paths."""
        data = {"a": {"b": 1}}
        
        assert json.has_path(data, "a.c") is False
        assert json.has_path(data, "x.y.z") is False
    
    def test_partial_path_exists(self):
        """has_path checks full path, not partial."""
        data = {"a": {"b": 1}}
        
        assert json.has_path(data, "a") is True
        assert json.has_path(data, "a.b") is True
        assert json.has_path(data, "a.b.c") is False
    
    def test_has_path_with_lists(self):
        """has_path works with list indices."""
        data = {"items": [{"id": 1}, {"id": 2}]}
        
        assert json.has_path(data, "items.0.id") is True
        assert json.has_path(data, "items.5.id") is False


class TestJsonSet:
    """Test json.set for immutable updates."""
    
    def test_set_creates_nested_structure(self):
        """set creates nested paths if they don't exist."""
        data = {}
        
        result = json.set(data, "a.b.c", 42)
        
        assert result["a"]["b"]["c"] == 42
        # Original unchanged (immutable)
        assert data == {}
    
    def test_set_updates_existing_value(self):
        """set updates existing values."""
        data = {"a": {"b": 1}}
        
        result = json.set(data, "a.b", 2)
        
        assert result["a"]["b"] == 2
        # Original unchanged
        assert data["a"]["b"] == 1
    
    def test_set_preserves_other_keys(self):
        """set preserves other keys in structure."""
        data = {
            "a": {"b": 1, "c": 2},
            "d": 3
        }
        
        result = json.set(data, "a.b", 10)
        
        assert result["a"]["b"] == 10
        assert result["a"]["c"] == 2
        assert result["d"] == 3
    
    def test_set_with_lists(self):
        """set can update list elements."""
        data = {"items": [1, 2, 3]}
        
        result = json.set(data, "items.1", 20)
        
        assert result["items"] == [1, 20, 3]
        assert data["items"] == [1, 2, 3]  # Original unchanged


class TestJsonFlatten:
    """Test json.flatten for nested structures."""
    
    def test_flatten_nested_dict(self):
        """flatten converts nested dict to flat keys."""
        data = {
            "a": {
                "b": {
                    "c": 1
                }
            }
        }
        
        result = json.flatten(data)
        
        assert "a.b.c" in result
        assert result["a.b.c"] == 1
    
    def test_flatten_mixed_structure(self):
        """flatten handles mixed nested structures."""
        data = {
            "user": {
                "name": "Alice",
                "address": {
                    "city": "Amsterdam"
                }
            },
            "active": True
        }
        
        result = json.flatten(data)
        
        assert result["user.name"] == "Alice"
        assert result["user.address.city"] == "Amsterdam"
        assert result["active"] is True
    
    def test_flatten_with_lists(self):
        """flatten includes list indices in keys."""
        data = {
            "items": [
                {"id": 1},
                {"id": 2}
            ]
        }
        
        result = json.flatten(data)
        
        assert "items.0.id" in result
        assert "items.1.id" in result
        assert result["items.0.id"] == 1


class TestComplexScenarios:
    """Test json functions with complex real-world structures."""
    
    def test_api_response_access(self):
        """Simulate accessing nested API response data."""
        api_response = {
            "status": "success",
            "data": {
                "user": {
                    "id": 123,
                    "profile": {
                        "email": "alice@example.com",
                        "preferences": {
                            "notifications": True
                        }
                    }
                }
            }
        }
        
        # Access deeply nested value
        email = json.get(api_response, "data.user.profile.email")
        assert email == "alice@example.com"
        
        # Check path exists
        assert json.has_path(api_response, "data.user.profile.preferences.notifications")
        
        # Access with default
        timezone = json.get(api_response, "data.user.profile.timezone", default="UTC")
        assert timezone == "UTC"
    
    def test_configuration_access(self):
        """Simulate accessing configuration data."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin"
                }
            },
            "features": {
                "logging": True,
                "cache": {"enabled": True, "ttl": 300}
            }
        }
        
        # Check feature flags
        assert json.has_path(config, "features.logging")
        assert json.get(config, "features.logging") is True
        
        # Get cache TTL with default
        ttl = json.get(config, "features.cache.ttl", default=600)
        assert ttl == 300
    
    def test_update_nested_config(self):
        """Simulate updating nested configuration."""
        config = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0"
            }
        }
        
        # Update version
        updated = json.set(config, "app.version", "1.0.1")
        assert updated["app"]["version"] == "1.0.1"
        
        # Add new nested key
        updated = json.set(config, "app.build.number", 42)
        assert updated["app"]["build"]["number"] == 42


class TestNegativeCases:
    """Test error handling and edge cases."""
    
    def test_get_on_non_dict(self):
        """get handles non-dict values gracefully."""
        data = {"a": "string_value"}
        
        # Trying to access path on string returns default
        result = json.get(data, "a.b.c", default="not_found")
        assert result == "not_found"
    
    def test_get_on_none_value(self):
        """get handles None values in path."""
        data = {"a": None}
        
        result = json.get(data, "a.b", default="default")
        assert result == "default"
    
    def test_invalid_list_index(self):
        """get handles invalid list indices gracefully."""
        data = {"items": [1, 2, 3]}
        
        result = json.get(data, "items.10", default="out_of_range")
        assert result == "out_of_range"
    
    def test_empty_path(self):
        """get with empty path returns original data."""
        data = {"a": 1}
        
        result = json.get(data, "")
        assert result == data
    
    def test_has_path_on_empty_data(self):
        """has_path on empty dict returns False."""
        assert json.has_path({}, "a.b.c") is False
    
    def test_flatten_empty_dict(self):
        """flatten on empty dict returns empty dict."""
        result = json.flatten({})
        assert result == {}
    
    def test_set_immutability(self):
        """set does not modify original data."""
        original = {"a": {"b": 1}}
        original_copy = {"a": {"b": 1}}
        
        modified = json.set(original, "a.b", 2)
        
        # Original unchanged
        assert original == original_copy
        # Modified has new value
        assert modified["a"]["b"] == 2
