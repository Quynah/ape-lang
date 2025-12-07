"""
Ape Linker - Module Resolution and Dependency Management

The Linker is responsible for:
1. Resolving module imports using deterministic search paths
2. Building a dependency graph of all modules
3. Detecting circular dependencies
4. Producing a topologically ordered list of modules for compilation

Resolution order (per docs/modules_and_imports.md):
1. ./lib/<module>.ape
2. ./<module>.ape
3. <APE_INSTALL>/ape_std/<module>.ape

If a module is not found, a LinkError is raised with no fallbacks.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field

from ape.parser.parser import Parser
from ape.parser.ast_nodes import ModuleNode
from ape.tokenizer.tokenizer import Tokenizer


class LinkError(Exception):
    """Error raised when module linking fails"""
    pass


@dataclass
class ResolvedModule:
    """
    Represents a resolved module with its metadata.
    
    Attributes:
        module_name: The declared module name (from 'module <name>' statement)
        file_path: Absolute path to the source file
        ast: Parsed AST of the module
        imports: List of imported module names (simple names, not qualified)
        depends_on: Set of module names this module depends on
    """
    module_name: str
    file_path: Path
    ast: ModuleNode
    imports: List[str] = field(default_factory=list)
    depends_on: Set[str] = field(default_factory=set)
    
    def __hash__(self):
        return hash(self.module_name)
    
    def __eq__(self, other):
        if isinstance(other, ResolvedModule):
            return self.module_name == other.module_name
        return False


@dataclass
class LinkedProgram:
    """
    Result of linking: all modules in topological order.
    
    Attributes:
        entry_module: The entry point module
        modules: All modules in dependency order (dependencies before dependents)
        module_map: Map from module name to ResolvedModule
    """
    entry_module: ResolvedModule
    modules: List[ResolvedModule]
    module_map: Dict[str, ResolvedModule] = field(default_factory=dict)


class Linker:
    """
    Ape Module Linker.
    
    Resolves all module imports, builds dependency graph, and produces
    a linked program ready for compilation.
    """
    
    def __init__(self, ape_install_dir: Optional[Path] = None):
        """
        Initialize the linker.
        
        Args:
            ape_install_dir: Root directory for APE_INSTALL (defaults to package location)
        """
        self.ape_install_dir = ape_install_dir or self._get_default_ape_install()
        self.resolved_modules: Dict[str, ResolvedModule] = {}
        self.resolution_stack: List[str] = []  # For cycle detection during resolution
    
    def _get_default_ape_install(self) -> Path:
        """Get the default APE_INSTALL directory"""
        # Try environment variable first
        env_path = os.environ.get('APE_INSTALL')
        if env_path:
            return Path(env_path)
        
        # Default to package parent directory
        # This assumes ape is installed and we can find ape_std/ relative to it
        return Path(__file__).parent.parent.parent
    
    def link(self, entry_file: Path) -> LinkedProgram:
        """
        Link a program starting from an entry file.
        
        Args:
            entry_file: Path to the main/entry Ape source file
            
        Returns:
            LinkedProgram with all modules in topological order
            
        Raises:
            LinkError: If resolution fails, modules not found, or cycles detected
        """
        entry_file = Path(entry_file).resolve()
        
        if not entry_file.exists():
            raise LinkError(f"Entry file not found: {entry_file}")
        
        # Reset state
        self.resolved_modules = {}
        self.resolution_stack = []
        
        # Resolve the entry module and all its dependencies
        entry_module = self._resolve_module_from_file(entry_file, is_entry=True)
        
        # Build topological order
        ordered_modules = self._topological_sort(entry_module)
        
        # Build module map
        module_map = {m.module_name: m for m in ordered_modules}
        
        return LinkedProgram(
            entry_module=entry_module,
            modules=ordered_modules,
            module_map=module_map
        )
    
    def _resolve_module_from_file(self, file_path: Path, is_entry: bool = False) -> ResolvedModule:
        """
        Parse and resolve a module from a file path.
        
        Args:
            file_path: Absolute path to the .ape file
            is_entry: True if this is the entry point module
            
        Returns:
            ResolvedModule with all dependencies resolved
        """
        file_path = file_path.resolve()
        
        # Parse the file
        source = file_path.read_text(encoding='utf-8')
        tokens = Tokenizer(source, str(file_path)).tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Determine module name
        if ast.has_module_declaration and ast.name:
            module_name = ast.name
        else:
            # For files without module declaration, use filename (without .ape)
            module_name = file_path.stem
        
        # Check for cycles during resolution (BEFORE checking if already resolved)
        if module_name in self.resolution_stack:
            cycle_path = ' -> '.join(self.resolution_stack + [module_name])
            raise LinkError(
                f"Circular dependency detected: {cycle_path}\n\n"
                f"Ape does not allow circular module dependencies. "
                f"Refactor your code to break the cycle."
            )
        
        # Check if already resolved
        if module_name in self.resolved_modules:
            return self.resolved_modules[module_name]
        
        # Add to resolution stack
        self.resolution_stack.append(module_name)
        
        # Create the resolved module
        resolved = ResolvedModule(
            module_name=module_name,
            file_path=file_path,
            ast=ast
        )
        
        # Register it immediately to prevent infinite loops
        self.resolved_modules[module_name] = resolved
        
        # Resolve all imports
        for import_node in ast.imports:
            imported_module_name = import_node.module_name
            
            # Resolve the imported module
            try:
                imported_module = self._resolve_import(
                    imported_module_name,
                    from_file=file_path
                )
                
                # Track dependency
                resolved.imports.append(imported_module_name)
                resolved.depends_on.add(imported_module.module_name)
                
            except LinkError:
                # Re-raise with context
                raise
        
        # Remove from resolution stack
        self.resolution_stack.pop()
        
        return resolved
    
    def _resolve_import(self, module_name: str, from_file: Path) -> ResolvedModule:
        """
        Resolve an import statement to an actual module.
        
        Search order (deterministic):
        1. ./lib/<module>.ape
        2. ./<module>.ape
        3. <APE_INSTALL>/ape_std/<module>.ape
        
        Args:
            module_name: Name of the module to import (e.g., 'math', 'strings')
            from_file: Path of the file doing the importing
            
        Returns:
            ResolvedModule for the imported module
            
        Raises:
            LinkError: If module cannot be found
        """
        # Base directory is the directory containing the importing file
        base_dir = from_file.parent
        
        # Build search paths in order
        search_paths = [
            base_dir / "lib" / f"{module_name}.ape",
            base_dir / f"{module_name}.ape",
            self.ape_install_dir / "ape_std" / f"{module_name}.ape"
        ]
        
        # Also check for hierarchical module paths (e.g., strings.upper -> strings/upper.ape)
        if '.' in module_name:
            module_path = module_name.replace('.', os.sep)
            search_paths.extend([
                base_dir / "lib" / f"{module_path}.ape",
                base_dir / f"{module_path}.ape",
                self.ape_install_dir / "ape_std" / f"{module_path}.ape"
            ])
        
        # Try each path in order
        for path in search_paths:
            if path.exists() and path.is_file():
                # Found it! Resolve recursively
                return self._resolve_module_from_file(path)
        
        # Module not found - build detailed error message
        searched_locations = "\\n  ".join(str(p) for p in search_paths[:3])  # Show only main paths
        raise LinkError(
            f"Module '{module_name}' not found.\\n"
            f"Searched locations:\\n  {searched_locations}\\n\\n"
            f"Ensure the module exists in one of these locations or check your "
            f"APE_INSTALL environment variable (currently: {self.ape_install_dir})"
        )
    
    def _topological_sort(self, entry_module: ResolvedModule) -> List[ResolvedModule]:
        """
        Perform topological sort on the dependency graph.
        
        Returns modules in dependency order: dependencies before dependents.
        
        Args:
            entry_module: The entry point module
            
        Returns:
            List of modules in compilation order
            
        Raises:
            LinkError: If a cycle is detected (shouldn't happen if resolution succeeded)
        """
        visited = set()
        result = []
        visiting = set()  # For cycle detection
        
        def visit(module: ResolvedModule):
            if module.module_name in visited:
                return
            
            if module.module_name in visiting:
                # Cycle detected during sort (shouldn't happen)
                raise LinkError("Internal error: cycle detected during topological sort")
            
            visiting.add(module.module_name)
            
            # Visit dependencies first
            for dep_name in module.depends_on:
                if dep_name in self.resolved_modules:
                    visit(self.resolved_modules[dep_name])
            
            visiting.remove(module.module_name)
            visited.add(module.module_name)
            result.append(module)
        
        # Start from entry module
        visit(entry_module)
        
        # Also visit any unvisited modules (shouldn't happen in normal cases)
        for module in self.resolved_modules.values():
            if module.module_name not in visited:
                visit(module)
        
        return result
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph as an adjacency list.
        
        Returns:
            Dict mapping module names to their dependencies
        """
        return {
            name: list(module.depends_on)
            for name, module in self.resolved_modules.items()
        }
