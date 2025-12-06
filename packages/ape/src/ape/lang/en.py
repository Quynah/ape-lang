"""
English language adapter (canonical/identity).

English is the canonical APE syntax. This adapter performs no transformations.
"""

from typing import Dict
from ape.lang.base import LanguageAdapter


class EnglishAdapter(LanguageAdapter):
    """
    English language adapter - identity transformation.
    
    English is the canonical APE syntax, so this adapter returns
    source code unchanged.
    """
    
    def __init__(self):
        super().__init__(
            language_code="en",
            language_name="English",
            script="latin"
        )
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        English is canonical - no mapping needed.
        
        Returns:
            Empty dictionary (identity transformation)
        """
        return {}


__all__ = ['EnglishAdapter']
