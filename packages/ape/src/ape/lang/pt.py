"""
Portuguese language adapter.

Maps Portuguese keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class PortugueseAdapter(LanguageAdapter):
    """
    Portuguese (Português) language adapter.
    
    Maps Portuguese keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="pt",
            language_name="Portuguese",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        Portuguese to English keyword mapping.
        
        Returns:
            Dictionary mapping Portuguese keywords to English
        """
        return {
            'se': 'if',
            'senão': 'else',
            'enquanto': 'while',
            'para': 'for',
            'em': 'in',
            'e': 'and',
            'ou': 'or',
            'não': 'not',
        }


__all__ = ['PortugueseAdapter']
