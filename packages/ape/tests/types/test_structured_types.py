"""
Test Suite for APE Structured Types (v1.0.0 Scaffold)

Tests for List<T>, Map<K,V>, Record, and Tuple types.

Author: David Van Aelst
Status: Scaffold - tests skipped pending implementation
"""

import pytest
from ape.types import ApeList, ApeMap, ApeRecord, ApeTuple


@pytest.mark.skip(reason="v1.0.0 scaffold - List<T> implementation pending")
class TestApeList:
    """Test cases for ApeList<T> type"""
    
    def test_list_creation(self):
        """Test creating a typed list"""
        int_list = ApeList(int, [1, 2, 3])
        assert int_list.length() == 3
    
    def test_list_indexing(self):
        """Test list element access by index"""
        str_list = ApeList(str, ["hello", "world"])
        assert str_list[0] == "hello"
        assert str_list[1] == "world"
    
    def test_list_append(self):
        """Test appending items to list"""
        int_list = ApeList(int, [1, 2])
        int_list.append(3)
        assert int_list.length() == 3
        assert int_list[2] == 3
    
    def test_list_type_violation(self):
        """Test that type violations are caught"""
        int_list = ApeList(int, [1, 2, 3])
        with pytest.raises(TypeError):
            int_list.append("string")  # Should fail - wrong type
    
    def test_list_bounds_checking(self):
        """Test index out of bounds"""
        int_list = ApeList(int, [1, 2, 3])
        with pytest.raises(IndexError):
            _ = int_list[10]


@pytest.mark.skip(reason="v1.0.0 scaffold - Map<K,V> implementation pending")
class TestApeMap:
    """Test cases for ApeMap<K, V> type"""
    
    def test_map_creation(self):
        """Test creating a typed map"""
        scores = ApeMap(str, int, {"Alice": 100, "Bob": 95})
        assert scores.has("Alice")
    
    def test_map_get(self):
        """Test retrieving values by key"""
        scores = ApeMap(str, int, {"Alice": 100})
        assert scores["Alice"] == 100
    
    def test_map_set(self):
        """Test setting key-value pairs"""
        scores = ApeMap(str, int, {})
        scores.set("Charlie", 90)
        assert scores["Charlie"] == 90
    
    def test_map_key_not_found(self):
        """Test accessing non-existent key"""
        scores = ApeMap(str, int, {})
        with pytest.raises(KeyError):
            _ = scores["Missing"]
    
    def test_map_type_violation(self):
        """Test that type violations are caught"""
        scores = ApeMap(str, int, {})
        with pytest.raises(TypeError):
            scores.set("Alice", "not an integer")


@pytest.mark.skip(reason="v1.0.0 scaffold - Record implementation pending")
class TestApeRecord:
    """Test cases for ApeRecord type"""
    
    def test_record_creation(self):
        """Test creating a record with named fields"""
        person = ApeRecord(
            fields={"name": str, "age": int, "email": str},
            values={"name": "Alice", "age": 30, "email": "alice@example.com"}
        )
        assert person.name == "Alice"
    
    def test_record_field_access(self):
        """Test accessing record fields"""
        person = ApeRecord(
            fields={"name": str, "age": int},
            values={"name": "Bob", "age": 25}
        )
        assert person.name == "Bob"
        assert person.age == 25
    
    def test_record_type_violation(self):
        """Test that field type violations are caught"""
        person = ApeRecord(
            fields={"name": str, "age": int},
            values={"name": "Charlie", "age": 30}
        )
        with pytest.raises(TypeError):
            person.age = "not an integer"


@pytest.mark.skip(reason="v1.0.0 scaffold - Tuple implementation pending")
class TestApeTuple:
    """Test cases for ApeTuple type"""
    
    def test_tuple_creation(self):
        """Test creating a typed tuple"""
        point = ApeTuple(types=(int, int), values=(10, 20))
        assert len(point) == 2
    
    def test_tuple_indexing(self):
        """Test tuple element access"""
        result = ApeTuple(
            types=(str, bool, int),
            values=("success", True, 42)
        )
        assert result[0] == "success"
        assert result[1] is True
        assert result[2] == 42
    
    def test_tuple_immutability(self):
        """Test that tuples cannot be modified"""
        point = ApeTuple(types=(int, int), values=(10, 20))
        with pytest.raises(TypeError):
            point[0] = 15  # Should fail - tuples are immutable
