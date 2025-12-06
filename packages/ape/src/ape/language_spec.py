"""
Machine-readable description of Ape's core language constructs for v1.0.

This module encodes the canonical keyword and token sets used by the official
v1.0 examples and documentation.

It is designed for use by:
- tooling (syntax highlighting, editors, LSP),
- documentation generators,
- lightweight validators.

The real parser/validator remains the final authority for semantics, but this
module is expected to stay in sync with it for all public language features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Dict


#: Keywords that introduce top-level declarations in Ape source files.
TOP_LEVEL_KEYWORDS: FrozenSet[str] = frozenset(
    {
        "module",
        "import",
        "from",
        "enum",
        "entity",
        "task",
        "flow",
        "policy",
    }
)

#: Keywords that introduce sections inside declarations (tasks, flows, policies).
SECTION_KEYWORDS: FrozenSet[str] = frozenset(
    {
        "inputs",
        "outputs",
        "constraints",
        "steps",
        "rules",
        "allow",
        "deviation",
        "scope",
        "mode",
        "bounds",
        "rationale",
    }
)

#: Control flow keywords.
CONTROL_FLOW_KEYWORDS: FrozenSet[str] = frozenset(
    {
        "if",
        "else",
        "elif",
        "while",
        "for",
        "in",
    }
)

#: Logical operators and boolean values.
BOOLEAN_KEYWORDS: FrozenSet[str] = frozenset(
    {
        "and",
        "or",
        "not",
        "true",
        "false",
        "True",
        "False",
    }
)

#: Primitive scalar types used in v1.0 examples.
PRIMITIVE_TYPES: FrozenSet[str] = frozenset(
    {
        "String",
        "Integer",
        "Float",
        "Boolean",
        "Any",
    }
)

#: Structured types (scaffolded in v1.0, syntax supported).
STRUCTURED_TYPES: FrozenSet[str] = frozenset(
    {
        "List",
        "Map",
        "Dict",
        "Record",
        "Tuple",
        "Optional",
    }
)

#: All operators recognized by the tokenizer.
OPERATORS: FrozenSet[str] = frozenset(
    {
        # Comparison
        "<", ">", "<=", ">=", "==", "!=",
        # Arithmetic
        "+", "-", "*", "/", "%",
        # Structural
        ":", ",", ".", "|", "->",
    }
)

#: Prefix used for comment lines.
COMMENT_PREFIX: str = "#"

#: Prefix used for list items (steps, constraints, rules, enum items).
LIST_ITEM_PREFIX: str = "-"

#: Multi-language keyword mappings (7 supported languages).
#: Maps language-specific keywords back to canonical English.
MULTI_LANGUAGE_KEYWORDS: Dict[str, Dict[str, str]] = {
    "en": {},  # English is canonical
    "nl": {  # Dutch
        "als": "if",
        "anders": "else",
        "zolang": "while",
        "voor": "for",
        "in": "in",
        "en": "and",
        "of": "or",
        "niet": "not",
    },
    "fr": {  # French
        "si": "if",
        "sinon": "else",
        "tant que": "while",
        "pour": "for",
        "dans": "in",
        "et": "and",
        "ou": "or",
        "pas": "not",
    },
    "de": {  # German
        "wenn": "if",
        "sonst": "else",
        "solange": "while",
        "für": "for",
        "in": "in",
        "und": "and",
        "oder": "or",
        "nicht": "not",
    },
    "es": {  # Spanish
        "si": "if",
        "sino": "else",
        "mientras": "while",
        "para": "for",
        "en": "in",
        "y": "and",
        "o": "or",
        "no": "not",
    },
    "it": {  # Italian
        "se": "if",
        "altrimenti": "else",
        "mentre": "while",
        "per": "for",
        "in": "in",
        "e": "and",
        "o": "or",
        "non": "not",
    },
    "pt": {  # Portuguese
        "se": "if",
        "senão": "else",
        "enquanto": "while",
        "para": "for",
        "em": "in",
        "e": "and",
        "ou": "or",
        "não": "not",
    },
}


@dataclass(frozen=True)
class WordClass:
    """
    Describes a simple class of words used in the language.

    For Ape v1.0 this is intended to be *complete* for all officially
    documented constructs and examples, so tooling can rely on it.
    New public features must update this module accordingly.
    """
    name: str
    words: FrozenSet[str]


#: Verbs and tokens that commonly start step sentences in v1.0 examples.
#: This set is exhaustive for all official examples and documentation.
STEP_VERBS: WordClass = WordClass(
    name="step_verbs",
    words=frozenset(
        {
            "add",
            "aggregate",
            "allow",
            "calculate",
            "call",
            "check",
            "collect",
            "compare",
            "compute",
            "convert",
            "copy",
            "count",
            "create",
            "deterministic",
            "display",
            "divide",
            "ensure",
            "exit",
            "extract",
            "filter",
            "format",
            "generate",
            "if",
            "include",
            "iterate",
            "map",
            "multiply",
            "otherwise",
            "output",
            "parse",
            "power",
            "print",
            "process",
            "read",
            "reduce",
            "return",
            "run",
            "set",
            "sort",
            "store",
            "subtract",
            "sum",
            "terminate",
            "transform",
            "validate",
            "verify",
            "write",
        }
    ),
)

#: Common step patterns and connectors used in natural language steps.
STEP_CONNECTORS: WordClass = WordClass(
    name="step_connectors",
    words=frozenset(
        {
            "to",
            "with",
            "from",
            "into",
            "equals",
            "is",
            "as",
            "then",
            "and",
            "or",
            "the",
            "a",
            "an",
        }
    ),
)


def is_top_level_keyword(token: str) -> bool:
    """
    Return True if *token* is a reserved top-level keyword.

    This function is intended for tooling; the canonical parser
    still defines the true behavior.
    """
    return token in TOP_LEVEL_KEYWORDS


def is_section_keyword(token: str) -> bool:
    """
    Return True if *token* is a reserved block section keyword.
    """
    return token in SECTION_KEYWORDS


def is_control_flow_keyword(token: str) -> bool:
    """
    Return True if *token* is a control flow keyword (if, while, for, etc.).
    """
    return token in CONTROL_FLOW_KEYWORDS


def is_boolean_keyword(token: str) -> bool:
    """
    Return True if *token* is a boolean keyword or literal.
    """
    return token in BOOLEAN_KEYWORDS


def is_primitive_type(name: str) -> bool:
    """
    Return True if *name* is a known primitive scalar type.
    """
    return name in PRIMITIVE_TYPES


def is_structured_type(name: str) -> bool:
    """
    Return True if *name* is a structured type (List, Map, Record, etc.).
    
    Note: These types are scaffolded in v1.0 - syntax is supported but
    runtime implementation is pending.
    """
    return name in STRUCTURED_TYPES


def is_operator(token: str) -> bool:
    """
    Return True if *token* is a recognized operator.
    """
    return token in OPERATORS


def get_language_keywords(language_code: str) -> Dict[str, str]:
    """
    Get keyword mappings for a specific language.
    
    Args:
        language_code: ISO 639-1 language code (en, nl, fr, de, es, it, pt)
        
    Returns:
        Dictionary mapping language-specific keywords to canonical English.
        Empty dict for English (canonical).
        
    Raises:
        KeyError: If language code is not supported.
    """
    return MULTI_LANGUAGE_KEYWORDS[language_code]


def list_supported_languages() -> list[str]:
    """
    List all supported language codes.
    
    Returns:
        List of ISO 639-1 language codes.
    """
    return list(MULTI_LANGUAGE_KEYWORDS.keys())


def iter_all_keywords() -> Iterable[str]:
    """
    Iterate over all known reserved tokens that should not be used
    as identifiers in user code.
    
    This includes English keywords only. Multi-language keywords are
    normalized at parse time.
    """
    # Top-level + sections + control flow + boolean + primitive types.
    # Step verbs are intentionally not included here to avoid
    # over-restricting identifier choices in future versions.
    seen = set()
    for token in (
        *TOP_LEVEL_KEYWORDS,
        *SECTION_KEYWORDS,
        *CONTROL_FLOW_KEYWORDS,
        *BOOLEAN_KEYWORDS,
        *PRIMITIVE_TYPES,
    ):
        if token not in seen:
            seen.add(token)
            yield token


def get_all_language_variants(english_keyword: str) -> list[str]:
    """
    Get all language variants of a canonical English keyword.
    
    Args:
        english_keyword: Canonical English keyword (e.g., "if", "while")
        
    Returns:
        List of all language variants including the English original.
        
    Example:
        >>> get_all_language_variants("if")
        ['if', 'als', 'si', 'wenn', 'si', 'se', 'se']
    """
    variants = [english_keyword]
    for lang_map in MULTI_LANGUAGE_KEYWORDS.values():
        for foreign, english in lang_map.items():
            if english == english_keyword and foreign not in variants:
                variants.append(foreign)
    return variants

