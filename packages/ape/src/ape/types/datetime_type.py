"""
APE DateTime and Duration Types

Decision Engine datetime primitives for temporal operations.

Author: David Van Aelst
Status: Decision Engine v2024
"""

from datetime import datetime, timedelta
from typing import Union
from dataclasses import dataclass


@dataclass
class ApeDateTime:
    """
    DateTime type for APE - immutable temporal point.
    
    Always UTC, always ISO-8601 serializable.
    Runtime contract: DateTime → ISO-8601 UTC string
    
    Example:
        now = ApeDateTime.now()
        parsed = ApeDateTime.parse_iso8601("2024-05-08T12:00:00Z")
    """
    _dt: datetime
    
    def __post_init__(self):
        # Ensure UTC
        if self._dt.tzinfo is None:
            import warnings
            warnings.warn("DateTime created without timezone, assuming UTC")
    
    @classmethod
    def now(cls) -> 'ApeDateTime':
        """Get current UTC time."""
        from datetime import timezone
        return cls(datetime.now(timezone.utc))
    
    @classmethod
    def parse_iso8601(cls, iso_string: str) -> 'ApeDateTime':
        """
        Parse ISO-8601 string to DateTime.
        
        Args:
            iso_string: ISO-8601 formatted string (e.g., "2024-05-08T12:00:00Z")
        
        Returns:
            ApeDateTime instance
        """
        # Handle Z suffix (UTC)
        if iso_string.endswith('Z'):
            iso_string = iso_string[:-1] + '+00:00'
        
        return cls(datetime.fromisoformat(iso_string))
    
    def to_iso8601(self) -> str:
        """Convert to ISO-8601 string (UTC)."""
        return self._dt.isoformat().replace('+00:00', 'Z')
    
    def subtract_days(self, days: int) -> 'ApeDateTime':
        """Subtract days from this datetime."""
        return ApeDateTime(self._dt - timedelta(days=days))
    
    def subtract_hours(self, hours: int) -> 'ApeDateTime':
        """Subtract hours from this datetime."""
        return ApeDateTime(self._dt - timedelta(hours=hours))
    
    def add_days(self, days: int) -> 'ApeDateTime':
        """Add days to this datetime."""
        return ApeDateTime(self._dt + timedelta(days=days))
    
    def add_hours(self, hours: int) -> 'ApeDateTime':
        """Add hours to this datetime."""
        return ApeDateTime(self._dt + timedelta(hours=hours))
    
    def compare(self, other: 'ApeDateTime') -> int:
        """
        Compare two datetimes.
        
        Returns:
            -1 if self < other
             0 if self == other
             1 if self > other
        """
        if self._dt < other._dt:
            return -1
        elif self._dt > other._dt:
            return 1
        else:
            return 0
    
    def __lt__(self, other: 'ApeDateTime') -> bool:
        return self._dt < other._dt
    
    def __le__(self, other: 'ApeDateTime') -> bool:
        return self._dt <= other._dt
    
    def __gt__(self, other: 'ApeDateTime') -> bool:
        return self._dt > other._dt
    
    def __ge__(self, other: 'ApeDateTime') -> bool:
        return self._dt >= other._dt
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ApeDateTime):
            return False
        return self._dt == other._dt
    
    def __str__(self) -> str:
        return self.to_iso8601()
    
    def __repr__(self) -> str:
        return f"ApeDateTime({self.to_iso8601()})"


@dataclass
class ApeDuration:
    """
    Duration type for APE - immutable time span.
    
    Runtime contract: Duration → seconds (int)
    
    Example:
        d = ApeDuration.days(7)
        h = ApeDuration.hours(48)
    """
    _td: timedelta
    
    @classmethod
    def days(cls, n: int) -> 'ApeDuration':
        """Create duration from days."""
        return cls(timedelta(days=n))
    
    @classmethod
    def hours(cls, n: int) -> 'ApeDuration':
        """Create duration from hours."""
        return cls(timedelta(hours=n))
    
    @classmethod
    def minutes(cls, n: int) -> 'ApeDuration':
        """Create duration from minutes."""
        return cls(timedelta(minutes=n))
    
    @classmethod
    def seconds(cls, n: int) -> 'ApeDuration':
        """Create duration from seconds."""
        return cls(timedelta(seconds=n))
    
    def total_seconds(self) -> int:
        """Get total seconds."""
        return int(self._td.total_seconds())
    
    def total_days(self) -> int:
        """Get total days (truncated)."""
        return self._td.days
    
    def __str__(self) -> str:
        return f"{self.total_seconds()}s"
    
    def __repr__(self) -> str:
        return f"ApeDuration({self.total_seconds()}s)"


# Datetime functions for std.datetime module
def datetime_now() -> ApeDateTime:
    """Get current UTC time."""
    return ApeDateTime.now()


def datetime_parse_iso8601(iso_string: str) -> ApeDateTime:
    """Parse ISO-8601 string to DateTime."""
    return ApeDateTime.parse_iso8601(iso_string)


def datetime_subtract_days(dt: ApeDateTime, days: int) -> ApeDateTime:
    """Subtract days from datetime."""
    return dt.subtract_days(days)


def datetime_subtract_hours(dt: ApeDateTime, hours: int) -> ApeDateTime:
    """Subtract hours from datetime."""
    return dt.subtract_hours(hours)


def datetime_add_days(dt: ApeDateTime, days: int) -> ApeDateTime:
    """Add days to datetime."""
    return dt.add_days(days)


def datetime_add_hours(dt: ApeDateTime, hours: int) -> ApeDateTime:
    """Add hours to datetime."""
    return dt.add_hours(hours)


def datetime_compare(dt1: ApeDateTime, dt2: ApeDateTime) -> int:
    """Compare two datetimes (-1, 0, 1)."""
    return dt1.compare(dt2)


def duration_days(n: int) -> ApeDuration:
    """Create duration from days."""
    return ApeDuration.days(n)


def duration_hours(n: int) -> ApeDuration:
    """Create duration from hours."""
    return ApeDuration.hours(n)


__all__ = [
    'ApeDateTime', 'ApeDuration',
    'datetime_now', 'datetime_parse_iso8601',
    'datetime_subtract_days', 'datetime_subtract_hours',
    'datetime_add_days', 'datetime_add_hours',
    'datetime_compare',
    'duration_days', 'duration_hours'
]
