"""
Tests for APE Standard Library v0 (Pure, Deterministic Core)

Tests all stdlib modules: logic, collections, strings, math
"""

import pytest
from ape.std import logic, collections, strings, math


class TestLogicModule:
    """Tests for std.logic module"""
    
    def test_assert_condition_true(self):
        """assert_condition should pass for true condition"""
        logic.assert_condition(True)  # Should not raise
    
    def test_assert_condition_false(self):
        """assert_condition should raise RuntimeError for false condition"""
        with pytest.raises(RuntimeError, match="Assertion failed"):
            logic.assert_condition(False)
    
    def test_assert_condition_with_message(self):
        """assert_condition should use custom message"""
        with pytest.raises(RuntimeError, match="Custom error"):
            logic.assert_condition(False, "Custom error")
    
    def test_assert_condition_type_error(self):
        """assert_condition should reject non-boolean"""
        with pytest.raises(TypeError, match="requires boolean"):
            logic.assert_condition("not a bool")
    
    def test_all_true_all_truthy(self):
        """all_true should return True when all values are truthy"""
        assert logic.all_true([True, 1, "yes", [1]]) is True
    
    def test_all_true_some_falsy(self):
        """all_true should return False when any value is falsy"""
        assert logic.all_true([True, 0, "yes"]) is False
    
    def test_all_true_empty_list(self):
        """all_true should return True for empty list"""
        assert logic.all_true([]) is True
    
    def test_all_true_type_error(self):
        """all_true should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            logic.all_true("not a list")
    
    def test_any_true_some_truthy(self):
        """any_true should return True when any value is truthy"""
        assert logic.any_true([False, 0, "", 1]) is True
    
    def test_any_true_all_falsy(self):
        """any_true should return False when all values are falsy"""
        assert logic.any_true([False, 0, "", []]) is False
    
    def test_any_true_empty_list(self):
        """any_true should return False for empty list"""
        assert logic.any_true([]) is False
    
    def test_any_true_type_error(self):
        """any_true should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            logic.any_true(42)
    
    def test_none_true_all_falsy(self):
        """none_true should return True when all values are falsy"""
        assert logic.none_true([False, 0, "", []]) is True
    
    def test_none_true_some_truthy(self):
        """none_true should return False when any value is truthy"""
        assert logic.none_true([False, 0, 1]) is False
    
    def test_none_true_empty_list(self):
        """none_true should return True for empty list"""
        assert logic.none_true([]) is True
    
    def test_none_true_type_error(self):
        """none_true should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            logic.none_true(True)
    
    def test_equals_same_values(self):
        """equals should return True for equal values"""
        assert logic.equals(42, 42) is True
        assert logic.equals("hello", "hello") is True
        assert logic.equals([1, 2], [1, 2]) is True
    
    def test_equals_different_values(self):
        """equals should return False for different values"""
        assert logic.equals(42, 43) is False
        assert logic.equals("hello", "world") is False
    
    def test_not_equals_different_values(self):
        """not_equals should return True for different values"""
        assert logic.not_equals(42, 43) is True
        assert logic.not_equals("hello", "world") is True
    
    def test_not_equals_same_values(self):
        """not_equals should return False for equal values"""
        assert logic.not_equals(42, 42) is False
        assert logic.not_equals("hello", "hello") is False


class TestCollectionsModule:
    """Tests for std.collections module"""
    
    def test_count_list(self):
        """count should return length of list"""
        assert collections.count([1, 2, 3]) == 3
        assert collections.count([]) == 0
    
    def test_count_type_error(self):
        """count should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            collections.count("not a list")
    
    def test_is_empty_empty_list(self):
        """is_empty should return True for empty list"""
        assert collections.is_empty([]) is True
    
    def test_is_empty_non_empty_list(self):
        """is_empty should return False for non-empty list"""
        assert collections.is_empty([1]) is False
    
    def test_is_empty_type_error(self):
        """is_empty should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            collections.is_empty(42)
    
    def test_contains_present(self):
        """contains should return True when value is in list"""
        assert collections.contains([1, 2, 3], 2) is True
    
    def test_contains_absent(self):
        """contains should return False when value is not in list"""
        assert collections.contains([1, 2, 3], 4) is False
    
    def test_contains_type_error(self):
        """contains should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            collections.contains("not a list", "x")
    
    def test_filter_items_basic(self):
        """filter_items should filter using predicate"""
        result = collections.filter_items([1, 2, 3, 4], lambda x: x > 2)
        assert result == [3, 4]
    
    def test_filter_items_empty_result(self):
        """filter_items should return empty list when nothing matches"""
        result = collections.filter_items([1, 2, 3], lambda x: x > 10)
        assert result == []
    
    def test_filter_items_type_error_list(self):
        """filter_items should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            collections.filter_items("not a list", lambda x: True)
    
    def test_filter_items_type_error_predicate(self):
        """filter_items should reject non-callable predicate"""
        with pytest.raises(TypeError, match="requires callable"):
            collections.filter_items([1, 2, 3], "not callable")
    
    def test_map_items_basic(self):
        """map_items should transform using function"""
        result = collections.map_items([1, 2, 3], lambda x: x * 2)
        assert result == [2, 4, 6]
    
    def test_map_items_type_conversion(self):
        """map_items should support type conversion"""
        result = collections.map_items([1, 2, 3], lambda x: str(x))
        assert result == ["1", "2", "3"]
    
    def test_map_items_type_error_list(self):
        """map_items should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            collections.map_items(42, lambda x: x)
    
    def test_map_items_type_error_transformer(self):
        """map_items should reject non-callable transformer"""
        with pytest.raises(TypeError, match="requires callable"):
            collections.map_items([1, 2, 3], 42)


