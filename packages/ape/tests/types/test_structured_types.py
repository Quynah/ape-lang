"""
Test Suite for APE Structured Types

Tests for List<T>, Map<K,V>, Record, and Tuple types.

Author: David Van Aelst
Status: Lists and Tuples are production-ready; Map and Record are scaffolded
"""

import pytest
from ape.types import ApeList, ApeMap, ApeRecord, ApeTuple


class TestApeList:
    """Test cases for ApeList<T> type"""
    
    def test_list_creation(self):
        """Test creating a list"""
        int_list = ApeList([1, 2, 3])
        assert len(int_list) == 3
    
    def test_list_indexing(self):
        """Test list element access by index"""
        str_list = ApeList(["hello", "world"])
        assert str_list[0] == "hello"
        assert str_list[1] == "world"
    
    def test_list_empty(self):
        """Test empty list creation"""
        empty_list = ApeList()
        assert len(empty_list) == 0
    
    def test_list_iteration(self):
        """Test iterating over list"""
        int_list = ApeList([1, 2, 3])
        items = []
        for item in int_list:
            items.append(item)
        assert items == [1, 2, 3]
    
    def test_list_membership(self):
        """Test membership testing (in operator)"""
        int_list = ApeList([1, 2, 3])
        assert 2 in int_list
        assert 5 not in int_list
    
    def test_list_equality(self):
        """Test value-based equality"""
        list1 = ApeList([1, 2, 3])
        list2 = ApeList([1, 2, 3])
        list3 = ApeList([3, 2, 1])
        assert list1 == list2
        assert list1 != list3
    
    def test_list_concatenation(self):
        """Test list concatenation"""
        list1 = ApeList([1, 2])
        list2 = ApeList([3, 4])
        list3 = list1 + list2
        assert len(list3) == 4
        assert list3[0] == 1
        assert list3[3] == 4
    
    def test_list_bounds_checking(self):
        """Test index out of bounds"""
        int_list = ApeList([1, 2, 3])
        with pytest.raises(IndexError):
            _ = int_list[10]
    
    def test_list_invalid_index_type(self):
        """Test that non-integer indices raise TypeError"""
        int_list = ApeList([1, 2, 3])
        with pytest.raises(TypeError):
            _ = int_list["invalid"]


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


class TestApeTuple:
    """Test cases for ApeTuple type"""
    
    def test_tuple_creation(self):
        """Test creating a tuple"""
        point = ApeTuple((10, 20))
        assert len(point) == 2
    
    def test_tuple_indexing(self):
        """Test tuple element access"""
        result = ApeTuple(("success", True, 42))
        assert result[0] == "success"
        assert result[1] is True
        assert result[2] == 42
    
    def test_tuple_iteration(self):
        """Test iterating over tuple"""
        point = ApeTuple((10, 20, 30))
        items = []
        for item in point:
            items.append(item)
        assert items == [10, 20, 30]
    
    def test_tuple_equality(self):
        """Test value-based equality"""
        tuple1 = ApeTuple((1, 2, 3))
        tuple2 = ApeTuple((1, 2, 3))
        tuple3 = ApeTuple((3, 2, 1))
        assert tuple1 == tuple2
        assert tuple1 != tuple3
    
    def test_tuple_hashable(self):
        """Test that tuples are hashable"""
        tuple1 = ApeTuple((1, 2, 3))
        tuple2 = ApeTuple((1, 2, 3))
        # Should be able to use in set/dict
        s = {tuple1, tuple2}
        assert len(s) == 1  # Same values, so only one in set
    
    def test_tuple_bounds_checking(self):
        """Test index out of bounds"""
        point = ApeTuple((10, 20))
        with pytest.raises(IndexError):
            _ = point[10]
    
    def test_tuple_invalid_index_type(self):
        """Test that non-integer indices raise TypeError"""
        point = ApeTuple((10, 20))
        with pytest.raises(TypeError):
            _ = point["invalid"]
