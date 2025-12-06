"""
Spanish language adapter.

Maps Spanish keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class SpanishAdapter(LanguageAdapter):
    """
    Spanish (Español) language adapter.
    
    Maps Spanish keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="es",
            language_name="Spanish",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        Spanish to English keyword mapping.
        
        Returns:
            Dictionary mapping Spanish keywords to English
        """
        return {
            'si': 'if',
            'sino': 'else',
            'mientras': 'while',
            'para': 'for',
            'en': 'in',
            'y': 'and',
            'o': 'or',
            'no': 'not',
        }


__all__ = ['SpanishAdapter']
