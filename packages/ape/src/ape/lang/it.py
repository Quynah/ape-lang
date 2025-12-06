"""
Italian language adapter.

Maps Italian keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class ItalianAdapter(LanguageAdapter):
    """
    Italian (Italiano) language adapter.
    
    Maps Italian keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="it",
            language_name="Italian",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        Italian to English keyword mapping.
        
        Returns:
            Dictionary mapping Italian keywords to English
        """
        return {
            'se': 'if',
            'altrimenti': 'else',
            'mentre': 'while',
            'per': 'for',
            'in': 'in',
            'e': 'and',
            'o': 'or',
            'non': 'not',
        }


__all__ = ['ItalianAdapter']