class TestStringsModule:
    """Tests for std.strings module"""
    
    def test_lower_basic(self):
        """lower should convert to lowercase"""
        assert strings.lower("HELLO") == "hello"
        assert strings.lower("HeLLo") == "hello"
    
    def test_lower_already_lowercase(self):
        """lower should handle already lowercase strings"""
        assert strings.lower("hello") == "hello"
    
    def test_lower_type_error(self):
        """lower should reject non-string"""
        with pytest.raises(TypeError, match="requires string"):
            strings.lower(42)
    
    def test_upper_basic(self):
        """upper should convert to uppercase"""
        assert strings.upper("hello") == "HELLO"
        assert strings.upper("HeLLo") == "HELLO"
    
    def test_upper_already_uppercase(self):
        """upper should handle already uppercase strings"""
        assert strings.upper("HELLO") == "HELLO"
    
    def test_upper_type_error(self):
        """upper should reject non-string"""
        with pytest.raises(TypeError, match="requires string"):
            strings.upper([])
    
    def test_trim_whitespace(self):
        """trim should remove leading and trailing whitespace"""
        assert strings.trim("  hello  ") == "hello"
        assert strings.trim("\thello\n") == "hello"
    
    def test_trim_no_whitespace(self):
        """trim should handle strings without whitespace"""
        assert strings.trim("hello") == "hello"
    
    def test_trim_type_error(self):
        """trim should reject non-string"""
        with pytest.raises(TypeError, match="requires string"):
            strings.trim(None)
    
    def test_starts_with_true(self):
        """starts_with should return True when text starts with prefix"""
        assert strings.starts_with("hello world", "hello") is True
    
    def test_starts_with_false(self):
        """starts_with should return False when text doesn't start with prefix"""
        assert strings.starts_with("hello world", "world") is False
    
    def test_starts_with_type_error_text(self):
        """starts_with should reject non-string text"""
        with pytest.raises(TypeError, match="requires string for text"):
            strings.starts_with(42, "hello")
    
    def test_starts_with_type_error_prefix(self):
        """starts_with should reject non-string prefix"""
        with pytest.raises(TypeError, match="requires string for prefix"):
            strings.starts_with("hello", 42)
    
    def test_ends_with_true(self):
        """ends_with should return True when text ends with suffix"""
        assert strings.ends_with("hello world", "world") is True
    
    def test_ends_with_false(self):
        """ends_with should return False when text doesn't end with suffix"""
        assert strings.ends_with("hello world", "hello") is False
    
    def test_ends_with_type_error_text(self):
        """ends_with should reject non-string text"""
        with pytest.raises(TypeError, match="requires string for text"):
            strings.ends_with([], "world")
    
    def test_ends_with_type_error_suffix(self):
        """ends_with should reject non-string suffix"""
        with pytest.raises(TypeError, match="requires string for suffix"):
            strings.ends_with("hello", [])
    
    def test_contains_text_true(self):
        """contains_text should return True when text contains fragment"""
        assert strings.contains_text("hello world", "lo wo") is True
    
    def test_contains_text_false(self):
        """contains_text should return False when text doesn't contain fragment"""
        assert strings.contains_text("hello world", "xyz") is False
    
    def test_contains_text_type_error_text(self):
        """contains_text should reject non-string text"""
        with pytest.raises(TypeError, match="requires string for text"):
            strings.contains_text(42, "hello")
    
    def test_contains_text_type_error_fragment(self):
        """contains_text should reject non-string fragment"""
        with pytest.raises(TypeError, match="requires string for fragment"):
            strings.contains_text("hello", 42)


