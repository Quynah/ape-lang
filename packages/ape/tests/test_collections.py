"""
Collection and aggregation runtime tests for APE Decision Engine.

Tests verify:
- group_by, unique, count
- sum_values, max_value, min_value
- any_match, all_match
- reduce, sort, reverse
- Generic data handling
"""
import pytest
from ape.std import collections


class TestGrouping:
    """Test group_by collection function."""
    
    def test_group_by_simple_key(self):
        """group_by categorizes records by key function."""
        records = [
            {"department": "A", "score": 10},
            {"department": "B", "score": 20},
            {"department": "A", "score": 15}
        ]
        
        result = collections.group_by(records, lambda r: r["department"])
        
        assert "A" in result
        assert "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        assert result["A"][0]["score"] == 10
        assert result["A"][1]["score"] == 15
    
    def test_group_by_numeric_key(self):
        """group_by works with numeric keys."""
        items = [
            {"value": 1, "category": 1},
            {"value": 2, "category": 2},
            {"value": 3, "category": 1}
        ]
        
        result = collections.group_by(items, lambda x: x["category"])
        
        assert 1 in result
        assert 2 in result
        assert len(result[1]) == 2
    
    def test_group_by_empty_list(self):
        """group_by on empty list returns empty dict."""
        result = collections.group_by([], lambda x: x)
        assert result == {}


class TestUnique:
    """Test unique collection function."""
    
    def test_unique_removes_duplicates(self):
        """unique removes duplicate values."""
        items = [1, 2, 3, 2, 1, 4]
        result = collections.unique(items)
        
        assert len(result) == 4
        assert set(result) == {1, 2, 3, 4}
    
    def test_unique_preserves_order(self):
        """unique preserves first occurrence order."""
        items = [3, 1, 2, 1, 3]
        result = collections.unique(items)
        
        # First occurrences: 3, 1, 2
        assert result == [3, 1, 2]
    
    def test_unique_strings(self):
        """unique works with strings."""
        items = ["a", "b", "a", "c", "b"]
        result = collections.unique(items)
        
        assert len(result) == 3
        assert set(result) == {"a", "b", "c"}


class TestAggregations:
    """Test aggregation functions."""
    
    def test_sum_values(self):
        """sum_values adds numeric values."""
        items = [1, 2, 3, 4, 5]
        result = collections.sum_values(items)
        
        assert result == 15
    
    def test_max_value(self):
        """max_value finds maximum."""
        items = [10, 5, 20, 15]
        result = collections.max_value(items)
        
        assert result == 20
    
    def test_min_value(self):
        """min_value finds minimum."""
        items = [10, 5, 20, 15]
        result = collections.min_value(items)
        
        assert result == 5
    
    def test_aggregations_with_floats(self):
        """Aggregations work with floats."""
        items = [1.5, 2.3, 0.7]
        
        assert collections.sum_values(items) == pytest.approx(4.5)
        assert collections.max_value(items) == 2.3
        assert collections.min_value(items) == 0.7


class TestPredicates:
    """Test any_match and all_match predicate functions."""
    
    def test_any_match_true(self):
        """any_match returns True if any element matches."""
        items = [1, 2, 3, 4, 5]
        result = collections.any_match(items, lambda x: x > 4)
        
        assert result is True
    
    def test_any_match_false(self):
        """any_match returns False if no elements match."""
        items = [1, 2, 3]
        result = collections.any_match(items, lambda x: x > 10)
        
        assert result is False
    
    def test_all_match_true(self):
        """all_match returns True if all elements match."""
        items = [2, 4, 6, 8]
        result = collections.all_match(items, lambda x: x % 2 == 0)
        
        assert result is True
    
    def test_all_match_false(self):
        """all_match returns False if any element doesn't match."""
        items = [2, 4, 5, 8]
        result = collections.all_match(items, lambda x: x % 2 == 0)
        
        assert result is False
    
    def test_any_match_empty_list(self):
        """any_match on empty list returns False."""
        result = collections.any_match([], lambda x: True)
        assert result is False
    
    def test_all_match_empty_list(self):
        """all_match on empty list returns True (vacuous truth)."""
        result = collections.all_match([], lambda x: False)
        assert result is True


