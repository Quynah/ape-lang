"""
Language adapter registry.

Provides lookup and validation for language adapters.
"""

from typing import Dict, List
from ape.lang.base import LanguageAdapter
from ape.errors import ValidationError


# Registry of available language adapters
_ADAPTERS: Dict[str, LanguageAdapter] = {}


def register_adapter(adapter: LanguageAdapter) -> None:
    """
    Register a language adapter.
    
    Args:
        adapter: Language adapter to register
        
    Raises:
        ValidationError: If language code already registered
    """
    if adapter.language_code in _ADAPTERS:
        raise ValidationError(
            f"Language adapter '{adapter.language_code}' already registered",
            details={'language_code': adapter.language_code}
        )
    _ADAPTERS[adapter.language_code] = adapter


def get_adapter(language_code: str) -> LanguageAdapter:
    """
    Get language adapter by language code.
    
    Args:
        language_code: ISO 639-1 language code (e.g., 'en', 'nl')
        
    Returns:
        Language adapter for the specified code
        
    Raises:
        ValidationError: If language code not supported
    """
    if language_code not in _ADAPTERS:
        supported = ', '.join(sorted(_ADAPTERS.keys()))
        raise ValidationError(
            f"Unsupported language code '{language_code}'. Supported: {supported}",
            details={'language_code': language_code, 'supported': list(_ADAPTERS.keys())}
        )
    return _ADAPTERS[language_code]


def list_supported_languages() -> List[str]:
    """
    List all supported language codes.
    
    Returns:
        Sorted list of ISO 639-1 language codes
    """
    return sorted(_ADAPTERS.keys())


def is_supported(language_code: str) -> bool:
    """
    Check if language code is supported.
    
    Args:
        language_code: ISO 639-1 language code
        
    Returns:
        True if language is supported
    """
    return language_code in _ADAPTERS


# Auto-register all built-in adapters
def _register_builtin_adapters():
    """Register all built-in language adapters."""
    # Import here to avoid circular dependencies
    from ape.lang.en import EnglishAdapter
    from ape.lang.nl import DutchAdapter
    from ape.lang.fr import FrenchAdapter
    from ape.lang.de import GermanAdapter
    from ape.lang.es import SpanishAdapter
    from ape.lang.it import ItalianAdapter
    from ape.lang.pt import PortugueseAdapter
    
    register_adapter(EnglishAdapter())
    register_adapter(DutchAdapter())
    register_adapter(FrenchAdapter())
    register_adapter(GermanAdapter())
    register_adapter(SpanishAdapter())
    register_adapter(ItalianAdapter())
    register_adapter(PortugueseAdapter())


# Register adapters on module import
_register_builtin_adapters()


__all__ = [
    'register_adapter',
    'get_adapter',
    'list_supported_languages',
    'is_supported',
]
