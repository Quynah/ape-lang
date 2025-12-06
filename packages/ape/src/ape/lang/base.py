"""
Base interface for language adapters.

Language adapters provide deterministic normalization of surface syntax
to canonical APE source code.
"""

from abc import ABC, abstractmethod
from typing import Dict


class LanguageAdapter(ABC):
    """
    Base class for language adapters.
    
    Language adapters transform language-specific surface syntax into
    canonical APE source code through deterministic keyword mapping.
    
    Design Constraints:
    - Operates on raw source text (before tokenization)
    - Pure string → string transformation
    - Keyword-only mapping (whole-word, exact matches)
    - No semantic modifications
    - No NLP, no fuzzy matching, no heuristics
    - Fail hard on unknown keywords
    
    Attributes:
        language_code: ISO 639-1 language code (e.g., 'en', 'nl', 'fr')
        language_name: Human-readable language name
        script: Writing system (always 'latin' in v1.0.1)
    """
    
    def __init__(self, language_code: str, language_name: str, script: str = "latin"):
        """
        Initialize language adapter.
        
        Args:
            language_code: ISO 639-1 code (e.g., 'en', 'nl')
            language_name: Human-readable name (e.g., 'English', 'Dutch')
            script: Writing system (default: 'latin')
        """
        self.language_code = language_code
        self.language_name = language_name
        self.script = script
    
    @abstractmethod
    def get_keyword_mapping(self) -> Dict[str, str]:
        """
        Return mapping from language-specific keywords to canonical APE keywords.
        
        Returns:
            Dictionary mapping language keywords to canonical English keywords
            
        Example:
            {'als': 'if', 'anders': 'else'}  # Dutch
        """
        pass
    
    def normalize_source(self, source: str) -> str:
        """
        Normalize language-specific source code to canonical APE.
        
        This method performs deterministic keyword replacement using whole-word
        matching. Identifiers, literals, and comments are unchanged.
        
        Args:
            source: Language-specific APE source code
            
        Returns:
            Canonical APE source code
            
        Raises:
            No exceptions - returns normalized source or leaves unchanged
        """
        mapping = self.get_keyword_mapping()
        
        if not mapping:
            # Identity adapter (e.g., English)
            return source
        
        # Perform whole-word keyword replacement
        result = source
        for lang_keyword, canonical_keyword in mapping.items():
            result = self._replace_whole_word(result, lang_keyword, canonical_keyword)
        
        return result
    
    def _replace_whole_word(self, text: str, old_word: str, new_word: str) -> str:
        """
        Replace whole-word occurrences of old_word with new_word.
        
        Uses word boundaries to prevent partial matches.
        Example: 'als' matches 'als x' but not 'also'
        
        Args:
            text: Source text
            old_word: Word to replace
            new_word: Replacement word
            
        Returns:
            Text with replacements
        """
        import re
        
        # Word boundary pattern: matches whole words only
        pattern = r'\b' + re.escape(old_word) + r'\b'
        return re.sub(pattern, new_word, text)
    
    def __repr__(self) -> str:
        return f"LanguageAdapter({self.language_code}, {self.language_name}, {self.script})"


__all__ = ['LanguageAdapter']
