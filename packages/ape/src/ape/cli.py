"""
Ape CLI - Command Line Interface

Provides commands for parsing, validating, and building Ape source files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ape.parser.parser import parse_ape_source
from ape.ir.ir_builder import IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.compiler.semantic_validator import SemanticValidator
from ape.compiler.strictness_engine import StrictnessEngine
from ape.codegen.python_codegen import PythonCodeGenerator
from ape.linker import Linker, LinkError


def load_source(path: str | Path) -> str:
    """Load Ape source file content."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Ape source file not found: {p}")
    return p.read_text(encoding="utf-8")


def build_ast(path: str | Path):
    """Parse Ape source to AST."""
    source = load_source(path)
    filename = str(Path(path).name)
    module_ast = parse_ape_source(source, filename)
    return module_ast


def build_ir(path: str | Path):
    """Build IR from Ape source."""
    module_ast = build_ast(path)
    builder = IRBuilder()
    filename = str(Path(path).name)
    module_ir = builder.build_module(module_ast, filename)
    return module_ir


def build_project(path: str | Path) -> ProjectNode:
    """
    Build ProjectNode from Ape source with full module resolution.
    
    This function uses the Linker to resolve all module dependencies,
    then builds IR for each module in dependency order.
    
    Args:
        path: Path to the entry Ape source file
        
    Returns:
        ProjectNode containing all linked modules
        
    Raises:
        LinkError: If module resolution fails
    """
    # Link all modules starting from entry file
    linker = Linker()
    try:
        program = linker.link(Path(path))
    except LinkError as e:
        # Re-raise with better context
        raise LinkError(f"Failed to link {path}: {e}") from e
    
    # Build IR for all modules in dependency order
    builder = IRBuilder()
    ir_modules = []
    
    for resolved_module in program.modules:
        module_ir = builder.build_module(
            resolved_module.ast,
            str(resolved_module.file_path.name)
        )
        ir_modules.append(module_ir)
    
    # Create project node
    project_name = Path(path).stem.title() + "Project"
    project = ProjectNode(name=project_name, modules=ir_modules)
    
    return project


def cmd_parse(args) -> int:
    """Parse command: show AST representation."""
    try:
        module_ast = build_ast(args.path)
        print(f"AST for {args.path}:")
        print(repr(module_ast))
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_ir(args) -> int:
    """IR command: show IR as JSON."""
    try:
        module_ir = build_ir(args.path)
        
        def default(o):
            """Custom JSON serializer for IR nodes."""
            if hasattr(o, '__dict__'):
                return {k: v for k, v in o.__dict__.items() if not k.startswith('_')}
            if hasattr(o, 'value'):  # Handle enums
                return o.value
            return str(o)
        
        print(f"IR for {args.path}:")
        print(json.dumps(module_ir, default=default, indent=2))
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_validate(args) -> int:
    """Validate command: run semantic validation and strictness checks."""
    try:
        project = build_project(args.path)
        
        # Semantic validation
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        
        # Strictness validation
        strict = StrictnessEngine()
        strict_errors = strict.enforce(project)
        
        all_errors = list(semantic_errors) + list(strict_errors)
        
        if not all_errors:
            print(f"✓ OK: {args.path} passed all validation checks.")
            return 0
        
        print(f"✗ Validation failed for {args.path}:")
        for err in all_errors:
            print(f"  - {err}")
        return 1
        
    except LinkError as e:
        print(f"LINK ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_build(args) -> int:
    """Build command: generate target code."""
    try:
        if args.target != "python":
            print(f"ERROR: unsupported target '{args.target}'. Only 'python' is supported in v0.1.", 
                  file=sys.stderr)
            return 1
        
        project = build_project(args.path)
        
        # Validate first
        validator = SemanticValidator()
        semantic_errors = validator.validate_project(project)
        strict = StrictnessEngine()
        strict_errors = strict.enforce(project)
        
        all_errors = list(semantic_errors) + list(strict_errors)
        if all_errors:
            print("Build failed due to validation/strictness errors:")
            for err in all_errors:
                print(f"  - {err}")
            return 1
        
        # Generate code
        generator = PythonCodeGenerator(project)
        files = generator.generate()
        
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        for f in files:
            path = out_dir / f.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f.content, encoding="utf-8")
            print(f"Generated {path}")
        
        print(f"\\n✓ Build successful. Generated {len(files)} file(s).")
        return 0
        
    except LinkError as e:
        print(f"LINK ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
        
        print(f"\n✓ Build successful: {len(files)} file(s) generated in {out_dir}")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="ape",
        description="Ape language compiler - Because I Said So",
        epilog="Example: python -m ape build examples/calculator_basic.ape --target=python"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # parse command
    p_parse = subparsers.add_parser("parse", help="Parse Ape source to AST")
    p_parse.add_argument("path", help=".ape source file")
    p_parse.set_defaults(func=cmd_parse)
    
    # ir command
    p_ir = subparsers.add_parser("ir", help="Build IR from Ape source")
    p_ir.add_argument("path", help=".ape source file")
    p_ir.set_defaults(func=cmd_ir)
    
    # validate command
    p_validate = subparsers.add_parser("validate", help="Semantic + strictness validation")
    p_validate.add_argument("path", help=".ape source file")
    p_validate.set_defaults(func=cmd_validate)
    
    # build command
    p_build = subparsers.add_parser("build", help="Build target code from Ape source")
    p_build.add_argument("path", help=".ape source file")
    p_build.add_argument("--target", default="python", 
                         help="build target (only 'python' supported for now)")
    p_build.add_argument("--out-dir", default="generated", 
                         help="output directory for generated files")
    p_build.set_defaults(func=cmd_build)
    
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
