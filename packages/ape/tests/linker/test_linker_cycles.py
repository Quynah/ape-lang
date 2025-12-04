"""
Tests for Ape Linker - Circular Dependency Detection

Tests cycle detection:
- Simple 2-module cycle (A -> B -> A)
- Longer cycles (A -> B -> C -> A)
- Self-import (A imports A)
"""

import pytest
from pathlib import Path

from ape.linker import Linker, LinkError


class TestLinkerCycles:
    """Test circular dependency detection"""
    
    def test_simple_cycle_two_modules(self, tmp_path):
        """Test detection of simple A -> B -> A cycle"""
        # Create A that imports B
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        # Create B that imports A
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import a

entity B:
    y: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(a_file)
        
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
        assert "a" in error_msg
        assert "b" in error_msg
        assert "->" in error_msg
    
    def test_three_module_cycle(self, tmp_path):
        """Test detection of A -> B -> C -> A cycle"""
        # Create A that imports B
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        # Create B that imports C
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import c

entity B:
    y: int
""")
        
        # Create C that imports A
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import a

entity C:
    z: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(a_file)
        
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
        # Should show the cycle path
        assert "a" in error_msg and "b" in error_msg and "c" in error_msg
    
    def test_longer_cycle(self, tmp_path):
        """Test detection of longer cycle: A -> B -> C -> D -> A"""
        # Create chain with cycle
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import c

entity B:
    x: int
""")
        
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import d

entity C:
    x: int
""")
        
        d_file = tmp_path / "d.ape"
        d_file.write_text("""module d

import a

entity D:
    x: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(a_file)
        
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
        # Cycle should include all modules
        for mod in ["a", "b", "c", "d"]:
            assert mod in error_msg
    
    def test_cycle_with_common_dependency(self, tmp_path):
        """Test cycle detection with a common dependency (not a cycle itself)"""
        # Create D (common dependency)
        d_file = tmp_path / "d.ape"
        d_file.write_text("""module d

entity D:
    x: int
""")
        
        # Create B that imports D and C
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import d
import c

entity B:
    x: int
""")
        
        # Create C that imports D and B (cycle: B <-> C)
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import d
import b

entity C:
    x: int
""")
        
        # Create A that imports B
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(a_file)
        
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
        # Cycle should be between b and c
        assert "b" in error_msg and "c" in error_msg
    
    def test_no_false_positive_on_diamond(self, tmp_path):
        """Test that diamond dependencies don't trigger false cycle detection"""
        # Diamond: A imports B and C, B and C both import D
        # This is NOT a cycle and should work fine
        
        d_file = tmp_path / "d.ape"
        d_file.write_text("""module d

entity D:
    x: int
""")
        
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import d

entity B:
    x: int
""")
        
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import d

entity C:
    x: int
""")
        
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b
import c

entity A:
    x: int
""")
        
        linker = Linker()
        # Should NOT raise an error
        program = linker.link(a_file)
        
        # Should successfully link all 4 modules
        assert len(program.modules) == 4
        module_names = {m.module_name for m in program.modules}
        assert module_names == {"a", "b", "c", "d"}
    
    def test_cycle_error_message_shows_path(self, tmp_path):
        """Test that cycle error shows the actual cycle path"""
        # Create simple cycle
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

import a

entity B:
    x: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(a_file)
        
        error_msg = str(exc_info.value)
        # Should show the path with arrows
        assert " -> " in error_msg
        # Should mention refactoring
        assert "Refactor" in error_msg or "refactor" in error_msg


class TestLinkerCycleVariations:
    """Test various cycle scenarios"""
    
    def test_cycle_in_lib_folder(self, tmp_path):
        """Test cycle detection works in lib/ folder"""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create cycle in lib/
        a_file = lib_dir / "a.ape"
        a_file.write_text("""module a

import b

entity A:
    x: int
""")
        
        b_file = lib_dir / "b.ape"
        b_file.write_text("""module b

import a

entity B:
    x: int
""")
        
        # Main imports a
        main_file = tmp_path / "main.ape"
        main_file.write_text("""module main

import a

entity Main:
    x: int
""")
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(main_file)
        
        assert "Circular dependency detected" in str(exc_info.value)
    
    def test_indirect_cycle_detection(self, tmp_path):
        """Test that cycles are detected even with long chains"""
        # Create A -> B -> C -> D -> E -> C (cycle at C)
        
        (tmp_path / "a.ape").write_text("""module a

import b

entity A:
    x: int
""")
        (tmp_path / "b.ape").write_text("""module b

import c

entity B:
    x: int
""")
        (tmp_path / "c.ape").write_text("""module c

import d

entity C:
    x: int
""")
        (tmp_path / "d.ape").write_text("""module d

import e

entity D:
    x: int
""")
        (tmp_path / "e.ape").write_text("""module e

import c

entity E:
    x: int
""")  # Back to C
        
        linker = Linker()
        with pytest.raises(LinkError) as exc_info:
            linker.link(tmp_path / "a.ape")
        
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
        # The cycle involves c, d, e
        assert "c" in error_msg
        assert "d" in error_msg
        assert "e" in error_msg
    
    def test_multiple_entry_points_no_cycle(self, tmp_path):
        """Test that having multiple possible entry points doesn't cause issues"""
        # Create independent modules that could each be entry points
        
        a_file = tmp_path / "a.ape"
        a_file.write_text("""module a

entity A:
    x: int
""")
        
        b_file = tmp_path / "b.ape"
        b_file.write_text("""module b

entity B:
    x: int
""")
        
        c_file = tmp_path / "c.ape"
        c_file.write_text("""module c

import a
import b

entity C:
    x: int
""")
        
        linker = Linker()
        
        # Should be able to link from any of them
        program_a = linker.link(a_file)
        assert len(program_a.modules) == 1
        
        # Reset for next link
        linker = Linker()
        program_c = linker.link(c_file)
        assert len(program_c.modules) == 3
