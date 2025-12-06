"""
German language adapter.

Maps German keywords to canonical APE (English).
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class GermanAdapter(LanguageAdapter):
    """
    German (Deutsch) language adapter.
    
    Maps German keywords to canonical English APE keywords.
    """
    
    def __init__(self):
        super().__init__(
            language_code="de",
            language_name="German",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        German to English keyword mapping.
        
        Returns:
            Dictionary mapping German keywords to English
        """
        return {
            'wenn': 'if',
            'sonst': 'else',
            'solange': 'while',
            'für': 'for',
            'in': 'in',
            'und': 'and',
            'oder': 'or',
            'nicht': 'not',
        }


__all__ = ['GermanAdapter']
