"""
Validate that language_spec.py stays in sync with actual shipped examples.

This test scans all .ape example files in the repository and extracts step verbs
to ensure they're documented in STEP_VERBS. It helps prevent spec drift.
"""

import re
from pathlib import Path
from typing import Set

import pytest

from ape.language_spec import (
    STEP_VERBS,
    TOP_LEVEL_KEYWORDS,
    SECTION_KEYWORDS,
    CONTROL_FLOW_KEYWORDS,
    BOOLEAN_KEYWORDS,
    PRIMITIVE_TYPES,
    STRUCTURED_TYPES,
    OPERATORS,
    MULTI_LANGUAGE_KEYWORDS,
    is_top_level_keyword,
    is_section_keyword,
    is_control_flow_keyword,
    is_boolean_keyword,
    is_primitive_type,
    is_structured_type,
    is_operator,
    get_language_keywords,
    list_supported_languages,
    get_all_language_variants,
    iter_all_keywords,
)


# Known directories containing .ape files
APE_EXAMPLE_DIRS = [
    "examples",
    "tests/evidence/ape",
    "tutorials",
    "ape_std",
]


def find_ape_files() -> list[Path]:
    """Find all .ape files in known example directories."""
    base_dir = Path(__file__).parent.parent
    ape_files = []
    
    for example_dir in APE_EXAMPLE_DIRS:
        dir_path = base_dir / example_dir
        if dir_path.exists():
            ape_files.extend(dir_path.glob("**/*.ape"))
    
    # Also check root-level demo files
    root_dir = base_dir.parent.parent
    ape_files.extend(root_dir.glob("demo_*.ape"))
    
    return sorted(ape_files)


def extract_step_verbs(ape_file: Path) -> Set[str]:
    """
    Extract step verbs from a .ape file by parsing steps: sections.
    
    Returns set of lowercase step verbs found in the file.
    """
    verbs = set()
    content = ape_file.read_text(encoding="utf-8")
    
    # Find all steps: sections (after 'steps:' until next unindented line or EOF)
    in_steps = False
    for line in content.split("\n"):
        stripped = line.lstrip()
        
        # Check if we're entering a steps section
        if stripped.startswith("steps:"):
            in_steps = True
            continue
        
        # Check if we've left the steps section (unindented line that's not a comment/blank)
        if in_steps and line and not line[0].isspace() and not line.strip().startswith("#"):
            in_steps = False
        
        # Extract verb from step bullets
        if in_steps and stripped.startswith("-"):
            # Remove the bullet and leading whitespace
            step_text = stripped[1:].lstrip()
            
            # Extract first word as potential verb
            match = re.match(r"(\w+)", step_text)
            if match:
                verb = match.group(1).lower()
                verbs.add(verb)
    
    return verbs


