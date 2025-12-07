"""
Script to migrate Ape to new structure and update all imports
"""
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAP = {
    'from apeparser.tokenizer import': 'from ape.tokenizer.tokenizer import',
    'from apeparser.parser import': 'from ape.parser.parser import',
    'from apeparser.ast_nodes import': 'from ape.parser.ast_nodes import',
    'from apeparser.ir_builder import': 'from ape.ir.ir_builder import',
    'from apeparser import': 'from ape.parser import',
    'from apecompiler.ir_nodes import': 'from ape.compiler.ir_nodes import',
    'from apecompiler.semantic_validator import': 'from ape.compiler.semantic_validator import',
    'from apecompiler.strictness_engine import': 'from ape.compiler.strictness_engine import',
    'from apecompiler.errors import': 'from ape.compiler.errors import',
    'from apecompiler import': 'from ape.compiler import',
    'from apecodegen.python_codegen import': 'from ape.codegen.python_codegen import',
    'from apecodegen import': 'from ape.codegen import',
    'from aperuntime import': 'from ape.runtime import',
    'from aperuntime.core import': 'from ape.runtime.core import',
    'from apecli.cli import': 'from ape.cli import',
    'import apeparser': 'import ape.parser',
    'import apecompiler': 'import ape.compiler',
    'import apecodegen': 'import ape.codegen',
    'import aperuntime': 'import ape.runtime',
}

def update_imports_in_file(filepath):
    """Update imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for old_import, new_import in IMPORT_MAP.items():
            content = content.replace(old_import, new_import)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error in {filepath}: {e}")
        return False

def main():
    root = Path(r'c:\Users\quyna\Documents\Ape')
    
    # Update all Python files in src/ape/
    updated_count = 0
    for py_file in (root / 'src' / 'ape').rglob('*.py'):
        if update_imports_in_file(py_file):
            updated_count += 1
    
    # Update all test files
    for py_file in (root / 'tests').rglob('*.py'):
        if update_imports_in_file(py_file):
            updated_count += 1
    
    # Update other Python files in root
    for py_file in root.glob('*.py'):
        if py_file.name != 'migrate_structure.py':
            if update_imports_in_file(py_file):
                updated_count += 1
    
    print(f"\n✅ Migration complete! Updated {updated_count} files.")

if __name__ == '__main__':
    main()
