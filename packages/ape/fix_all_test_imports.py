#!/usr/bin/env python3
"""Fix all remaining test imports to use new structure."""

import re
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # apeparser imports
    r'from src\.apeparser import (.+)': lambda m: f'from ape.parser import {m.group(1)}' if 'IRBuilder' not in m.group(1) else handle_mixed_imports(m.group(1)),
    r'from src\.apeparser\.parser import parse_ape_source': 'from ape.parser import parse_ape_source',
    r'from src\.apeparser\.tokenizer import (.+)': r'from ape.tokenizer import \1',
    
    # apecompiler imports
    r'from src\.apecompiler\.ir_nodes import (.+)': r'from ape.compiler.ir_nodes import \1',
    r'from src\.apecompiler\.semantic_validator import (.+)': r'from ape.compiler.semantic_validator import \1',
    r'from src\.apecompiler\.strictness_engine import (.+)': r'from ape.compiler.strictness_engine import \1',
    r'from src\.apecompiler\.errors import (.+)': r'from ape.compiler.errors import \1',
    
    # apecodegen imports
    r'from src\.apecodegen\.python_codegen import (.+)': r'from ape.codegen.python_codegen import \1',
    
    # aperuntime imports
    r'from src\.aperuntime\.core import (.+)': r'from ape.runtime.core import \1',
}

def handle_mixed_imports(imports_str):
    """Handle imports that contain both parser and IR items."""
    items = [item.strip() for item in imports_str.split(',')]
    parser_items = []
    ir_items = []
    
    for item in items:
        if 'IRBuilder' in item:
            ir_items.append(item)
        else:
            parser_items.append(item)
    
    result = []
    if parser_items:
        result.append(f'from ape.parser import {", ".join(parser_items)}')
    if ir_items:
        result.append(f'from ape.ir import {", ".join(ir_items)}')
    
    return '\n'.join(result)

def fix_file(filepath):
    """Fix imports in a single file."""
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    
    for pattern, replacement in IMPORT_MAPPINGS.items():
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        print(f"✓ Fixed: {filepath}")
        return True
    return False

def main():
    """Fix all test files."""
    repo_root = Path(__file__).parent
    test_dir = repo_root / 'tests'
    
    fixed_count = 0
    for test_file in test_dir.rglob('*.py'):
        if fix_file(test_file):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} test files!")

if __name__ == '__main__':
    main()
