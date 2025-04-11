"""
Import Path Resolution Module.

This module resolves Python import statements to actual file paths in the repository.
It handles both absolute and relative imports.
"""

import os
import sys
import logging
from typing import Dict, List, Set, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class ImportPathResolver:
    """Resolves Python import paths to actual files in the repository."""
    
    def __init__(self, root_dir: str, python_ext: str = '.py'):
        """
        Initialize the resolver with a root directory.
        
        Args:
            root_dir: The root directory of the Python project
            python_ext: The file extension for Python files (default: '.py')
        """
        self.root_dir = os.path.abspath(root_dir)
        self.python_ext = python_ext
        self.sys_path = list(sys.path)
        
        # Add the root directory to the front of the path resolution list
        if self.root_dir not in self.sys_path:
            self.sys_path.insert(0, self.root_dir)
        
        # Cache for resolved paths
        self._path_cache: Dict[str, str] = {}
    
    def resolve_import(self, import_name: str, source_file: str = None, level: int = 0) -> Optional[str]:
        """
        Resolves an import to an actual file path.
        
        Args:
            import_name: The import name to resolve (e.g., 'package.module')
            source_file: The file containing the import (for relative imports)
            level: The level of relative import (0 for absolute, >= 1 for relative)
            
        Returns:
            The resolved file path, or None if it cannot be resolved
        """
        # Generate a cache key to avoid redundant resolution
        cache_key = f"{import_name}:{source_file}:{level}"
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]
        
        try:
            resolved_path = None
            
            if level > 0:
                # Handle relative imports
                if not source_file:
                    logger.warning(f"Cannot resolve relative import {import_name} without source file")
                    return None
                
                # Get the directory of the source file
                source_dir = os.path.dirname(os.path.abspath(source_file))
                
                # Go up 'level' directories
                for _ in range(level - 1):
                    source_dir = os.path.dirname(source_dir)
                
                # Calculate the relative import path
                if import_name:
                    module_path = os.path.join(source_dir, *import_name.split('.'))
                else:
                    # For "from . import x" cases
                    module_path = source_dir
                
                resolved_path = self._find_module_path(module_path)
            else:
                # Handle absolute imports, search in sys.path order
                for path in self.sys_path:
                    module_path = os.path.join(path, *import_name.split('.'))
                    result = self._find_module_path(module_path)
                    if result:
                        resolved_path = result
                        break
            
            # Cache the result
            self._path_cache[cache_key] = resolved_path
            return resolved_path
        
        except Exception as e:
            logger.error(f"Error resolving import {import_name}: {str(e)}")
            return None
    
    def _find_module_path(self, module_path: str) -> Optional[str]:
        """
        Find the actual file path for a module.
        
        This handles both direct file matches and __init__.py files in packages.
        
        Args:
            module_path: The filesystem path to check
            
        Returns:
            The resolved file path, or None if not found
        """
        # Check for direct .py file
        py_path = f"{module_path}{self.python_ext}"
        if os.path.isfile(py_path):
            return py_path
        
        # Check for package (__init__.py)
        init_path = os.path.join(module_path, f"__init__{self.python_ext}")
        if os.path.isfile(init_path):
            return init_path
        
        # Last resort: check for .pyd, .so, .pyd extensions for binary modules
        for ext in ['.pyd', '.so', '.pyc']:
            bin_path = f"{module_path}{ext}"
            if os.path.isfile(bin_path):
                return bin_path
        
        return None
    
    def resolve_imports_in_file(self, file_path: str, imports: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """
        Resolve all imports found in a file.
        
        Args:
            file_path: The path to the file containing the imports
            imports: List of import dictionaries from the import_parser module
            
        Returns:
            Dictionary mapping import specifiers to resolved file paths
        """
        result = {}
        
        for imp in imports:
            if imp['type'] == 'import':
                module_name = imp['module']
                resolved_path = self.resolve_import(module_name, file_path, 0)
                result[module_name] = resolved_path
                
            elif imp['type'] == 'from':
                module_name = imp['module'] or ''  # Handle 'from . import x' case
                level = imp['level']
                resolved_path = self.resolve_import(module_name, file_path, level)
                
                if module_name:
                    import_key = f"{'.' * level}{module_name}"
                else:
                    import_key = '.' * level
                    
                result[import_key] = resolved_path
        
        return result


def build_dependency_mapping(
    file_paths: List[str], 
    imports_by_file: Dict[str, List[Dict[str, Any]]],
    root_dir: str
) -> Dict[str, Dict[str, Any]]:
    """
    Build a mapping of files to their dependencies.
    
    Args:
        file_paths: List of Python file paths
        imports_by_file: Dictionary mapping file paths to their imports
        root_dir: Root directory of the project
        
    Returns:
        Dictionary mapping file paths to their resolved dependencies
    """
    resolver = ImportPathResolver(root_dir)
    result = {}
    
    for file_path in file_paths:
        if file_path in imports_by_file and imports_by_file[file_path]:
            imports = imports_by_file[file_path]
            resolved_imports = resolver.resolve_imports_in_file(file_path, imports)
            
            # Store with additional metadata
            result[file_path] = {
                'dependencies': resolved_imports,
                'import_details': imports
            }
    
    return result 