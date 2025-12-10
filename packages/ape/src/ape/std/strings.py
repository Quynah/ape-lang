"""
APE Standard Library - Strings Module

Pure string manipulation functions.
"""



def lower(text: str) -> str:
    """
    Convert text to lowercase.
    
    Args:
        text: String to convert
        
    Returns:
        Lowercase version of text
        
    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"lower requires string, got {type(text).__name__}")
    
    return text.lower()


def upper(text: str) -> str:
    """
    Convert text to uppercase.
    
    Args:
        text: String to convert
        
    Returns:
        Uppercase version of text
        
    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"upper requires string, got {type(text).__name__}")
    
    return text.upper()


def trim(text: str) -> str:
    """
    Remove leading and trailing whitespace.
    
    Args:
        text: String to trim
        
    Returns:
        Trimmed string
        
    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"trim requires string, got {type(text).__name__}")
    
    return text.strip()


def starts_with(text: str, prefix: str) -> bool:
    """
    Check if text starts with a prefix.
    
    Args:
        text: String to check
        prefix: Prefix to look for
        
    Returns:
        True if text starts with prefix, False otherwise
        
    Raises:
        TypeError: If text or prefix is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"starts_with requires string for text, got {type(text).__name__}")
    
    if not isinstance(prefix, str):
        raise TypeError(f"starts_with requires string for prefix, got {type(prefix).__name__}")
    
    return text.startswith(prefix)


def ends_with(text: str, suffix: str) -> bool:
    """
    Check if text ends with a suffix.
    
    Args:
        text: String to check
        suffix: Suffix to look for
        
    Returns:
        True if text ends with suffix, False otherwise
        
    Raises:
        TypeError: If text or suffix is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"ends_with requires string for text, got {type(text).__name__}")
    
    if not isinstance(suffix, str):
        raise TypeError(f"ends_with requires string for suffix, got {type(suffix).__name__}")
    
    return text.endswith(suffix)


def contains_text(text: str, fragment: str) -> bool:
    """
    Check if text contains a fragment.
    
    Args:
        text: String to search
        fragment: Fragment to find
        
    Returns:
        True if text contains fragment, False otherwise
        
    Raises:
        TypeError: If text or fragment is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"contains_text requires string for text, got {type(text).__name__}")
    
    if not isinstance(fragment, str):
        raise TypeError(f"contains_text requires string for fragment, got {type(fragment).__name__}")
    
    return fragment in text


__all__ = [
    'lower',
    'upper',
    'trim',
    'starts_with',
    'ends_with',
    'contains_text',
]
