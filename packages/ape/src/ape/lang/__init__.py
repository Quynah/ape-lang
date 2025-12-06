"""
APE Multi-Language Surface Syntax

Language adapters for deterministic normalization of surface syntax to canonical APE.

Design Principles:
- ONE language (APE), multiple surface syntaxes
- Adapters run BEFORE tokenization
- Canonical AST remains identical across all languages
- Parser and runtime unchanged
- Deterministic keyword-only mapping (no NLP, no heuristics)
- Fail hard on ambiguous or unknown input

Supported Languages (v1.0.1):
- en (English) - Canonical / identity adapter
- nl (Dutch)
- fr (French)
- de (German)
- es (Spanish)
- it (Italian)
- pt (Portuguese)

All languages use Latin script only.
"""

from ape.lang.base import LanguageAdapter
from ape.lang.registry import get_adapter, list_supported_languages

__all__ = [
    'LanguageAdapter',
    'get_adapter',
    'list_supported_languages',
]
