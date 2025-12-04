"""Fix remaining imports in test files"""
import re
from pathlib import Path

fixes = [
    ('from ape.parser import parse_ape_source, IRBuilder', 
     'from ape.parser import parse_ape_source\nfrom ape.ir import IRBuilder'),
    ('from ape.parser import', 'from ape.parser.parser import'),
]

root = Path(r'c:\Users\quyna\Documents\Ape')
for test_file in (root / 'tests').rglob('*.py'):
    content = test_file.read_text(encoding='utf-8')
    original = content
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    if content != original:
        test_file.write_text(content, encoding='utf-8')
        print(f"✓ Fixed: {test_file}")

print("\n✅ Import fixes complete!")