class TestTransformations:
    """Test reduce, sort, reverse transformations."""
    
    def test_reduce_sum(self):
        """reduce can sum values."""
        items = [1, 2, 3, 4]
        result = collections.reduce(items, lambda acc, x: acc + x, 0)
        
        assert result == 10
    
    def test_reduce_product(self):
        """reduce can multiply values."""
        items = [2, 3, 4]
        result = collections.reduce(items, lambda acc, x: acc * x, 1)
        
        assert result == 24
    
    def test_reduce_with_initial(self):
        """reduce uses initial value correctly."""
        items = [1, 2, 3]
        result = collections.reduce(items, lambda acc, x: acc + x, 100)
        
        assert result == 106
    
    def test_sort_ascending(self):
        """sort orders items ascending by default."""
        items = [3, 1, 4, 1, 5, 9, 2, 6]
        result = collections.sort(items)
        
        assert result == [1, 1, 2, 3, 4, 5, 6, 9]
    
    def test_reverse_list(self):
        """reverse reverses list order."""
        items = [1, 2, 3, 4, 5]
        result = collections.reverse(items)
        
        assert result == [5, 4, 3, 2, 1]
    
    def test_reverse_empty(self):
        """reverse on empty list returns empty list."""
        result = collections.reverse([])
        assert result == []


class TestComplexScenarios:
    """Test collections with complex data types."""
    
    def test_group_by_with_records(self):
        """Collections work with record structures."""
        records = [
            {"user": "alice", "amount": 100, "category": "food"},
            {"user": "bob", "amount": 200, "category": "travel"},
            {"user": "alice", "amount": 50, "category": "food"}
        ]
        
        by_user = collections.group_by(records, lambda r: r["user"])
        
        assert len(by_user["alice"]) == 2
        assert len(by_user["bob"]) == 1
        
        # Can aggregate within groups
        alice_total = collections.sum_values([r["amount"] for r in by_user["alice"]])
        assert alice_total == 150
    
    def test_chained_operations(self):
        """Collections can be chained."""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Filter even numbers
        evens = [x for x in items if x % 2 == 0]
        # Get unique (already unique)
        unique_evens = collections.unique(evens)
        # Sum them
        total = collections.sum_values(unique_evens)
        
        assert total == 30  # 2 + 4 + 6 + 8 + 10
    
    def test_nested_group_by(self):
        """group_by can create nested structures."""
        data = [
            {"dept": "A", "team": "X", "score": 10},
            {"dept": "A", "team": "Y", "score": 20},
            {"dept": "B", "team": "X", "score": 30}
        ]
        
        by_dept = collections.group_by(data, lambda r: r["dept"])
        
        # Group A's items by team
        a_by_team = collections.group_by(by_dept["A"], lambda r: r["team"])
        
        assert "X" in a_by_team
        assert "Y" in a_by_team
        assert a_by_team["X"][0]["score"] == 10


class TestNegativeCases:
    """Test error handling and edge cases."""
    
    def test_max_on_empty_list_raises(self):
        """max_value on empty list raises error."""
        with pytest.raises(ValueError):
            collections.max_value([])
    
    def test_min_on_empty_list_raises(self):
        """min_value on empty list raises error."""
        with pytest.raises(ValueError):
            collections.min_value([])
    
    def test_sum_on_empty_list(self):
        """sum_values on empty list returns 0."""
        result = collections.sum_values([])
        assert result == 0
    
    def test_reduce_on_empty_list(self):
        """reduce on empty list returns initial value."""
        result = collections.reduce([], lambda acc, x: acc + x, 42)
        assert result == 42
    
    def test_group_by_with_none_key(self):
        """group_by handles None keys."""
        items = [
            {"key": None, "value": 1},
            {"key": "a", "value": 2},
            {"key": None, "value": 3}
        ]
        
        result = collections.group_by(items, lambda x: x["key"])
        
        assert None in result
        assert len(result[None]) == 2
