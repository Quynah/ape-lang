"""
French language adapter.

Maps French keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class FrenchAdapter(LanguageAdapter):
    """
    French (Français) language adapter.
    
    Maps French keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="fr",
            language_name="French",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        French to English keyword mapping.
        
        Returns:
            Dictionary mapping French keywords to English
        """
        return {
            'si': 'if',
            'sinon': 'else',
            'tant que': 'while',
            'pour': 'for',
            'dans': 'in',
            'et': 'and',
            'ou': 'or',
            'pas': 'not',
        }


__all__ = ['FrenchAdapter']
