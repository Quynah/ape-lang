"""
Tests for Ape CLI

Tests the command-line interface commands.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ape.cli import main


class TestCLIValidate:
    """Tests for 'ape validate' command"""
    
    def test_validate_calculator_basic(self):
        """Test that validate command works on calculator_basic.ape"""
        result = main(["validate", "examples/calculator_basic.ape"])
        assert result == 0, "calculator_basic.ape should validate successfully"
    
    def test_validate_calculator_smart(self):
        """Test that validate command works on calculator_smart.ape"""
        result = main(["validate", "examples/calculator_smart.ape"])
        assert result == 0, "calculator_smart.ape should validate successfully"
    
    def test_validate_email_policy(self):
        """Test that validate command works on email_policy_basic.ape"""
        result = main(["validate", "examples/email_policy_basic.ape"])
        assert result == 0, "email_policy_basic.ape should validate successfully"
    
    def test_validate_nonexistent_file(self):
        """Test that validate fails gracefully on missing file"""
        result = main(["validate", "examples/nonexistent.ape"])
        assert result == 1, "Should return error code for missing file"


class TestCLIBuild:
    """Tests for 'ape build' command"""
    
    def test_build_calculator_basic(self, tmp_path):
        """Test that build command generates Python code"""
        out_dir = tmp_path / "generated"
        result = main([
            "build",
            "examples/calculator_basic.ape",
            "--target=python",
            "--out-dir", str(out_dir)
        ])
        
        assert result == 0, "Build should succeed"
        
        # Check that at least one .py file was generated
        py_files = list(out_dir.rglob("*.py"))
        assert len(py_files) > 0, f"Expected at least one .py file in {out_dir}"
        
        # Check that generated code has expected content
        for py_file in py_files:
            content = py_file.read_text()
            # Should have imports, dataclasses, functions, etc.
            assert len(content) > 100, f"Generated file {py_file} seems too small"
    
    def test_build_calculator_smart(self, tmp_path):
        """Test that build works with deviation-containing example"""
        out_dir = tmp_path / "generated"
        result = main([
            "build",
            "examples/calculator_smart.ape",
            "--target=python",
            "--out-dir", str(out_dir)
        ])
        
        assert result == 0, "Build should succeed"
        py_files = list(out_dir.rglob("*.py"))
        assert len(py_files) > 0, "Expected generated Python files"
    
    def test_build_email_policy(self, tmp_path):
        """Test that build works with email policy example"""
        out_dir = tmp_path / "generated"
        result = main([
            "build",
            "examples/email_policy_basic.ape",
            "--target=python",
            "--out-dir", str(out_dir)
        ])
        
        assert result == 0, "Build should succeed"
        py_files = list(out_dir.rglob("*.py"))
        assert len(py_files) > 0, "Expected generated Python files"
    
    def test_build_unsupported_target(self, tmp_path):
        """Test that build fails gracefully for unsupported targets"""
        result = main([
            "build",
            "examples/calculator_basic.ape",
            "--target=javascript",
            "--out-dir", str(tmp_path)
        ])
        
        assert result == 1, "Should return error code for unsupported target"


class TestCLIParse:
    """Tests for 'ape parse' command"""
    
    def test_parse_calculator_basic(self):
        """Test that parse command works"""
        result = main(["parse", "examples/calculator_basic.ape"])
        assert result == 0, "Parse should succeed"


class TestCLIIR:
    """Tests for 'ape ir' command"""
    
    def test_ir_calculator_basic(self):
        """Test that ir command works"""
        result = main(["ir", "examples/calculator_basic.ape"])
        assert result == 0, "IR build should succeed"