class TestMathModule:
    """Tests for std.math module"""
    
    def test_abs_value_positive(self):
        """abs_value should return positive number unchanged"""
        assert math.abs_value(42) == 42
        assert math.abs_value(3.14) == 3.14
    
    def test_abs_value_negative(self):
        """abs_value should convert negative to positive"""
        assert math.abs_value(-42) == 42
        assert math.abs_value(-3.14) == 3.14
    
    def test_abs_value_zero(self):
        """abs_value should return 0 for 0"""
        assert math.abs_value(0) == 0
    
    def test_abs_value_type_error(self):
        """abs_value should reject non-number"""
        with pytest.raises(TypeError, match="requires number"):
            math.abs_value("not a number")
    
    def test_min_value_first_smaller(self):
        """min_value should return first value when smaller"""
        assert math.min_value(1, 2) == 1
    
    def test_min_value_second_smaller(self):
        """min_value should return second value when smaller"""
        assert math.min_value(5, 3) == 3
    
    def test_min_value_equal(self):
        """min_value should return value when equal"""
        assert math.min_value(42, 42) == 42
    
    def test_min_value_type_error_a(self):
        """min_value should reject non-number for a"""
        with pytest.raises(TypeError, match="requires number for a"):
            math.min_value("not a number", 42)
    
    def test_min_value_type_error_b(self):
        """min_value should reject non-number for b"""
        with pytest.raises(TypeError, match="requires number for b"):
            math.min_value(42, "not a number")
    
    def test_max_value_first_larger(self):
        """max_value should return first value when larger"""
        assert math.max_value(10, 5) == 10
    
    def test_max_value_second_larger(self):
        """max_value should return second value when larger"""
        assert math.max_value(3, 7) == 7
    
    def test_max_value_equal(self):
        """max_value should return value when equal"""
        assert math.max_value(42, 42) == 42
    
    def test_max_value_type_error_a(self):
        """max_value should reject non-number for a"""
        with pytest.raises(TypeError, match="requires number for a"):
            math.max_value([], 42)
    
    def test_max_value_type_error_b(self):
        """max_value should reject non-number for b"""
        with pytest.raises(TypeError, match="requires number for b"):
            math.max_value(42, [])
    
    def test_clamp_within_range(self):
        """clamp should return value when within range"""
        assert math.clamp(5, 0, 10) == 5
    
    def test_clamp_below_range(self):
        """clamp should return min when value below range"""
        assert math.clamp(-5, 0, 10) == 0
    
    def test_clamp_above_range(self):
        """clamp should return max when value above range"""
        assert math.clamp(15, 0, 10) == 10
    
    def test_clamp_at_boundaries(self):
        """clamp should handle boundary values"""
        assert math.clamp(0, 0, 10) == 0
        assert math.clamp(10, 0, 10) == 10
    
    def test_clamp_type_error_value(self):
        """clamp should reject non-number for value"""
        with pytest.raises(TypeError, match="requires number for value"):
            math.clamp("not a number", 0, 10)
    
    def test_clamp_type_error_min(self):
        """clamp should reject non-number for min_val"""
        with pytest.raises(TypeError, match="requires number for min_val"):
            math.clamp(5, "not a number", 10)
    
    def test_clamp_type_error_max(self):
        """clamp should reject non-number for max_val"""
        with pytest.raises(TypeError, match="requires number for max_val"):
            math.clamp(5, 0, "not a number")
    
    def test_clamp_invalid_range(self):
        """clamp should reject invalid range (min > max)"""
        with pytest.raises(ValueError, match="requires min_val <= max_val"):
            math.clamp(5, 10, 0)
    
    def test_sum_values_basic(self):
        """sum_values should sum list of numbers"""
        assert math.sum_values([1, 2, 3, 4]) == 10
    
    def test_sum_values_empty_list(self):
        """sum_values should return 0 for empty list"""
        assert math.sum_values([]) == 0
    
    def test_sum_values_floats(self):
        """sum_values should handle floats"""
        assert math.sum_values([1.5, 2.5, 3.0]) == 7.0
    
    def test_sum_values_negative(self):
        """sum_values should handle negative numbers"""
        assert math.sum_values([10, -5, -3]) == 2
    
    def test_sum_values_type_error_list(self):
        """sum_values should reject non-list"""
        with pytest.raises(TypeError, match="requires list"):
            math.sum_values("not a list")
    
    def test_sum_values_type_error_element(self):
        """sum_values should reject non-number in list"""
        with pytest.raises(TypeError, match="requires all values to be numbers"):
            math.sum_values([1, 2, "not a number", 4])


class TestStdlibDeterminism:
    """Tests for stdlib determinism"""
    
    def test_same_input_same_output(self):
        """Stdlib functions should be deterministic"""
        # logic
        assert logic.equals(42, 42) == logic.equals(42, 42)
        
        # collections
        assert collections.count([1, 2, 3]) == collections.count([1, 2, 3])
        
        # strings
        assert strings.lower("HELLO") == strings.lower("HELLO")
        
        # math
        assert math.abs_value(-5) == math.abs_value(-5)
