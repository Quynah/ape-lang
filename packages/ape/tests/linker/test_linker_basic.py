"""
Tests for Ape Linker - Basic Module Resolution

Tests basic functionality:
- Single file with no imports
- Simple imports from same directory
- Imports from lib/ subfolder
- Multiple imports
- Module not found errors
"""

import pytest

from ape.linker import Linker, LinkError, LinkedProgram


class TestLinkerBasic:
    """Test basic linker functionality"""
    
    def test_single_file_no_imports(self, tmp_path):
        """Test linking a single file with no imports"""
        # Create a simple module
        main_file = tmp_path / "main.ape"
        main_file.write_text("""
entity User:
    name: String
    id: int
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        assert isinstance(program, LinkedProgram)
        assert len(program.modules) == 1
        assert program.entry_module.file_path == main_file
        assert len(program.entry_module.imports) == 0
    
    def test_single_file_with_module_declaration(self, tmp_path):
        """Test file with explicit module declaration"""
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module myapp

entity User:
    name: String
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        assert len(program.modules) == 1
        assert program.entry_module.module_name == "myapp"
        assert program.entry_module.ast.has_module_declaration is True
    
    def test_import_from_same_directory(self, tmp_path):
        """Test importing a module from the same directory"""
        # Create math module
        math_file = tmp_path / "math.ape"
        math_file.write_text("""module math

entity Number:
    value: int
""")
        
        # Create main that imports math
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module main

import math

entity Calculator:
    number: Number
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        assert len(program.modules) == 2
        # Math should come before main (dependency order)
        assert program.modules[0].module_name == "math"
        assert program.modules[1].module_name == "main"
        
        # Check imports
        main_module = program.modules[1]
        assert "math" in main_module.imports
        assert "math" in main_module.depends_on
    
    def test_import_from_lib_subfolder(self, tmp_path):
        """Test importing a module from lib/ subfolder"""
        # Create lib directory
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create math module in lib/
        math_file = lib_dir / "math.ape"
        math_file.write_text("""module math

entity Number:
    value: int
""")
        
        # Create main that imports math
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module main

import math

entity Calculator:
    x: int
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        assert len(program.modules) == 2
        assert program.modules[0].module_name == "math"
        assert program.modules[0].file_path == math_file
    
    def test_multiple_imports(self, tmp_path):
        """Test importing multiple modules"""
        # Create math module
        math_file = tmp_path / "math.ape"
        math_file.write_text("""module math

entity Number:
    value: int
""")
        
        # Create strings module
        strings_file = tmp_path / "strings.ape"
        strings_file.write_text("""module strings

entity Text:
    content: String
""")
        
        # Create main that imports both
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module main

import math
import strings

entity Data:
    num: Number
    text: Text
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        assert len(program.modules) == 3
        # Dependencies should come before main
        module_names = [m.module_name for m in program.modules]
        assert "math" in module_names
        assert "strings" in module_names
        assert "main" in module_names
        assert module_names.index("main") == 2  # main should be last
    
    def test_transitive_dependencies(self, tmp_path):
        """Test A imports B, B imports C"""
        # Create C
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

entity Base:
    id: int
""")
        
        # Create B that imports C
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import c

entity Middle:
    base: Base
""")
        
        # Create A that imports B
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity Top:
    middle: Middle
""")
        
        linker = Linker()
        program = linker.link(a_file)
        
        assert len(program.modules) == 3
        # Order should be: C, B, A
        assert program.modules[0].module_name == "c"
        assert program.modules[1].module_name == "b"
        assert program.modules[2].module_name == "a"
    
    def test_diamond_dependency(self, tmp_path):
        """Test diamond: A imports B and C, B and C both import D"""
        # Create D
        d_file = tmp_path / "d.ape"
        d_file.write_text("""module d

entity Base:
    id: int
""")
        
        # Create B that imports D
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import d

entity Left:
    base: Base
""")
        
        # Create C that imports D
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import d

entity Right:
    base: Base
""")
        
        # Create A that imports B and C
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b
import c

entity Top:
    left: Left
    right: Right
