"""
DateTime and Duration runtime tests for APE Decision Engine.

Tests verify:
- DateTime operations (now, arithmetic, comparisons)
- Duration semantics (days, hours, minutes)
- ISO-8601 serialization
- Deterministic behavior
"""
import pytest
from datetime import datetime, timezone
from ape.types import ApeDateTime, ApeDuration
from ape.std import datetime as datetime_module


class TestDateTimeBasics:
    """Test DateTime type runtime behavior."""
    
    def test_now_returns_utc(self):
        """now() returns UTC datetime."""
        dt = datetime_module.now()
        
        assert isinstance(dt, ApeDateTime)
        # Should be close to current time
        now_utc = datetime.now(timezone.utc)
        diff = abs((dt._dt - now_utc).total_seconds())
        assert diff < 2  # Within 2 seconds
    
    def test_iso8601_serialization(self):
        """DateTime serializes to ISO-8601 format."""
        dt = ApeDateTime.now()
        iso_string = dt.to_iso8601()
        
        assert isinstance(iso_string, str)
        assert iso_string.endswith('Z')  # UTC marker
        assert 'T' in iso_string  # Date/time separator
    
    def test_parse_iso8601(self):
        """Can parse ISO-8601 strings."""
        iso_string = "2024-12-17T10:30:00Z"
        dt = datetime_module.parse_iso8601(iso_string)
        
        assert isinstance(dt, ApeDateTime)
        assert dt._dt.year == 2024
        assert dt._dt.month == 12
        assert dt._dt.day == 17
        assert dt._dt.hour == 10
        assert dt._dt.minute == 30


class TestDateTimeArithmetic:
    """Test DateTime arithmetic operations."""
    
    def test_subtract_days(self):
        """Can subtract days from DateTime."""
        dt = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        past = datetime_module.subtract_days(dt, 5)
        
        assert isinstance(past, ApeDateTime)
        assert past._dt.day == 12
    
    def test_add_days(self):
        """Can add days to DateTime."""
        dt = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        future = datetime_module.add_days(dt, 3)
        
        assert isinstance(future, ApeDateTime)
        assert future._dt.day == 20
    
    def test_add_negative_days(self):
        """Adding negative days goes backward."""
        dt = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        past = datetime_module.add_days(dt, -2)
        
        assert past._dt.day == 15


class TestDateTimeComparisons:
    """Test DateTime comparison operations."""
    
    def test_compare_earlier(self):
        """Earlier dates compare as less than."""
        dt1 = datetime_module.parse_iso8601("2024-12-15T00:00:00Z")
        dt2 = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        
        result = datetime_module.compare(dt1, dt2)
        assert result < 0  # dt1 is earlier
    
    def test_compare_later(self):
        """Later dates compare as greater than."""
        dt1 = datetime_module.parse_iso8601("2024-12-20T00:00:00Z")
        dt2 = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        
        result = datetime_module.compare(dt1, dt2)
        assert result > 0  # dt1 is later
    
    def test_compare_equal(self):
        """Same dates compare as equal."""
        dt1 = datetime_module.parse_iso8601("2024-12-17T10:00:00Z")
        dt2 = datetime_module.parse_iso8601("2024-12-17T10:00:00Z")
        
        result = datetime_module.compare(dt1, dt2)
        assert result == 0


class TestDuration:
    """Test Duration type runtime behavior."""
    
    def test_days_duration(self):
        """days() creates Duration with correct value."""
        duration = datetime_module.days(5)
        
        assert isinstance(duration, ApeDuration)
        # 5 days = 432000 seconds
        assert duration.to_seconds() == 5 * 24 * 60 * 60
    
    def test_hours_duration(self):
        """hours() creates Duration with correct value."""
        duration = datetime_module.hours(3)
        
        assert isinstance(duration, ApeDuration)
        # 3 hours = 10800 seconds
        assert duration.to_seconds() == 3 * 60 * 60
    
    def test_duration_serialization(self):
        """Duration serializes to seconds (int)."""
        duration = ApeDuration.from_days(2)
        seconds = duration.to_seconds()
        
        assert isinstance(seconds, int)
        assert seconds == 2 * 24 * 60 * 60


class TestDeterminism:
    """Test deterministic behavior of DateTime operations."""
    
    def test_parse_deterministic(self):
        """Parsing same ISO string gives same result."""
        iso = "2024-12-17T12:00:00Z"
        dt1 = datetime_module.parse_iso8601(iso)
        dt2 = datetime_module.parse_iso8601(iso)
        
        assert dt1.to_iso8601() == dt2.to_iso8601()
    
    def test_arithmetic_deterministic(self):
        """Same arithmetic operations give same results."""
        base = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        
        result1 = datetime_module.add_days(base, 7)
        result2 = datetime_module.add_days(base, 7)
        
        assert result1.to_iso8601() == result2.to_iso8601()
    
    def test_comparison_deterministic(self):
        """Same comparisons give same results."""
        dt1 = datetime_module.parse_iso8601("2024-12-15T00:00:00Z")
        dt2 = datetime_module.parse_iso8601("2024-12-17T00:00:00Z")
        
        comp1 = datetime_module.compare(dt1, dt2)
        comp2 = datetime_module.compare(dt1, dt2)
        
        assert comp1 == comp2


class TestNegativeCases:
    """Test error handling for DateTime operations."""
    
    def test_invalid_iso8601_format(self):
        """Invalid ISO-8601 format raises error."""
        with pytest.raises(ValueError):
            datetime_module.parse_iso8601("not-a-date")
    
    def test_invalid_iso8601_missing_timezone(self):
        """ISO-8601 without timezone marker raises error."""
        with pytest.raises(ValueError):
            datetime_module.parse_iso8601("2024-12-17T10:00:00")
    
    def test_duration_edge_cases(self):
        """Duration handles zero and negative values."""
        # Zero duration
        zero = datetime_module.days(0)
        assert zero.to_seconds() == 0
        
        # Negative duration (should work for subtraction)
        negative = datetime_module.days(-1)
        assert negative.to_seconds() == -24 * 60 * 60


class TestRuntimeIntegration:
    """Test DateTime integration with APE runtime."""
    
    def test_datetime_in_record(self):
        """DateTime can be stored in records."""
        dt = datetime_module.now()
        record = {
            "timestamp": dt.to_iso8601(),
            "value": 42
        }
        
        assert isinstance(record["timestamp"], str)
        assert record["timestamp"].endswith('Z')
    
    def test_duration_in_calculations(self):
        """Duration works in time-based calculations."""
        base = datetime_module.parse_iso8601("2024-12-01T00:00:00Z")
        offset = datetime_module.days(10)
        
        # Manual calculation: add duration's seconds
        future_dt = base._dt.timestamp() + offset.to_seconds()
        
        # Should be Dec 11
        from datetime import datetime as dt_class
        result = dt_class.fromtimestamp(future_dt, tz=timezone.utc)
        assert result.day == 11