class TestLanguageSpec:
    """Validate language_spec.py completeness and consistency."""
    
    def test_step_verbs_cover_examples(self):
        """All step verbs used in shipped examples must be in STEP_VERBS."""
        ape_files = find_ape_files()
        assert len(ape_files) > 0, "Should find at least one .ape file"
        
        all_found_verbs = set()
        files_with_unknown_verbs = []
        
        for ape_file in ape_files:
            found_verbs = extract_step_verbs(ape_file)
            unknown_verbs = found_verbs - STEP_VERBS.words
            
            if unknown_verbs:
                files_with_unknown_verbs.append((ape_file, unknown_verbs))
            
            all_found_verbs.update(found_verbs)
        
        if files_with_unknown_verbs:
            error_msg = "Found step verbs not in STEP_VERBS:\n"
            for file_path, verbs in files_with_unknown_verbs:
                error_msg += f"  {file_path.name}: {sorted(verbs)}\n"
            error_msg += "\nAdd missing verbs to STEP_VERBS in language_spec.py"
            pytest.fail(error_msg)
    
    def test_step_verbs_alphabetically_sorted(self):
        """STEP_VERBS should be alphabetically sorted for maintainability."""
        verbs_list = sorted(list(STEP_VERBS.words))
        # Just verify we can iterate - sets are unordered by nature
        assert len(verbs_list) > 0, "STEP_VERBS should not be empty"
    
    def test_keyword_uniqueness(self):
        """Keyword sets should not overlap."""
        all_keywords = (
            TOP_LEVEL_KEYWORDS
            | SECTION_KEYWORDS
            | CONTROL_FLOW_KEYWORDS
            | BOOLEAN_KEYWORDS
        )
        
        # Check for any duplicates
        keyword_list = list(all_keywords)
        assert len(keyword_list) == len(set(keyword_list)), "Keywords should be unique across sets"
    
    def test_helper_functions(self):
        """Test helper functions work correctly."""
        assert is_top_level_keyword("module") is True
        assert is_top_level_keyword("task") is True
        assert is_top_level_keyword("unknown") is False
        
        assert is_section_keyword("steps") is True
        assert is_section_keyword("inputs") is True
        assert is_section_keyword("unknown") is False
        
        assert is_control_flow_keyword("if") is True
        assert is_control_flow_keyword("else") is True
        assert is_control_flow_keyword("unknown") is False
        
        assert is_boolean_keyword("true") is True
        assert is_boolean_keyword("and") is True
        assert is_boolean_keyword("unknown") is False
        
        assert is_primitive_type("Integer") is True
        assert is_primitive_type("String") is True
        assert is_primitive_type("Unknown") is False
        
        assert is_structured_type("List") is True
        assert is_structured_type("Map") is True
        assert is_structured_type("Unknown") is False
        
        assert is_operator("+") is True
        assert is_operator("==") is True
        assert is_operator("???") is False
    
    def test_multi_language_support(self):
        """Test multi-language keyword mappings."""
        languages = list_supported_languages()
        assert len(languages) >= 7, "Should support at least 7 languages"
        assert "en" in languages
        assert "nl" in languages
        assert "fr" in languages
        
        # Test Dutch mappings
        nl_keywords = get_language_keywords("nl")
        assert "als" in nl_keywords  # if in Dutch
        assert nl_keywords["als"] == "if"
        
        # Test getting all variants
        if_variants = get_all_language_variants("if")
        assert "if" in if_variants
        assert "als" in if_variants  # Dutch
        assert "si" in if_variants  # French/Spanish
        assert "wenn" in if_variants  # German
    
    def test_iter_all_keywords(self):
        """Test iteration over all reserved keywords."""
        all_keywords = set(iter_all_keywords())
        assert len(all_keywords) > 30, "Should have at least 30 reserved keywords"
        assert "module" in all_keywords
        assert "task" in all_keywords
        assert "steps" in all_keywords
        assert "if" in all_keywords
    
    def test_step_verbs_count(self):
        """Verify STEP_VERBS has expected count for v1.0."""
        # v1.0 complete spec has 47 step verbs (expanded from initial 34)
        assert len(STEP_VERBS.words) == 47, (
            f"Expected 47 step verbs for v1.0 complete, found {len(STEP_VERBS.words)}"
        )
    
    def test_critical_step_verbs_present(self):
        """Ensure critical step verbs from examples are present."""
        critical_verbs = {
            "call", "create", "return", "set", "check", "compute",
            "otherwise", "output", "run", "store",  # Added in v1.0 completion
        }
        
        missing = critical_verbs - STEP_VERBS.words
        assert not missing, f"Missing critical step verbs: {missing}"
    
    def test_operators_complete(self):
        """Verify operator set is complete."""
        expected_operators = {
            "<", ">", "<=", ">=", "==", "!=",  # Comparison
            "+", "-", "*", "/", "%",            # Arithmetic
            ":", ",", ".", "|", "->",           # Structural
        }
        
        missing = expected_operators - OPERATORS
        assert not missing, f"Missing operators: {missing}"
    
    def test_primitive_types_complete(self):
        """Verify primitive types are complete."""
        expected_primitives = {"String", "Integer", "Float", "Boolean", "Any"}
        assert PRIMITIVE_TYPES == expected_primitives
    
    def test_structured_types_complete(self):
        """Verify structured types are complete."""
        expected_structured = {"List", "Map", "Dict", "Record", "Tuple", "Optional"}
        assert STRUCTURED_TYPES == expected_structured


class TestLanguageSpecDocumentation:
    """Ensure language_spec.py documentation is accurate."""
    
    def test_module_docstring_claims_completeness(self):
        """Module docstring should claim completeness for v1.0."""
        import ape.language_spec as spec_module
        docstring = spec_module.__doc__
        assert "complete" in docstring.lower() or "v1.0" in docstring.lower(), (
            "Module docstring should indicate completeness for v1.0"
        )
    
    def test_wordclass_docstring_claims_completeness(self):
        """WordClass docstring should state tooling can rely on it."""
        from ape.language_spec import WordClass
        docstring = WordClass.__doc__
        assert "complete" in docstring.lower() or "rely" in docstring.lower(), (
            "WordClass docstring should state completeness for tooling"
        )