""")
        
        linker = Linker()
        program = linker.link(a_file)
        
        assert len(program.modules) == 4
        # D should come first, B and C in some order, A last
        module_names = [m.module_name for m in program.modules]
        assert module_names[0] == "d"
        assert module_names[-1] == "a"
        assert "b" in module_names
        assert "c" in module_names


class TestLinkerErrors:
    """Test error conditions"""
    
    def test_module_not_found_error(self, tmp_path):
        """Test clear error when module not found"""
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module main

import nonexistent

entity Data:
    x: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(main_file)
        
        error_msg = str(exc_info.value)
        assert "nonexistent" in error_msg
        assert "not found" in error_msg
        assert "Searched locations:" in error_msg
    
    def test_entry_file_not_found(self, tmp_path):
        """Test error when entry file doesn't exist"""
        nonexistent = tmp_path / "nonexistent.ape"
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(nonexistent)
        
        assert "Entry file not found" in str(exc_info.value)
    
    def test_import_without_module_declaration(self, tmp_path):
        """Test that imports work even without module declaration"""
        # Create math module without module declaration
        math_file = tmp_path / "math.ape"
        math_file.write_text("""entity Number:
    value: int
""")
        
        # Create main that imports it
        main_file = tmp_path / "main.ape"
        main_file.write_text("""import math

entity Calculator:
    x: int
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        # Should work - module names derived from filenames
        assert len(program.modules) == 2
        module_names = [m.module_name for m in program.modules]
        assert "math" in module_names
        assert "main" in module_names


class TestLinkerResolutionOrder:
    """Test the specific resolution order: lib/ -> ./ -> ape_std/"""
    
    def test_lib_takes_precedence_over_same_directory(self, tmp_path):
        """Test that lib/module.ape is found before ./module.ape"""
        # Create lib directory
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create math in lib/ (should be found)
        lib_math = lib_dir / "math.ape"
        lib_math.write_text("""module math

entity LibNumber:
    value: int
""")
        
        # Create math in same directory (should be ignored)
        same_math = tmp_path / "math.ape"
        same_math.write_text("""module math

entity SameNumber:
    value: int
""")
        
        # Create main
        main_file = tmp_path / "main.ape"
        main_file.write_text("""import math

entity Test:
    x: int
""")
        
        linker = Linker()
        program = linker.link(main_file)
        
        # Should have used lib/math.ape
        math_module = [m for m in program.modules if m.module_name == "math"][0]
        assert math_module.file_path == lib_math
        assert "LibNumber" in math_module.ast.entities[0].name
    
    def test_ape_std_as_fallback(self, tmp_path):
        """Test that ape_std/ is checked as last resort"""
        # Create ape_std directory
        ape_std_dir = tmp_path / "ape_std"
        ape_std_dir.mkdir()
        
        # Create math in ape_std/
        std_math = ape_std_dir / "math.ape"
        std_math.write_text("""module math

entity StdNumber:
    value: int
""")
        
        # Create main in a subdirectory
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        main_file = app_dir / "main.ape"
        main_file.write_text("""import math

entity Test:
    x: int
""")
        
        # Use tmp_path as APE_INSTALL
        linker = Linker(ape_install_dir=tmp_path)
        program = linker.link(main_file)
        
        # Should have found math in ape_std/
        math_module = [m for m in program.modules if m.module_name == "math"][0]
        assert math_module.file_path == std_math


class TestLinkerDependencyGraph:
    """Test dependency graph generation"""
    
    def test_get_dependency_graph(self, tmp_path):
        """Test retrieving the dependency graph"""
        # Create simple chain: A -> B -> C
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

entity C:
    x: int
""")
        
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import c

entity B:
    x: int
""")
        
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        linker = Linker()
        _program = linker.link(a_file)

        dep_graph = linker.get_dependency_graph()
        assert "a" in dep_graph
        assert "b" in dep_graph
        assert "c" in dep_graph
        
        assert "b" in dep_graph["a"]
        assert "c" in dep_graph["b"]
        assert len(dep_graph["c"]) == 0  # c has no dependencies
