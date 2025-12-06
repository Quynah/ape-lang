"""
Dutch language adapter.

Maps Dutch keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class DutchAdapter(LanguageAdapter):
    """
    Dutch (Nederlands) language adapter.
    
    Maps Dutch keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="nl",
            language_name="Dutch",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        Dutch to English keyword mapping.
        
        Returns:
            Dictionary mapping Dutch keywords to English
        """
        return {
            'als': 'if',
            'anders': 'else',
            'zolang': 'while',
            'voor': 'for',
            'in': 'in',
            'en': 'and',
            'of': 'or',
            'niet': 'not',
        }


__all__ = ['DutchAdapter']
